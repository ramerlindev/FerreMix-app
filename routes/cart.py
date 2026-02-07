from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Product, Cart, CartItem, Order, OrderItem
from extensions import db

cart_bp = Blueprint('cart', __name__)

def get_user_cart():
    # Helper to get or create cart for logged in user
    if not current_user.is_authenticated:
        return None
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart

@cart_bp.route('/')
@login_required
def view_cart():
    cart = get_user_cart()
    total = sum(item.product.price * item.quantity for item in cart.items) if cart else 0
    return render_template('cart.html', cart=cart, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = get_user_cart()
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} agregado al carrito.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        return redirect(url_for('main.index'))
        
    quantity = int(request.form.get('quantity'))
    if quantity > 0:
        item.quantity = quantity
        db.session.commit()
        flash('Carrito actualizado.', 'success')
    else:
        db.session.delete(item)
        db.session.commit()
        flash('Producto eliminado del carrito.', 'success')
        
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        return redirect(url_for('main.index'))
        
    db.session.delete(item)
    db.session.commit()
    flash('Producto eliminado.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_user_cart()
    if not cart or not cart.items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('main.index'))
        
    total = sum(item.product.price * item.quantity for item in cart.items)
    
    if request.method == 'POST':
        # Simulate Payment Process
        # Here you would integrate Stripe/PayPal
        
        # Create Order
        order = Order(user_id=current_user.id, total_amount=total, status='completed')
        db.session.add(order)
        db.session.commit() # Commit to get order ID
        
        # Move items to OrderItems
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                price_at_purchase=cart_item.product.price,
                quantity=cart_item.quantity
            )
            db.session.add(order_item)
            
        # Clear Cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        
        flash('¡Compra realizada con éxito!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('checkout.html', cart=cart, total=total)
