import os
import time

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None
        self.max_retries = 5
        self.retry_delay = 2

    def connect(self):
        if self.connection is None:
            retries = 0
            while retries < self.max_retries:
                try:
                    self.connection = psycopg2.connect(
                        host=os.getenv("DB_HOST"),
                        database=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER",),
                        password=os.getenv("DB_PASSWORD"),
                        port=os.getenv("DB_PORT"),
                        connect_timeout=3
                    )
                    print("Подключение успешно!")
                    self._create_tables()
                    return self.connection
                except psycopg2.OperationalError as e:
                    retries += 1
                    print(f"Попытка {retries}/{self.max_retries}: {e}")
                    if retries < self.max_retries:
                        time.sleep(self.retry_delay)
                    else:
                        raise e
        return self.connection

    def _create_tables(self):
        cursor = self.connection.cursor()
        try:
            # Проверяем существование таблицы
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                print("Создание таблиц...")
                cursor.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("CREATE INDEX idx_users_email ON users(email)")
                cursor.execute("CREATE INDEX idx_users_is_active ON users(is_active)")

                self.connection.commit()
                print("Таблицы созданы успешно")
            else:
                print("Таблицы уже существуют")

        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            cursor.close()

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, params)
            if query.strip().lower().startswith(('insert', 'update', 'delete')):
                conn.commit()
            result = cursor.fetchall() if cursor.description else None
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


db = Database()