# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# Create your models here.


class Symbols(models.Model):
    symbol = models.CharField(primary_key=True, max_length=32)
    company = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'symbols'

    def __str__(self):
        return self.symbol


class StockData(models.Model):
    issuer_code = models.ForeignKey('Symbols', models.DO_NOTHING, db_column='issuer_code', blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    last_trade_price = models.FloatField(blank=True, null=True)
    max_price = models.FloatField(blank=True, null=True)
    min_price = models.FloatField(blank=True, null=True)
    avg_price = models.FloatField(blank=True, null=True)
    percent_change = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    turnover_best = models.FloatField(blank=True, null=True)
    total_turnover = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stock_data'