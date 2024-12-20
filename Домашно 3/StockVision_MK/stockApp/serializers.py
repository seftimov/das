from rest_framework import serializers
from .models import StockData


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ['date', 'last_trade_price', 'max_price', 'min_price', 'avg_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'date': representation['date'],
            'open': representation['avg_price'],
            'high': representation['max_price'],
            'low': representation['min_price'],
            'close': representation['last_trade_price']
        }
