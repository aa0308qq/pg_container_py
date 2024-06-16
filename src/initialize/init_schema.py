import psycopg


def postgres_init(
    database: str,
    user: str,
    password: str,
    host: str,
    port: int,
):
    postgres_schemas(
        database,
        user,
        password,
        host,
        port,
    )


def postgres_schemas(
    database: str,
    user: str,
    password: str,
    host: str,
    port: int,
):
    connection_info = f"""
                       host={host}
                       port={port}
                       dbname={database}
                       user={user}
                       password={password}
                       """

    with psycopg.connect(connection_info) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS Users (user_id SERIAL PRIMARY KEY,
                                                             username VARCHAR(50) UNIQUE NOT NULL, \
                                                             password VARCHAR(255) NOT NULL, \
                                                             email VARCHAR(100) UNIQUE NOT NULL, \
                                                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS Products (product_id SERIAL PRIMARY KEY, \
                                                                product_name VARCHAR(100) NOT NULL, \
                                                                description TEXT, \
                                                                price NUMERIC(10, 2) NOT NULL, \
                                                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS Orders (order_id SERIAL PRIMARY KEY, \
                                                              user_id INT REFERENCES Users(user_id), \
                                                              order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, \
                                                              total_amount NUMERIC(10, 2) NOT NULL);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS OrderDetails (order_detail_id SERIAL PRIMARY KEY, \
                                                                    order_id INT REFERENCES Orders(order_id), \
                                                                    product_id INT REFERENCES Products(product_id), \
                                                                    quantity INT NOT NULL, \
                                                                    unit_price NUMERIC(10, 2) NOT NULL);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS Reviews (review_id SERIAL PRIMARY KEY, \
                                                               user_id INT REFERENCES Users(user_id), \
                                                               product_id INT REFERENCES Products(product_id), \
                                                               rating INT CHECK (rating >= 1 AND rating <= 5), \
                                                               comment TEXT, \
                                                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")
        conn.commit()
