from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import Product, Category, User, Order
from extensions import db

admin_bp = Blueprint('admin', __name__)

# Decorador personalizado para requerir admin
def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return login_required(wrapper)

@admin_bp.route('/')
@admin_required
def dashboard():
    products_count = Product.query.count()
    users_count = User.query.count()
    orders_count = Order.query.count()
    categories_count = Category.query.count()
    return render_template('admin/dashboard.html', products_count=products_count, users_count=users_count, orders_count=orders_count, categories_count=categories_count)

@admin_bp.route('/products')
@admin_required
def products_list():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/product/new', methods=['GET', 'POST'])
@admin_required
def create_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        category_id = request.form.get('category_id')
        stock = request.form.get('stock')
        is_offer = 'is_offer' in request.form
        
        product = Product(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            category_id=category_id,
            stock=stock,
            is_offer=is_offer
        )
        db.session.add(product)
        db.session.commit()
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('admin.products_list'))
        
    return render_template('admin/product_form.html', categories=categories, action='Crear')

@admin_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        product.image_url = request.form.get('image_url')
        product.category_id = request.form.get('category_id')
        product.stock = request.form.get('stock')
        product.is_offer = 'is_offer' in request.form
        
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('admin.products_list'))
        
    return render_template('admin/product_form.html', product=product, categories=categories, action='Editar')

@admin_bp.route('/product/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado.', 'success')
    return redirect(url_for('admin.products_list'))

@admin_bp.route('/users')
@admin_required
def users_list():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/new', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        if User.query.filter_by(email=email).first():
            flash('El email ya existe.', 'warning')
        else:
            user = User(email=email, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('admin.users_list'))
            
    return render_template('admin/user_form.html')

# Category Management
@admin_bp.route('/categories')
@admin_required
def categories_list():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def create_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        
        category = Category(name=name, slug=slug)
        db.session.add(category)
        db.session.commit()
        flash('Categoría creada.', 'success')
        return redirect(url_for('admin.categories_list'))
        
    return render_template('admin/category_form.html', action='Crear')

@admin_bp.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        db.session.commit()
        flash('Categoría actualizada.', 'success')
        return redirect(url_for('admin.categories_list'))
        
    return render_template('admin/category_form.html', category=category, action='Editar')

@admin_bp.route('/category/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada.', 'success')
    return redirect(url_for('admin.categories_list'))

@admin_bp.route('/orders')
@admin_required
def orders_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        status = request.form.get('status')
        if status:
            order.status = status
            db.session.commit()
            flash('Estado de la orden actualizado.', 'success')
            return redirect(url_for('admin.orders_list'))
            
    return render_template('admin/order_detail.html', order=order)
