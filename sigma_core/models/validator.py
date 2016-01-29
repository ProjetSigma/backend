import timeout_decorator

from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from jsonfield import JSONField

import re # regex

from django.core.validators import validate_email


def get_validator_by_name(name):
    """
    For given validator name, returns associated functions array:
    validator = { validate_fields: vf, validate_input: vi }
    Where:
        - vf(fields)
            Raises a ValidationError if given fields are not valid for this validator
        - vi(fields, user_input)
            Throws a ValidationError if given input is not valid for this validator

    Returns None if there is no validator matching that name.
    """

    # Validators functions
    def text_validate_fields(fields):
        # TODO: Is it safe to call re.compile with user input ? Possible infinite loops ... ?
        try:
            re.compile(fields['regex'])
        except re.error:
            raise ValidationError(fields['message'] + " (invalid Regex syntax)")

    # Protection against Evil Regex. Only 50ms to evaluate regex - should be enough.
    @timeout_decorator.timeout(0.05, use_signals=False)
    def regex_check_timeout(regex, error_message, input):
        try:
            RegexValidator(regex, error_message)(input)
        except re.error: # Should not happen ...
            raise ValidationError("Invalid validator for this field.")

    def text_validate_input(fields, input):
        if (fields['regex']):
            try:
                regex_check_timeout(fields['regex'], fields['message'], input)
            except timeout_decorator.TimeoutError:
                raise ValidationError(fields['message'])

    # Validators map
    validators_map = {
        Validator.VALIDATOR_NONE: {
            'validate_fields':    lambda f: True,
            'validate_input':     lambda f,i: True,
        },
        Validator.VALIDATOR_TEXT: {
            'validate_fields':    text_validate_fields,
            'validate_input':     text_validate_input
        },
        # TODO: Register validators here
    }

    # Find matching validator
    try:
        return validators_map[name]
    except KeyError:
        return None


def validate_validator_fields(validator, fields):
    v = get_validator_by_name(validator)
    v['validate_fields'](fields)

def are_validator_fields_valid(validator, fields):
    try:
        validate_validator_fields(validator, fields)
        return True
    except ValidationError:
        return False

def validate_validator_input(validator, fields, value):
    v = get_validator_by_name(validator)
    v['validate_input'](fields, value)

def is_validator_input_valid(validator, fields, value):
    try:
        validate_validator_input(validator, fields, value)
        return True
    except ValidationError:
        return False

class Validator(models.Model):
    class Meta:
        pass

    VALIDATOR_TEXT = 'text'
    VALIDATOR_NONE = 'none'
    VALIDATOR_HTML_CHOICES = (
        (VALIDATOR_TEXT, 'Text'),
        (VALIDATOR_NONE, 'None')
    )

    # Displayed validator name
    display_name    = models.CharField(max_length=255)
    # HTML name (<input type="html_name">)
    html_name       = models.CharField(max_length=255,
                            choices=VALIDATOR_HTML_CHOICES,
                            default=VALIDATOR_NONE,
                            primary_key=True)
    # Serialized JSON array (fieldName => fieldDescription)
    values          = JSONField()

    def __str__(self):
        return "Validator \"%s\" (\"%s\" with values=\"%s\")" % (self.display_name, self.html_name, self.values)

    def validate_fields(self, fields):
        return validate_validator_fields(self.html_name, fields)

    def validate_input(self, fields, client_input):
        return validate_validator_input(self.html_name, fields, client_input)
