from flask import Blueprint, render_template, request, url_for
from models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        categories = Category.get_all()
        
        # Build sections for Homepage
        category_sections = []
        
        # 1. Offers Section (Fake 'Offers' category for display)
        offers_products = Product.filter({'is_offer': True}, limit=4)
        if offers_products:
            category_sections.append({
                'title': 'Ofertas Destacadas',
                'description': 'Aprovecha nuestros descuentazos',
                'link': url_for('main.offers'),
                'products': offers_products
            })
            
        # 2. Per Category Sections (Limit to first 5 categories to avoid too many requests)
        for cat in categories[:5]:
            products = Product.filter({'category_id': cat['id']}, limit=4)
            if products:
                category_sections.append({
                    'title': cat['name'],
                    'id': cat['id'], # Helper for link construction if needed
                    'link': url_for('main.offers', category=cat['id']),
                    'products': products
                })

        # Fallback products if sections are empty or just for the bottom grid
        all_products = Product.get_all(limit=20)

        return render_template('index.html', category_sections=category_sections, categories=categories, products=all_products, title="Inicio")
    except Exception as e:
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
