import os
from flask import Flask
from config import Config
from extensions import login_manager
from models import User, Product

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    login_manager.init_app(app)

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register Blueprints
    from routes.main import main_bp
    from auth.routes import auth_bp
    from admin.routes import admin_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(orders_bp, url_prefix='/orders')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
