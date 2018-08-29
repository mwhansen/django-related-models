from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class MockPerson(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class MockPet(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(MockPerson, related_name="pets")


class MockPersonLocation(models.Model):
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    owner = models.ForeignKey(MockPerson, related_name="owned_locations")


class MockTaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.tag
