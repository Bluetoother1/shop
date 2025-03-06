from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from shop.models import Product
from .stripe_utils import create_payment_intent
from bonussystem.models import UserProfile, BonusTransaction


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'cart/cart.html', {'cart': cart, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')


@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    total_amount = cart.total_price()

    # Проверяем, хочет ли пользователь списать бонусы
    use_bonus = request.POST.get('use_bonus', False)
    bonus_points_used = 0

    if use_bonus:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            # Максимальное количество бонусов, которое можно списать
            max_bonus = min(user_profile.bonus_points, total_amount-1)
            if max_bonus > 0:
                bonus_points_used = max_bonus
                total_amount -= bonus_points_used  # Уменьшаем сумму к оплате
        except UserProfile.DoesNotExist:
            pass  # Если профиль не найден, пропускаем списание бонусов

    # Создаем заказ
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount / 100,  # Переводим в рубли
        status='pending',
        bonus_points_used=bonus_points_used
    )

    # Создаем  Stripe с уменьшенной суммой
    intent = create_payment_intent(total_amount)
    if intent:
        order.stripe_payment_intent = intent['id']
        order.save()

        return render(request, 'cart/payment.html', {
            'client_secret': intent['client_secret'],
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'order': order
        })
    else:
        return render(request, 'cart/error.html', {'message': 'Ошибка при создании платежа'})


@login_required
def payment_success(request):
    # Получаем заказ
    order_id = request.GET.get('order_id')
    if not order_id:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Проверяем, был ли заказ уже обработан
    if order.status == 'paid':
        return redirect('home')

    # Обновляем статус заказа
    order.status = 'paid'
    order.save()

    # Списание бонусов
    if order.bonus_points_used > 0:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.deduct_bonus_points(order.bonus_points_used)

            # Логируем списание бонусов
            BonusTransaction.objects.create(
                user=request.user,
                amount=-order.bonus_points_used,
                description=f"Списание бонусов для заказа #{order.id}"
            )
        except UserProfile.DoesNotExist:
            pass  # Если профиль не найден, пропускаем списание бонусов

    # Начисляем бонусы за заказ
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # 1 балл за каждые 10 рублей (без учета списанных бонусов)
        bonus_points = int((order.total_amount) * 10)
        user_profile.add_bonus_points(bonus_points)

        # Логируем начисление бонусов
        BonusTransaction.objects.create(
            user=request.user,
            amount=bonus_points,
            description=f"Начисление бонусов за заказ #{order.id}"
        )
    except UserProfile.DoesNotExist:
        bonus_points = 0

    # Создаем копию для каждого товара в корзине
    cart = Cart.objects.get(user=request.user)
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )

    # Очищаем корзину
    cart.items.all().delete()

    return render(request, 'cart/success.html', {
        'order': order,
        'bonus_points': bonus_points
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/order_history.html', {'orders': orders})


@login_required
def repeat_order(request, order_id):
    # Получаем заказ из истории
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Получаем или создаем корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Копируем товары из заказа в корзину
    for order_item in order.items.all():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=order_item.product,
            defaults={'quantity': order_item.quantity}
        )
        if not created:
            cart_item.quantity += order_item.quantity
            cart_item.save()

    # Перенаправляем пользователя в корзину
    return redirect('view_cart')
