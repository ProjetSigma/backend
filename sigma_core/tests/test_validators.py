from django.test import TestCase

from django.core.exceptions import ValidationError

from sigma_core.models.validator import get_validator_by_name
from sigma_core.models.validator import Validator

def are_validator_fields_valid(validator, fields):
    try:
        v = get_validator_by_name(validator)
        return v['validate_fields'](fields)
    except ValidationError:
        return False

def is_validator_input_valid(validator, fields, value):
    try:
        v = get_validator_by_name(validator)
        v['validate_input'](fields, value)
        return True
    except ValidationError:
        return False

class ValidatorTests(TestCase):
    @classmethod
    def setUp(self):
        pass
    def test_none_get_validator_by_name(self):
        self.assertEqual(get_validator_by_name('none'), None)

class TextValidatorTests(TestCase):
    @classmethod
    def setUp(self):
        pass
    def test_get_validator_by_name(self):
        self.assertNotEqual(get_validator_by_name('text'), None)
    def test_regex1(self):
        fields = {'regex': "\s*(?P<header>[^:]+)\s*:(?P<value>.*?)\s*$", 'message': 'Err msg' }
        self.assertTrue(are_validator_fields_valid('text', fields))
    def test_regex2(self):
        # The following pattern excludes filenames that end in either bat or exe:
        # https://docs.python.org/3/howto/regex.html
        fields = {'regex': ".*[.](?!bat$|exe$).*$", 'message': 'Err msg' }
        self.assertTrue(are_validator_fields_valid('text', fields))
        self.assertTrue(is_validator_input_valid('text', fields, 'file.png'))
        self.assertFalse(is_validator_input_valid('text', fields, 'file.exe'))
