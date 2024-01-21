import json
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from httpx import Auth
from .models import Product,OrderDetail
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from .forms import ProductForm,UserRegistrationForm
from django.contrib.auth import authenticate,logout 
from django.contrib import messages 
from django.db.models import Sum
import datetime
# Create your views here.
def index(request):
    product=Product.objects.all()
    return render(request,"myapp/index.html",{"product":product})

def detail(request,id):
    product=Product.objects.get(id=id)
    stripe_publishable_key=settings.STRIPE_PUBLISHABLE_KEY
    return render(request,"myapp/detail.html",{"product":product,"stripe_publishable_key":stripe_publishable_key})
 
@csrf_exempt
def create_checkout_session(request,id):
    request_data=json.loads(request.body)
    product=Product.objects.get(id=id)
    stripe.api_key=settings.STRIPE_SECRET_KEY
    checkout_session=stripe.checkout.Session.create(
        customer_email=request_data['email'],
        payment_method_types=['card'],
        line_items=[
            {
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        'name':product.name,
                    },
                    'unit_amount':int(product.price*100)
                },
                'quantity':1
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success'))+
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('failed')),
    )
    order=OrderDetail()
    order.customer_email=request_data['email']
    order.product=product
    try:
        order.stripe_payment_intent = checkout_session['payment_intent']
    except KeyError:
        order.stripe_payment_intent = None
    order.amount=int(product.price)
    order.save()
    return JsonResponse({'sessionId':checkout_session.id})

def payment_success_view(request):
    session_id=request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key=settings.STRIPE_SECRET_KEY
    session=stripe.checkout.Session.retrieve(session_id)
    order=get_object_or_404(OrderDetail,stripe_payment_intent=session.payment_intent)
    order.has_paid=True
    #updating sales stats for a product
    product=Product.objects.get(id=order.product.id)
    product.total_sales_amount+=product.price
    product.total_sales+=1
    product.save()
    order.save()
    return render(request,'myapp/payment_success.html',{'order':order})
    
def payment_failed_view(request):
    return render(request,'myapp/failed.html')

def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST,request.FILES)
        if product_form.is_valid():
            new_product=product_form.save(commit=False)
            new_product.seller=request.user
            new_product.save()
            return redirect('index')
    else:
        product_form = ProductForm()
    return render(request, 'myapp/create_product.html', {'product_form': product_form})

def product_edit(request,id):
    product=Product.objects.get(id=id)
    if product.seller!=request.user:
        return redirect('invalid')
    product_form=ProductForm(request.POST or None,request.FILES or None,instance=product)
    if request.method=='POST':
        if product_form.is_valid():
            product_form.save()
            return redirect('index')
    return render(request,'myapp/product_edit.html',{'product_form':product_form,'product':product})

def product_delete(request,id):
    product=Product.objects.get(id=id)
    if product.seller!=request.user:
        return redirect('invalid')
    if request.method=='POST':
        product.delete()
        return redirect('index')
    return render(request,'myapp/delete.html',{"product":product})

def dashboard(request):
    products=Product.objects.filter(seller=request.user)
    return render(request,'myapp/dashboard.html',{'products':products})

def register(request):
    if request.method=='POST':
        user_form=UserRegistrationForm(request.POST)
        new_user=user_form.save(commit=False)
        new_user.set_password(user_form.cleaned_data['password'])
        new_user.save()
        return redirect('index')
    user_form=UserRegistrationForm()
    return render(request,'myapp/register.html',{'user_form':user_form})
 
def logout_view(request):
    logout(request)
    messages.success(request,("You Have been logged out!"))
    return redirect('index')

def invalid(request):
    return render(request,'myapp/invalid.html')

def my_purchases(request):
    #orders=OrderDetail.objects.filter(customer_email=request.user.email)
    orders=OrderDetail.objects.all()
    return render(request,'myapp/purchases.html',{'orders':orders})

def sales(request):
    orders=OrderDetail.objects.filter(product__seller=request.user)
    total_sales=orders.aggregate(Sum('amount'))
    #365 day sales sum
    last_year=datetime.date.today()-datetime.timedelta(days=365)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_year)
    yearly_sales=data.aggregate(Sum('amount'))
    
    #30 days sales sum
    last_month=datetime.date.today()-datetime.timedelta(days=30)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_month)
    monthly_sales=data.aggregate(Sum('amount'))
    
    last_week=datetime.date.today()-datetime.timedelta(days=7)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_week)
    weekly_sales=data.aggregate(Sum('amount'))
    
    #everyday sum for the past 30 days
    daily_sales_sum=OrderDetail.objects.filter(product__seller=request.user).values('created_on__date').order_by('created_on__date').annotate(sum=Sum('amount'))
    
    product_sales_sum=OrderDetail.objects.filter(product__seller=request.user).values('product__name').order_by('product__name').annotate(sum=Sum('amount'))
    print(product_sales_sum)
    return render(request,'myapp/sales.html',{"total_sales":total_sales,'yearly_sales':yearly_sales,'monthly_sales':monthly_sales,'weekly_sales':weekly_sales,'daily_sales_sum':daily_sales_sum,'product_sales_sum':product_sales_sum})