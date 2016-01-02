from django.db import models

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
