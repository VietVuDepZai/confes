from rest_framework import serializers
from .models import Document, Rating, Transaction

class DocumentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    rating_avg = serializers.FloatField(read_only=True)

    class Meta:
        model = Document
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('document', 'stars')


class TransactionSerializer(serializers.ModelSerializer):
    document_title = serializers.ReadOnlyField(source='document.title')

    class Meta:
        model = Transaction
        fields = ('id', 'document_title', 'transaction_type', 'amount', 'timestamp')
