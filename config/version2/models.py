from django.db import models
import uuid

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.BinaryField()
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    downloaded = models.BooleanField(default=False)
    option_once = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)