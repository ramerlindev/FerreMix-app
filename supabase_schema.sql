-- Habilitar extensión UUID si es necesaria (generalmente Supabase ya la tiene)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Categorías
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Tabla de Productos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url TEXT, -- URL de la imagen (puede ser de Supabase Storage o externa)
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    is_offer BOOLEAN DEFAULT FALSE,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de Carritos (Persistente)
CREATE TABLE IF NOT EXISTS carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- Si el usuario se borra, se borra su carrito
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_cart UNIQUE (user_id) -- Un carrito por usuario
);

-- 5. Items del Carrito
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_product_in_cart UNIQUE (cart_id, product_id)
);

-- 6. Tabla de Órdenes
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Items de la Orden (Detalle histórico)
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL, -- Guardamos nombre por si cambia el producto
    price_at_purchase DECIMAL(10, 2) NOT NULL, -- Precio al momento de la compra
    quantity INTEGER NOT NULL
);

-- DATOS DE EJEMPLO (SEED DATA)
-- Categorías
INSERT INTO categories (name, slug) VALUES 
('Herramientas Manuales', 'herramientas-manuales'),
('Herramientas Eléctricas', 'herramientas-electricas'),
('Pinturas', 'pinturas'),
('Plomería', 'plomeria'),
('Iluminación', 'iluminacion')
ON CONFLICT (slug) DO NOTHING;

-- Productos de Ejemplo (Basados en ferretería típica)
INSERT INTO products (name, description, price, category_id, is_offer, stock, image_url) VALUES
('Taladro Percutor 1/2"', 'Taladro de alta potencia para concreto y madera.', 3500.00, 2, TRUE, 50, 'https://placehold.co/400x300?text=Taladro'),
('Juego de Destornilladores', 'Set de 6 destornilladores punta plana y estrella.', 450.00, 1, FALSE, 100, 'https://placehold.co/400x300?text=Destornilladores'),
('Pintura Blanca 5 Galones', 'Pintura acrílica de alto rendimiento para interiores.', 2800.00, 3, TRUE, 30, 'https://placehold.co/400x300?text=Pintura'),
('Llave Inglesa 10"', 'Llave ajustable de acero cromado.', 600.00, 1, FALSE, 80, 'https://placehold.co/400x300?text=Llave+Inglesa'),
('Bombillo LED 9W', 'Pack de 4 bombillos luz blanca, ahorro de energía.', 350.00, 5, TRUE, 200, 'https://placehold.co/400x300?text=Bombillo+LED');

