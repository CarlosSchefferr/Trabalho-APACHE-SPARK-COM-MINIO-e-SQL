CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    order_date DATE NOT NULL
);

INSERT INTO customers (id, name, city, status) VALUES
    (1, 'Ana Souza', 'São Paulo', 'active'),
    (2, 'Bruno Lima', 'Rio de Janeiro', 'active'),
    (3, 'Carla Dias', 'Belo Horizonte', 'inactive');

INSERT INTO products (id, name, price) VALUES
    (1, 'Notebook', 4500.00),
    (2, 'Mouse', 120.00),
    (3, 'Teclado', 230.00);

INSERT INTO orders (id, customer_id, product_id, quantity, order_date) VALUES
    (1, 1, 1, 1, DATE '2026-05-01'),
    (2, 1, 2, 2, DATE '2026-05-02'),
    (3, 2, 3, 1, DATE '2026-05-03');
