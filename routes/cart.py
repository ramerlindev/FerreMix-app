from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Product, Cart, Order

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
@login_required
def view_cart():
    cart = Cart.get_user_cart(current_user.id)
    total = sum(item['product']['price'] * item['quantity'] for item in cart['items']) if cart and cart['items'] else 0
    return render_template('cart.html', cart=cart, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.get(product_id)
    if not product:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('main.index'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if product['stock'] < quantity:
        flash('No hay suficiente stock.', 'warning')
        return redirect(url_for('main.product_detail', id=product_id))

    cart = Cart.get_user_cart(current_user.id)
    Cart.add_item(cart['id'], product_id, quantity)
    
    flash('Producto agregado al carrito.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    quantity = int(request.form.get('quantity'))
    if quantity > 0:
        Cart.update_item_quantity(item_id, quantity)
        flash('Carrito actualizado.', 'success')
    else:
        Cart.remove_item(item_id)
        flash('Ítem eliminado.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    Cart.remove_item(item_id)
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.get_user_cart(current_user.id)
    if not cart or not cart['items']:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('main.index'))
        
    total = sum(item['product']['price'] * item['quantity'] for item in cart['items'])
    
    if request.method == 'POST':
        # Create Order
        Order.create(current_user.id, total, cart['items'])
        
        # Clear Cart
        Cart.clear(cart['id'])
        
        flash('¡Pedido realizado con éxito!', 'success')
        return redirect(url_for('orders.my_orders'))
        
    return render_template('checkout.html', cart=cart, total=total)
