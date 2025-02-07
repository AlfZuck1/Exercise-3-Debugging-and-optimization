from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)

# Simulación de conexión inicial a la base de datos para evitar repetir funciones
def first_db_connection():
    conn = sqlite3.connect("persistent.db")  # Base de datos persistente para realización de pruebas de manera correcta
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);")
    conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, total REAL);")
    # Usuario de prueba que se crea solo si no existe
    conn.execute("INSERT INTO users (id, name) SELECT 123, 'John Doe'" +
                 "WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 123)")  
    # Usuarios de prueba adicionales para la muestra de todos los usuarios cuando no se presenta el parámetro 'id'
    conn.execute("INSERT INTO users (id, name) SELECT 235, 'Pedro Salazar'" +
                 "WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 235)")  
    conn.execute("INSERT INTO users (id, name) SELECT 325, 'Alfredo Santiago'" +
                 "WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 325)") 
    conn.commit()
    return conn

# Simulación de conexión a la base de datos
def get_db_connection():
    return sqlite3.connect("persistent.db")

# Simulación de obtención de usuario
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Simulación de obtención de usuarios
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

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
        
# Simulación de obtención de pedido        
def get_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order
        
# Simulación de modificación de pedido en la base de datos
def modify_order(order_id, user_id, total):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET user_id = ?, total  = ? WHERE id = ?;", (user_id, total, order_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()  # Rollback si hay error de integridad
        raise e
    finally:
        conn.close()


@app.route('/api/users', methods=['GET'])
def get_user_api():
    """Endpoint que muestra todos los usuarios si el parámetro 'id' no está presente"""
    try:
        user_id = request.args.get("id") # Detectamos si está el parámetro "id"
        # Si está el parametro, se obtiene el usuario con el "id" buscado
        if user_id: 
            user = get_user(int(user_id))
            if user:
                return jsonify({"id": user[0], "name": user[1]})
            else:
                return jsonify({"error": "User not found"}), 404
        # Si no está el parametro, se muestran todos los usuarios
        else: 
            users = get_users()
            return jsonify({"error" : "Missing 'id' parameter", "users": users}), 200
    except TypeError:  
        return jsonify({"error": "Inappropriate argument type"}), 400

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Endpoint que modifica la orden si el ID ya existe"""
    try:
        order_data = request.json
        order_id = int(order_data["id"])
        order = get_order(order_id) # Buscar si el id de orden ya está asignado
        # El id de la orden ya existe, por lo que lo modificamos con la nueva información
        if order: 
            modify_order(order_data["id"], order_data["user_id"], order_data["total"])
            return jsonify({"message" : "Order ID already existed",
                            "order" : order}), 200
        # El id de la orden no existe, entonces se puede crear
        else: 
            insert_order(order_data["id"], order_data["user_id"], order_data["total"]) 
            return jsonify({"message": "Order created successfully"}), 201
    except sqlite3.IntegrityError as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Database integrity error"}), 500

if __name__ == '__main__':
    first_db_connection()
    app.run(port=8080, debug=True)