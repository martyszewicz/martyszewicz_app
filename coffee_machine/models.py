from django.db import models


class Coffee(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()

    def __str__(self):
        return self.name


class Report(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()

    def save_info_about_transaction(self):
        self.save()

    def __str__(self):
        return self.name
