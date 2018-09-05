from django.db import models


class MockPerson(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class MockPet(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(
        MockPerson, related_name="pets", on_delete=models.CASCADE, db_constraint=False
    )


class MockPersonLocation(models.Model):
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    owner = models.ForeignKey(
        MockPerson, related_name="owned_locations", on_delete=models.CASCADE, db_constraint=False
    )
