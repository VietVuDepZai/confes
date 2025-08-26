# documents/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction as db_transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from .models import Document, Rating, Transaction, PurchaseRecord
from .serializers import DocumentSerializer, RatingSerializer, TransactionSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # when user uploads document: set owner and +1 xu, create transaction
        with db_transaction.atomic():
            doc = serializer.save(owner=self.request.user)
            u = self.request.user
            u.xu += 1
            u.save()
            Transaction.objects.create(user=u, document=doc, type='upload', amount=1)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request, pk=None):
        doc = self.get_object()
        user = request.user
        if doc.owner == user:
            return Response({"detail":"Bạn không thể mua tài liệu của chính mình."}, status=status.HTTP_400_BAD_REQUEST)

        # If already purchased, allow download without charging
        already = PurchaseRecord.objects.filter(user=user, document=doc).exists()
        if already:
            # serve file
            try:
                return FileResponse(open(doc.file.path,'rb'), as_attachment=True, filename=doc.file.name.split('/')[-1])
            except Exception:
                raise Http404

        if user.xu < doc.cost:
            return Response({"detail":"Không đủ xu."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            user.xu -= doc.cost
            user.save()
            Transaction.objects.create(user=user, document=doc, type='purchase', amount=-doc.cost)
            PurchaseRecord.objects.create(user=user, document=doc)
        try:
            return FileResponse(open(doc.file.path,'rb'), as_attachment=True, filename=doc.file.name.split('/')[-1])
        except Exception:
            raise Http404

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        doc = self.get_object()
        user = request.user
        try:
            stars = int(request.data.get('stars', 0))
        except (TypeError, ValueError):
            return Response({"detail":"stars must be integer 1..5"}, status=status.HTTP_400_BAD_REQUEST)
        if stars < 1 or stars > 5:
            return Response({"detail":"stars must be 1..5"}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            rating, created = Rating.objects.update_or_create(user=user, document=doc, defaults={'stars': stars})
            agg = doc.ratings.aggregate(total=Sum('stars'), cnt=Count('id'))
            total = agg['total'] or 0
            cnt = agg['cnt'] or 0
            doc.rating_avg = (total / cnt) if cnt else 0.0
            doc.rating_count = cnt
            # basic rule: if rating_avg > 4 and rating_count >=5 => ensure cost >= 2
            if doc.rating_avg > 4.0 and doc.rating_count >= 5:
                doc.cost = max(doc.cost, 2)
            doc.save()
        return Response(RatingSerializer(rating).data)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-timestamp')
