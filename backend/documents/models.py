# documents/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="Noah-kun")
    file = models.FileField(upload_to='documents/')
    owner = models.ForeignKey(User, related_name='documents', on_delete=models.CASCADE)
    cost = models.IntegerField(default=1)
    rating_avg = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, related_name='ratings', on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()  # 1..5
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','document')

    def __str__(self):
        return f"{self.user} -> {self.document} : {self.stars}"

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('upload','Upload'),
        ('purchase','Purchase'),
    )
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='upload')
    amount = models.IntegerField()   # positive for gain, negative for spend
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.type} {self.amount}"

class PurchaseRecord(models.Model):
    user = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, related_name='purchased_by', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','document')

    def __str__(self):
        return f"{self.user} bought {self.document}"
