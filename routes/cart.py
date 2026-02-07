from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Product, Cart, Order, OrderShipping, Payment

cart_bp = Blueprint("cart", __name__)


def _build_cart_summary(user_id=None):
    if not user_id:
        return {"count": 0, "subtotal": 0, "items": []}

    cart = Cart.get_user_cart(user_id)
    items = []
    subtotal = 0

    if cart and cart["items"]:
        for item in cart["items"]:
            line_total = item["product"]["price"] * item["quantity"]
            subtotal += line_total
            items.append(
                {
                    "id": item["id"],
                    "product_id": item["product"]["id"],
                    "name": item["product"]["name"],
                    "price": float(item["product"]["price"]),
                    "quantity": item["quantity"],
                    "image_url": item["product"].get("image_url"),
                    "line_total": float(line_total),
                }
            )

    count = sum(item["quantity"] for item in items) if items else 0
    return {"count": count, "subtotal": float(subtotal), "items": items}


@cart_bp.route("/summary")
def cart_summary():
    if not current_user.is_authenticated:
        return jsonify(_build_cart_summary())

    return jsonify(_build_cart_summary(current_user.id))


@cart_bp.route("/")
@login_required
def view_cart():
    cart = Cart.get_user_cart(current_user.id)
    total = (
        sum(item["product"]["price"] * item["quantity"] for item in cart["items"])
        if cart and cart["items"]
        else 0
    )
    return render_template("cart.html", cart=cart, total=total)


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.get(product_id)
    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("main.index"))

    quantity = int(request.form.get("quantity", 1))

    if product["stock"] < quantity:
        flash("No hay suficiente stock.", "warning")
        return redirect(url_for("main.product_detail", id=product_id))

    cart = Cart.get_user_cart(current_user.id)
    Cart.add_item(cart["id"], product_id, quantity)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(_build_cart_summary(current_user.id))

    flash("Producto agregado al carrito.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update_item(item_id):
    quantity = int(request.form.get("quantity"))
    if quantity > 0:
        Cart.update_item_quantity(item_id, quantity)
        flash("Carrito actualizado.", "success")
    else:
        Cart.remove_item(item_id)
        flash("Ítem eliminado.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_item(item_id):
    Cart.remove_item(item_id)
    flash("Producto eliminado del carrito.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = Cart.get_user_cart(current_user.id)
    if not cart or not cart["items"]:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("main.index"))

    total = sum(item["product"]["price"] * item["quantity"] for item in cart["items"])

    if request.method == "POST":
        shipping_data = {
            "full_name": request.form.get("full_name"),
            "address": request.form.get("address"),
            "city": request.form.get("city"),
            "phone": request.form.get("phone"),
            "notes": request.form.get("notes"),
        }
        payment_method = request.form.get("payment_method")
        transaction_ref = request.form.get("transaction_ref")

        if not all(
            [
                shipping_data["full_name"],
                shipping_data["address"],
                shipping_data["city"],
                shipping_data["phone"],
                payment_method,
            ]
        ):
            flash("Completa los datos de envío y pago.", "warning")
            return redirect(url_for("cart.checkout"))

        # Create Order
        order = Order.create(current_user.id, total, cart["items"])

        # Save shipping & payment (simulado)
        OrderShipping.create(order["id"], shipping_data)
        Payment.create(
            order["id"],
            total,
            payment_method,
            status="paid",
            transaction_ref=transaction_ref,
        )

        # Clear Cart
        Cart.clear(cart["id"])

        flash("¡Pedido realizado con éxito!", "success")
        return redirect(url_for("orders.my_orders"))

    return render_template("checkout.html", cart=cart, total=total)
