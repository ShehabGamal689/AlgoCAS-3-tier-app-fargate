import os
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---- DB helpers -------------------------------------------------------------

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "testdb")  # e.g., sh-3-tier-rds

def get_connection(with_db=True):
    kwargs = dict(host=DB_HOST, user=DB_USER, password=DB_PASS)
    if with_db:
        kwargs["database"] = DB_NAME
    return mysql.connector.connect(**kwargs)

def initialize_database():
    """
    Make sure the database (schema) and table exist.
    Uses CREATE IF NOT EXISTS, so it's safe to run repeatedly.
    """
    # Create DB (if your user has privileges; ok for RDS master)
    conn = get_connection(with_db=False)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.close()
    conn.close()

    # Create table inside the DB
    conn = get_connection(with_db=True)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sample (
          id INT AUTO_INCREMENT PRIMARY KEY,
          info VARCHAR(255) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ---- Routes -----------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    # Keep it DB-free so ALB health checks never flap
    return jsonify({"ok": True}), 200

@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, info FROM sample ORDER BY id ASC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows), 200

@app.route("/api/data", methods=["POST"])
def create_item():
    payload = request.get_json(silent=True) or {}
    info = payload.get("info")
    if not info or not isinstance(info, str):
        return jsonify({"error": "Field 'info' (string) is required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO sample (info) VALUES (%s);", (info,))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "info": info}), 201

@app.route("/api/data/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sample WHERE id = %s;", (item_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if deleted == 0:
        return jsonify({"error": f"id {item_id} not found"}), 404
    return ("", 204)

# ---- Entrypoint -------------------------------------------------------------

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
