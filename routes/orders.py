from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import Order

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@login_required
def my_orders():
    orders = Order.get_by_user(current_user.id)
    return render_template('orders.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.get(order_id)
    
    if not order:
        abort(404)
        
    if order['user_id'] != current_user.id and not current_user.is_admin:
        abort(403)
        
    return render_template('order_detail.html', order=order)
