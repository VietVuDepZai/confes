from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from documents.models import Document
from documents.forms import DocumentForm
from django.contrib.auth.decorators import login_required
from documents.models import  Document, PurchaseRecord, Transaction
from users.forms import CustomUserCreationForm, LoginForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_or_email = form.cleaned_data.get('user_or_email')
            password = form.cleaned_data.get('password')
            
            # Kiểm tra nếu input là email thì tìm username
            if '@' in user_or_email:  # đơn giản, có thể check regex email
                try:
                    user_obj = User.objects.get(email=user_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = None
            else:
                username = user_or_email
            
            user = authenticate(username=username, password=password) if username else None
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Chào {user.username}, bạn đã đăng nhập thành công!")
                return redirect('home')
            else:
                messages.error(request, "Sai username/email hoặc mật khẩu.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công! Bạn đã được đăng nhập.")
            return redirect('home')
        else:
            messages.error(request, "Có lỗi xảy ra. Vui lòng kiểm tra lại.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})
@login_required(login_url='/login/')  # hoặc reverse('login')
def home(request):
    documents = Document.objects.all().select_related('owner')
    purchased_ids = PurchaseRecord.objects.filter(user=request.user).values_list('document_id', flat=True)
    return render(request, 'home.html', {
        'documents': documents,
        'purchased_ids': purchased_ids
    })
def user_logout(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất thành công!")
    return redirect('login')  # ho


@login_required
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()

            # Cộng 1 xu cho user sau khi upload
            request.user.coins += 1
            request.user.save()

            # Thông báo thành công
            messages.success(request, 'Tài liệu đã được thêm thành công! Bạn đã nhận +1 xu.')
            return redirect('home')
    else:
        form = DocumentForm()

    return render(request, 'documents/add_document.html', {'form': form})

@login_required
def purchase_document(request, document_id):
    doc = get_object_or_404(Document, id=document_id)

    if doc.owner == request.user:
        messages.error(request, "Bạn không thể mua tài liệu của chính mình.")
        return redirect('home')

    # Nếu đã mua rồi thì cho tải xuống
    if PurchaseRecord.objects.filter(user=request.user, document=doc).exists():
        messages.info(request, "Bạn đã mua tài liệu này trước đó. Có thể tải xuống.")
        return redirect(doc.file.url)

    if request.user.coins < doc.cost:
        messages.error(request, "Bạn không đủ xu để mua tài liệu này.")
        return redirect('home')

    # Tiến hành mua
    request.user.coins -= doc.cost
    request.user.save()

    PurchaseRecord.objects.create(user=request.user, document=doc)
    Transaction.objects.create(user=request.user, document=doc, type='purchase', amount=-doc.cost)

    messages.success(request, f"Mua tài liệu '{doc.title}' thành công!")
    return redirect('home')

@login_required
def edit_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, owner=request.user)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Tài liệu đã được cập nhật thành công!")
            return redirect('home')
        else:
            messages.error(request, "Có lỗi xảy ra. Vui lòng thử lại.")
    else:
        form = DocumentForm(instance=document)

    return render(request, 'documents/edit_document.html', {'form': form, 'document': document})


@login_required
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, owner=request.user)

    if request.method == 'POST':
        document.delete()
        messages.success(request, "Tài liệu đã được xóa thành công!")
        return redirect('home')

    return render(request, 'documents/confirm_delete.html', {'document': document})