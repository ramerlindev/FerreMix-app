from flask import Blueprint, render_template, request
from models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        categories = Category.query.all()
        # Pagination simple or limit could be added here
        products = Product.query.limit(20).all()
        return render_template('index.html', products=products, categories=categories, title="Inicio")
    except Exception as e:
        return f"<h1>Error de Base de Datos</h1><p>{str(e)}</p>", 500

@main_bp.route('/offers')
def offers():
    categories = Category.query.all()
    
    # Base query for offers
    query = Product.query.filter_by(is_offer=True)
    
    # Filters
    category_id = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    search = request.args.get('search')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
        
    products = query.all()
    return render_template('index.html', products=products, categories=categories, title="Ofertas", show_filters=True)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)
