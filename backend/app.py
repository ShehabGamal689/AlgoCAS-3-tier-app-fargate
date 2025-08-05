import os
import mysql.connector
from flask import Flask, jsonify

# 1) Create the Flask app
app = Flask(__name__)

# 2) Helper to get a DB connection
def get_connection():
    return mysql.connector.connect(
        host     = os.environ.get("DB_HOST", "localhost"),
        user     = os.environ.get("DB_USER", "root"),
        password = os.environ.get("DB_PASS", ""),
        database = os.environ.get("DB_NAME", "testdb")
    )

# 3) Database initialization function
def initialize_database():
    conn = mysql.connector.connect(
        host     = os.environ.get("DB_HOST", "localhost"),
        user     = os.environ.get("DB_USER", "root"),
        password = os.environ.get("DB_PASS", "")
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS testdb;")
    cursor.execute("USE testdb;")
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS sample (
        id   INT AUTO_INCREMENT PRIMARY KEY,
        info VARCHAR(255) NOT NULL
      );
    """)
    # only seed if empty
    cursor.execute("SELECT COUNT(*) FROM sample;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
          "INSERT INTO sample (info) VALUES (%s);",
          ("Hello from Shehab Gamal!",)
        )
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database initialized.")

# 4) Define your API route
@app.route("/api/data")
def get_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, info FROM sample;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

# 5) Main entrypoint: init DB then start Flask
if __name__ == "__main__":
    initialize_database()
    # Now start HTTP server
    app.run(host="0.0.0.0", port=5000, debug=True)
