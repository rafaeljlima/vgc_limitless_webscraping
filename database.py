import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.cnx = None
        self.cursor = None

    def create_connection(self):
        try:
            self.cnx = mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            self.cnx = None

    def get_cursor(self):
        if self.cnx:
            self.cursor = self.cnx.cursor()
            return self.cursor
        return None

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.cnx:
            self.cnx.close()

    @contextmanager
    def connect(self):
        self.create_connection()
        cursor = self.get_cursor()
        try:
            yield cursor
            self.cnx.commit()
        finally:
            self.close_connection()