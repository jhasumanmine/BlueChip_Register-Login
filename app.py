from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash,check_password_hash



app = Flask(__name__)

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here
    'database': 'Bluechip'
}

# Function to connect to the MySQL database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# API route for user registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json

    name = data.get('name')
    phone_number = data.get('phone_number')
    country_name = data.get('country_name')
    address = data.get('address')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Input validation
    if not all([name, phone_number, country_name, address, email, password, confirm_password]):
        return jsonify({'error': 'All fields are required!'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match!'}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert user into the database
        insert_query = """
        INSERT INTO users (name, phone_number, country_name, address, email, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, phone_number, country_name, address, email, hashed_password))
        conn.commit()

        return jsonify({'message': 'User registered successfully!'}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()

# API route for user login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Input validation
    if not all([email, password]):
        return jsonify({'error': 'Email and password are required!'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the user by email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
