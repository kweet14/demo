CREATE DATABASE shoe_store;

USE shoe_store;


CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role_id INT NOT NULL,

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
);


CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    
    article VARCHAR(20) NOT NULL UNIQUE,
    
    product_name VARCHAR(100) NOT NULL,
    
    unit VARCHAR(20) NOT NULL,
    
    price DECIMAL(10,2) NOT NULL,
    
    supplier_id INT NOT NULL,
    
    manufacturer_id INT NOT NULL,
    
    category_id INT NOT NULL,
    
    discount_percent INT DEFAULT 0,
    
    stock_quantity INT NOT NULL,
    
    description TEXT,
    
    image_path VARCHAR(255),

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id),

    FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers(manufacturer_id),

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);


CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,

    order_date DATE NOT NULL,

    delivery_date DATE NOT NULL,

    pickup_address VARCHAR(255) NOT NULL,

    client_id INT NOT NULL,

    receive_code VARCHAR(10) NOT NULL,

    status VARCHAR(50) NOT NULL,

    FOREIGN KEY (client_id)
        REFERENCES users(user_id)
);


CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,

    order_id INT NOT NULL,

    product_id INT NOT NULL,

    quantity INT NOT NULL,

    price DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
