from extensions import supabase, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime


class User(UserMixin):
    def __init__(self, id, email, password_hash, is_admin=False, created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at

    @staticmethod
    def get(user_id):
        try:
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                data = response.data[0]
                return User(
                    id=data["id"],
                    email=data["email"],
                    password_hash=data["password_hash"],
                    is_admin=data.get("is_admin", False),
                    created_at=data.get("created_at"),
                )
        except Exception as e:
            print(f"Error getting user: {e}")
        return None

    @staticmethod
    def get_by_email(email):
        try:
            response = supabase.table("users").select("*").eq("email", email).execute()
            if response.data:
                data = response.data[0]
                return User(
                    id=data["id"],
                    email=data["email"],
                    password_hash=data["password_hash"],
                    is_admin=data.get("is_admin", False),
                    created_at=data.get("created_at"),
                )
        except Exception as e:
            print(f"Error getting user by email: {e}")
        return None

    @staticmethod
    def create(email, password, is_admin=False):
        password_hash = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        data = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            response = supabase.table("users").insert(data).execute()
            if response.data:
                return User.get(user_id)
        except Exception as e:
            print(f"Error creating user: {e}")
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category:
    @staticmethod
    def get_all():
        response = supabase.table("categories").select("*").execute()
        return response.data

    @staticmethod
    def get(id):
        response = supabase.table("categories").select("*").eq("id", id).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def create(name, slug):
        response = (
            supabase.table("categories").insert({"name": name, "slug": slug}).execute()
        )
        return response.data[0] if response.data else None

    @staticmethod
    def update(id, data):
        response = supabase.table("categories").update(data).eq("id", id).execute()
        return response.data

    @staticmethod
    def delete(id):
        supabase.table("categories").delete().eq("id", id).execute()


class Product:
    @staticmethod
    def get_all(limit=None):
        query = supabase.table("products").select("*, categories(name)")
        if limit:
            query = query.limit(limit)
        response = query.execute()
        # Transform category nested object to flatten or keep consistent
        products = []
        for p in response.data:
            p["category"] = p["categories"] if "categories" in p else None
            products.append(p)
        return products

    @staticmethod
    def get(id):
        response = (
            supabase.table("products")
            .select("*, categories(name)")
            .eq("id", id)
            .execute()
        )
        if response.data:
            p = response.data[0]
            p["category"] = p["categories"] if "categories" in p else None
            return p
        return None

    @staticmethod
    def create(data):
        response = supabase.table("products").insert(data).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def update(id, data):
        response = supabase.table("products").update(data).eq("id", id).execute()
        return response.data

    @staticmethod
    def delete(id):
        supabase.table("products").delete().eq("id", id).execute()

    @staticmethod
    def filter(filters, limit=None):
        query = supabase.table("products").select("*, categories(name)")

        if "is_offer" in filters:
            query = query.eq("is_offer", filters["is_offer"])
        if "category_id" in filters and filters["category_id"]:
            query = query.eq("category_id", filters["category_id"])
        if "min_price" in filters and filters["min_price"]:
            query = query.gte("price", filters["min_price"])
        if "max_price" in filters and filters["max_price"]:
            query = query.lte("price", filters["max_price"])
        if "search" in filters and filters["search"]:
            query = query.ilike("name", f"%{filters['search']}%")

        if limit:
            query = query.limit(limit)

        response = query.execute()
        products = []
        for p in response.data:
            p["category"] = p["categories"] if "categories" in p else None
            products.append(p)
        return products


class Cart:
    @staticmethod
    def get_user_cart(user_id):
        # First check if cart exists
        response = supabase.table("carts").select("*").eq("user_id", user_id).execute()
        if not response.data:
            # Create cart
            response = supabase.table("carts").insert({"user_id": user_id}).execute()

        cart = response.data[0]
        # Get items
        items_response = (
            supabase.table("cart_items")
            .select("*, products(*)")
            .eq("cart_id", cart["id"])
            .execute()
        )

        cart["items"] = []
        for item in items_response.data:
            # Flatten product structure
            item["product"] = item["products"]
            cart["items"].append(item)

        return cart

    @staticmethod
    def add_item(cart_id, product_id, quantity):
        # Check if item exists in cart
        response = (
            supabase.table("cart_items")
            .select("*")
            .eq("cart_id", cart_id)
            .eq("product_id", product_id)
            .execute()
        )

        if response.data:
            # Update quantity
            new_qty = response.data[0]["quantity"] + int(quantity)
            supabase.table("cart_items").update({"quantity": new_qty}).eq(
                "id", response.data[0]["id"]
            ).execute()
        else:
            # Insert new item
            supabase.table("cart_items").insert(
                {"cart_id": cart_id, "product_id": product_id, "quantity": quantity}
            ).execute()

    @staticmethod
    def update_item_quantity(item_id, quantity):
        supabase.table("cart_items").update({"quantity": quantity}).eq(
            "id", item_id
        ).execute()

    @staticmethod
    def remove_item(item_id):
        supabase.table("cart_items").delete().eq("id", item_id).execute()

    @staticmethod
    def clear(cart_id):
        supabase.table("cart_items").delete().eq("cart_id", cart_id).execute()


class Order:
    @staticmethod
    def create(user_id, total_amount, items):
        # Create Order
        order_data = {
            "user_id": user_id,
            "total_amount": total_amount,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        order_res = supabase.table("orders").insert(order_data).execute()
        order = order_res.data[0]

        # Create Order Items
        order_items = []
        for item in items:
            order_items.append(
                {
                    "order_id": order["id"],
                    "product_id": item["product"]["id"],
                    "product_name": item["product"]["name"],
                    "quantity": item["quantity"],
                    "price_at_purchase": item["product"]["price"],
                }
            )

        if order_items:
            supabase.table("order_items").insert(order_items).execute()

        return order

    @staticmethod
    def get_by_user(user_id):
        response = (
            supabase.table("orders")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data

    @staticmethod
    def get_all():
        response = (
            supabase.table("orders")
            .select("*, users(email)")
            .order("created_at", desc=True)
            .execute()
        )
        orders = []
        for o in response.data:
            o["user"] = o["users"] if "users" in o else None
            orders.append(o)
        return orders

    @staticmethod
    def get(id):
        response = (
            supabase.table("orders").select("*, users(email)").eq("id", id).execute()
        )
        if not response.data:
            return None
        order = response.data[0]
        order["user"] = order["users"] if "users" in order else None

        # Get items
        items_res = (
            supabase.table("order_items")
            .select("*")
            .eq("order_id", order["id"])
            .execute()
        )
        order["items"] = items_res.data

        return order

    @staticmethod
    def update_status(id, status):
        supabase.table("orders").update({"status": status}).eq("id", id).execute()


class OrderShipping:
    @staticmethod
    def create(order_id, data):
        payload = {
            "order_id": order_id,
            "full_name": data.get("full_name"),
            "address": data.get("address"),
            "city": data.get("city"),
            "phone": data.get("phone"),
            "notes": data.get("notes"),
        }
        response = supabase.table("order_shipping").insert(payload).execute()
        return response.data[0] if response.data else None


class Payment:
    @staticmethod
    def create(order_id, amount, method, status="paid", transaction_ref=None):
        payload = {
            "order_id": order_id,
            "amount": amount,
            "method": method,
            "status": status,
            "transaction_ref": transaction_ref,
        }
        response = supabase.table("payments").insert(payload).execute()
        return response.data[0] if response.data else None
