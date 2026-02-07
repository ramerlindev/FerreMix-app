from flask import Blueprint, render_template, request
from models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        categories = Category.get_all()
        products = Product.get_all(limit=20)
        return render_template('index.html', products=products, categories=categories, title="Inicio")
    except Exception as e:
        # In production, log this. For now, showing it helps debug.
        return f"<h1>Error de Conexión a Supabase API</h1><p>{str(e)}</p>", 500

@main_bp.route('/offers')
def offers():
    categories = Category.get_all()
    
    # Filters
    filters = {
        'is_offer': True,
        'category_id': request.args.get('category'),
        'min_price': request.args.get('min_price'),
        'max_price': request.args.get('max_price'),
        'search': request.args.get('search')
    }
    
    # Clean filters (remove None or empty strings)
    filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    
    products = Product.filter(filters)
    return render_template('index.html', products=products, categories=categories, title="Ofertas", show_filters=True)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.get(id)
    if not product:
        return render_template('404.html'), 404
    return render_template('product_detail.html', product=product)
