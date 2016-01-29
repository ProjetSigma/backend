from django.db import models

from sigma_core.models.user import User
from sigma_core.models.validator import Validator
from jsonfield import JSONField

class CustomField(models.Model):
    class Meta:
        abstract = True

    NAME_MAX_LENGTH                 = 255
    FIELD_VALUE_MAX_LENGTH          = 255

    # Custom field displayed name
    name                = models.CharField(max_length=NAME_MAX_LENGTH)
    # Validator type for client input validation
    validator           = models.ForeignKey(Validator, related_name='+')
    # Serialized JSON array (fieldName => fieldValue)
    validator_values    = JSONField()

    def __str__(self):
        return "CustomField \"%s\" (validator \"%s\" with values=\"%s\")" % (self.name, self.validator.__str__(), self.validator_values)
