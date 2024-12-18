from django.contrib import admin
from .models import Symbols, StockData

# Register your models here.


class SymbolsAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company')


class StockDataAdmin(admin.ModelAdmin):
    pass

admin.site.register(Symbols, SymbolsAdmin)
admin.site.register(StockData, StockDataAdmin)
