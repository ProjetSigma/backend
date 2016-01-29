from django.test import TestCase

from django.core.exceptions import ValidationError

from sigma_core.models.validator import get_validator_by_name, are_validator_fields_valid, is_validator_input_valid
from sigma_core.models.validator import Validator

class ValidatorTests(TestCase):
    @classmethod
    def setUp(self):
        pass
    def test_notfound_get_validator_by_name(self):
        self.assertEqual(get_validator_by_name('notfound-validator'), None)
    def test_base_get_validator_by_name(self):
        self.assertNotEqual(get_validator_by_name(Validator.VALIDATOR_NONE), None)

class TextValidatorTests(TestCase):
    @classmethod
    def setUp(self):
        pass
    def test_get_validator_by_name(self):
        self.assertNotEqual(get_validator_by_name(Validator.VALIDATOR_TEXT), None)
    def test_regex1(self):
        fields = {'regex': "\s*(?P<header>[^:]+)\s*:(?P<value>.*?)\s*$", 'message': 'Err msg' }
        self.assertTrue(are_validator_fields_valid(Validator.VALIDATOR_TEXT, fields))
    def test_regex2(self):
        # The following pattern excludes filenames that end in either bat or exe:
        # https://docs.python.org/3/howto/regex.html
        fields = {'regex': ".*[.](?!bat$|exe$).*$", 'message': 'Err msg' }
        self.assertTrue(are_validator_fields_valid(Validator.VALIDATOR_TEXT, fields))
        self.assertTrue(is_validator_input_valid(Validator.VALIDATOR_TEXT, fields, 'file.png'))
        self.assertFalse(is_validator_input_valid(Validator.VALIDATOR_TEXT, fields, 'file.exe'))
    def test_evil_regex(self):
        fields = {'regex': "^(([a-z])+.)+[A-Z]([a-z])+$", 'message': 'Err msg' }
        value = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!'
        self.assertTrue(are_validator_fields_valid(Validator.VALIDATOR_TEXT, fields))
        self.assertFalse(is_validator_input_valid(Validator.VALIDATOR_TEXT, fields, value))
