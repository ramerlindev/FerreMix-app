from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import Product, Category, User, Order
from werkzeug.security import generate_password_hash

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Acceso no autorizado.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Counters might be inefficient via API if table is large.
    # Supabase allows 'count' in select with head=True for efficiency.
    # For now, fetching all is okay for small scale.
    try:
        products = Product.get_all()
        products_count = len(products) if products else 0

        # We don't have a get_all for users in the basic model yet, let's add simple count or fetch
        # For this demo, we might skip precise counts or implement specific methods if needed.
        # Assuming we can just count what we can fetch:

        categories = Category.get_all()
        categories_count = len(categories) if categories else 0

        orders = Order.get_all()
        orders_count = len(orders) if orders else 0

        users = User.get_all()
        users_count = len(users) if users else 0

        return render_template(
            "admin/dashboard.html",
            products_count=products_count,
            users_count=users_count,
            orders_count=orders_count,
            categories_count=categories_count,
        )
    except Exception as e:
        flash(f"Error cargando dashboard: {e}", "danger")
        return render_template(
            "admin/dashboard.html",
            products_count=0,
            users_count=0,
            orders_count=0,
            categories_count=0,
        )


# --- Products Management ---
@admin_bp.route("/products")
@login_required
@admin_required
def products_list():
    products = Product.get_all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/product/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_product():
    categories = Category.get_all()
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price")),
            "image_url": request.form.get("image_url"),
            "category_id": (
                int(request.form.get("category_id"))
                if request.form.get("category_id")
                else None
            ),
            "stock": int(request.form.get("stock")),
            "is_offer": "is_offer" in request.form,
        }
        Product.create(data)
        flash("Producto creado exitosamente.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template(
        "admin/product_form.html", categories=categories, action="Crear"
    )


@admin_bp.route("/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(id):
    product = Product.get(id)
    categories = Category.get_all()

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price")),
            "image_url": request.form.get("image_url"),
            "category_id": (
                int(request.form.get("category_id"))
                if request.form.get("category_id")
                else None
            ),
            "stock": int(request.form.get("stock")),
            "is_offer": "is_offer" in request.form,
        }
        Product.update(id, data)
        flash("Producto actualizado exitosamente.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template(
        "admin/product_form.html",
        product=product,
        categories=categories,
        action="Editar",
    )


@admin_bp.route("/product/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_product(id):
    Product.delete(id)
    flash("Producto eliminado.", "success")
    return redirect(url_for("admin.products_list"))


# --- Categories Management ---
@admin_bp.route("/categories")
@login_required
@admin_required
def categories_list():
    categories = Category.get_all()
    return render_template("admin/categories.html", categories=categories)


@admin_bp.route("/category/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name")
        slug = request.form.get("slug")
        Category.create(name, slug)
        flash("Categoría creada.", "success")
        return redirect(url_for("admin.categories_list"))
    return render_template("admin/category_form.html", action="Crear")


@admin_bp.route("/category/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_category(id):
    category = Category.get(id)
    if request.method == "POST":
        data = {"name": request.form.get("name"), "slug": request.form.get("slug")}
        Category.update(id, data)
        flash("Categoría actualizada.", "success")
        return redirect(url_for("admin.categories_list"))
    return render_template(
        "admin/category_form.html", category=category, action="Editar"
    )


@admin_bp.route("/category/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_category(id):
    Category.delete(id)
    flash("Categoría eliminada.", "success")
    return redirect(url_for("admin.categories_list"))


# --- Orders Management ---
@admin_bp.route("/orders")
@login_required
@admin_required
def orders_list():
    orders = Order.get_all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/order/<int:order_id>", methods=["GET", "POST"])
@login_required
@admin_required
def order_detail(order_id):
    order = Order.get(order_id)
    if request.method == "POST":
        status = request.form.get("status")
        Order.update_status(order_id, status)
        flash("Estado del pedido actualizado.", "success")
        return redirect(url_for("admin.order_detail", order_id=order_id))
    return render_template("admin/order_detail.html", order=order)


# --- Users (Limited) ---
@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    users = User.get_all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/user/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        is_admin = "is_admin" in request.form
        User.create(email, password, is_admin)
        flash("Usuario creado.", "success")
        return redirect(url_for("admin.users_list"))
    return render_template("admin/user_form.html")


@admin_bp.route("/user/edit/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.get(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.users_list"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        is_admin = "is_admin" in request.form

        data = {
            "email": email,
            "is_admin": is_admin,
        }
        if password:
            data["password_hash"] = generate_password_hash(password)

        User.update(user_id, data)
        flash("Usuario actualizado.", "success")
        return redirect(url_for("admin.users_list"))

    return render_template("admin/user_form.html", user=user)


@admin_bp.route("/user/delete/<user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash("No puedes eliminar tu propio usuario.", "danger")
        return redirect(url_for("admin.users_list"))

    User.delete(user_id)
    flash("Usuario eliminado.", "success")
    return redirect(url_for("admin.users_list"))
