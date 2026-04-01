from django.shortcuts import render,redirect,get_object_or_404
from Backend.models import Product,Order
from django.contrib import messages


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image.url,
        }

    request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {
        'cart': cart,
        'total': total
    })

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        if action == 'increase':
            cart[product_id]['quantity'] += 1
        elif action == 'decrease':
            cart[product_id]['quantity'] -= 1
            if cart[product_id]['quantity'] <= 0:
                del cart[product_id]

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart')

import razorpay
from django.conf import settings

def checkout(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        if not cart:
            messages.warning(request, "Your cart is empty!")
            return redirect('checkout')

        order = Order.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            total_amount=total,
            is_paid=False
        )

        # DO NOT clear cart yet
        return redirect('payment', order_id=order.id)

    return render(request, 'checkout.html', {'total': total})

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    razorpay_order = client.order.create({
        "amount": int(order.total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return render(request, 'payment.html', {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': int(order.total_amount * 100),
        'razorpay_order_id': razorpay_order['id']
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')

    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        order = Order.objects.get(razorpay_order_id=order_id)
        order.is_paid = True
        order.razorpay_payment_id = payment_id
        order.save()

        # NOW clear cart
        request.session['cart'] = {}

        return HttpResponse("Payment Successful ✅")

    except:
        return HttpResponse("Payment Failed ❌")