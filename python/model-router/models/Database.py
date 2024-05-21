from dataclasses import dataclass
import psycopg2
import os

@dataclass
class Database:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int  # Make port an integer for type safety

    @classmethod
    def from_env(cls):
        """Factory method to create a Database instance from environment variables."""
        return cls(
            db_name=os.getenv('POSTGRES_DB'),
            db_user=os.getenv('POSTGRES_USER'),
            db_password=os.getenv('POSTGRES_PASSWORD'),
            db_host=os.getenv('POSTGRES_HOST'),
            db_port=int(os.getenv('POSTGRES_PORT', 5432)),
        )

    def connect(self):
        """Establish a connection to the database."""
        db_config = {
            'dbname': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'host': self.db_host,
            'port': self.db_port,
        }
        return psycopg2.connect(**db_config)

    def db_version(self):
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                record = cursor.fetchone()
                return record[0]