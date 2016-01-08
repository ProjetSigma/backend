import timeout_decorator

from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

import re # regex

from django.core.validators import validate_email

def get_validator_by_name(name):
    """
    For given validator name, returns associated functions array:
    validator = { validate_fields: vf, validate_input: vi }
    Where:
        - vf(fields)
            returns True iif the specified fields are valid - or returns False/raises exceptions
        - vi(fields, user_input)
            Throws a ValidationError if given input is not valid for this validator

    Returns None if there is no validator matching that name.
    """
    # Validators functions
    def text_validate_fields(fields):
        re.compile(fields['regex']) # TODO: Is it safe to call re.compile with user input ? Possible infinite loops ... ?
        fields['message']
        return True
    # Protection against Evil Regex. Only 50ms to evaluate regex - should be enough.
    @timeout_decorator.timeout(0.05, use_signals=False)
    def regex_check_timeout(regex, error_message, input):
        RegexValidator(regex, error_message)(input)
    def text_validate_input(fields, input):
        if (fields['regex']):
            try:
                regex_check_timeout(fields['regex'], fields['message'], input)
            except timeout_decorator.TimeoutError:
                raise ValidationError(fields['message'])

    # Validators map
    validators_map = {
        'text': {
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

class Validator(models.Model):
    class Meta:
        pass

    VALIDATOR_VALUES_DESCRIPTION_MAX_LENGTH     = 1024 # In serialized form

    # Displayed validator name
    display_name    = models.CharField(max_length=255)
    # HTML name (<input type="html_name">)
    html_name       = models.CharField(max_length=255)
    # Serialized JSON array (fieldName => fieldDescription)
    values          = models.CharField(max_length=VALIDATOR_VALUES_DESCRIPTION_MAX_LENGTH)

    def __str__(self):
        return "Validator \"%s\" (\"%s\" with values=\"%s\")" % (self.display_name, self.html_name, self.values)
