# /exam/flask_app/database.py

import mysql.connector
from flask import current_app
import os

class database:
    def __init__(self):
        conn_kwargs = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "auth_plugin": "mysql_native_password"
        }

        if os.getenv("DB_SOCKET"):
            conn_kwargs["unix_socket"] = os.getenv("DB_SOCKET")
        else:
            conn_kwargs.update({
                "host": os.getenv("DB_HOST"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "ssl_disabled": True
            })

        self.db = mysql.connector.connect(**conn_kwargs)
        self.db.autocommit = True
        self.tables = ['users', 'events', 'participants', 'availability']

    def createTables(self): 
            
        cur = self.db.cursor()
        for table in self.tables:
            path = os.path.join("flask_app", "models", f"{table}.sql")
            with open(path, encoding="utf-8") as f:
                query = f.read()
                if query.strip():
                    print(f"Executing query from {table}.sql:")
                    print(query)
                    cur.execute(query)

    def createUser(self, email, password):
        cur = self.db.cursor(dictionary=True)
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))

    def authenticate(self, email, password):
        cur = self.db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        return cur.fetchone()

    def query(self, query, parameters=None):
        cur = self.db.cursor(dictionary=True)
        cur.execute(query, parameters or ())
        if cur.description:
            return cur.fetchall()
        return []

    def insertRows(self, table, columns, rows):
        cur = self.db.cursor()
        col_str = ", ".join(columns)
        val_str = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table} ({col_str}) VALUES ({val_str})"
        cur.executemany(query, rows)

    def delete(self, query, parameters=None):
        cur = self.db.cursor()
        cur.execute(query, parameters or ())

    def update(self, query, parameters=None):
        cur = self.db.cursor()
        cur.execute(query, parameters or ())
