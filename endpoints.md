# FerreMix API Endpoints

## Autenticación
- `GET /auth/login`: Formulario de login.
- `POST /auth/login`: Procesar login.
- `GET /auth/register`: Formulario de registro.
- `POST /auth/register`: Procesar registro.
- `GET /auth/logout`: Cerrar sesión.

## Público (Main)
- `GET /`: Página de inicio (Catálogo).
- `GET /offers`: Página de ofertas (con filtros).
- `GET /product/<id>`: Detalle de producto.

## Carrito de Compras
- `GET /cart/`: Ver carrito.
- `POST /cart/add/<id>`: Agregar producto al carrito.
- `POST /cart/update/<id>`: Actualizar cantidad de ítem.
- `POST /cart/remove/<id>`: Eliminar ítem del carrito.
- `GET /cart/checkout`: Página de pago.
- `POST /cart/checkout`: Procesar pago (crear orden).

## Usuarios (Órdenes)
- `GET /orders/`: Historial de órdenes del usuario.
- `GET /orders/<id>`: Detalle de una orden específica.

## Administración (Requiere is_admin=True)
- `GET /admin/`: Dashboard.
- `GET /admin/products`: Lista de productos.
- `GET /admin/product/new`: Formulario crear producto.
- `POST /admin/product/new`: Guardar nuevo producto.
- `GET /admin/product/edit/<id>`: Formulario editar producto.
- `POST /admin/product/edit/<id>`: Guardar cambios producto.
- `POST /admin/product/delete/<id>`: Eliminar producto.
- `GET /admin/users`: Lista de usuarios.
- `GET /admin/user/new`: Formulario crear usuario.
- `POST /admin/user/new`: Guardar nuevo usuario.
- `GET /admin/categories`: Lista de categorías.
- `GET /admin/category/new`: Formulario crear categoría.
- `POST /admin/category/new`: Guardar nueva categoría.
- `GET /admin/category/edit/<id>`: Formulario editar categoría.
- `POST /admin/category/edit/<id>`: Guardar cambios categoría.
- `POST /admin/category/delete/<id>`: Eliminar categoría.
- `GET /admin/orders`: Lista de todas las órdenes.
- `GET /admin/order/<id>`: Detalle de orden.
- `POST /admin/order/<id>`: Cambiar estado orden.
