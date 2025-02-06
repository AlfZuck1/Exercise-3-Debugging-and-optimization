from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Simulación de base de datos con SQLite
def get_db_connection():
    conn = sqlite3.connect(":memory:")  # Base de datos en memoria
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);")
    conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, total REAL);")
    conn.execute("INSERT INTO users (id, name) VALUES (123, 'John Doe');")  # Usuario de prueba
    conn.commit()
    return conn

# Simulación de obtención de usuario
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Simulación de inserción de pedido en la base de datos
def insert_order(order_id, user_id, total):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (id, user_id, total) VALUES (?, ?, ?);", (order_id, user_id, total))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()  # Rollback si hay error de integridad
        raise e
    finally:
        conn.close()

@app.route('/api/users', methods=['GET'])
def get_user_api():
    """Endpoint que genera un KeyError si el parámetro 'id' no está presente"""
    try:
        user_id = int(request.args["id"])  # ERROR: Si 'id' no está en la query, lanza KeyError
        user = get_user(user_id)
        if user:
            return jsonify({"id": user[0], "name": user[1]})
        else:
            return jsonify({"error": "User not found"}), 404
    except KeyError:  # Captura error si falta el parámetro
        app.logger.error("KeyError: 'id' - El parámetro 'id' no fue enviado en la solicitud")
        return jsonify({"error": "Missing 'id' parameter"}), 400

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Endpoint que genera un IntegrityError si el ID ya existe"""
    try:
        order_data = request.json
        insert_order(order_data["id"], order_data["user_id"], order_data["total"])  # ERROR si el ID ya existe
        return jsonify({"message": "Order created successfully"}), 201
    except sqlite3.IntegrityError as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Order ID already exists"}), 400

if __name__ == '__main__':
    app.run(port=8080, debug=True)