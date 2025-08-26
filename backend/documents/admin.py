# documents/admin.py
from django.contrib import admin
from .models import Document, Rating, Transaction, PurchaseRecord

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title','owner','cost','rating_avg','rating_count','created_at')
    search_fields = ('title','owner__username')

admin.site.register(Rating)
admin.site.register(Transaction)
admin.site.register(PurchaseRecord)
