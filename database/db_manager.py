import sqlite3
import pymysql
from sqlalchemy import create_engine
from contextlib import contextmanager
import logging
from config.settings import (
    DATABASE_TYPE, DATABASE_NAME, DATABASE_HOST, 
    DATABASE_USER, DATABASE_PASSWORD, DATABASE_PORT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    _instance = None
    _engine = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database connection"""
        try:
            if DATABASE_TYPE == 'sqlite':
                self.connection_string = f'sqlite:///{DATABASE_NAME}'
                self._engine = create_engine(self.connection_string)
                logger.info(f"SQLite database initialized: {DATABASE_NAME}")
            elif DATABASE_TYPE == 'mysql':
                self.connection_string = (
                    f'mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}'
                    f'@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
                )
                self._engine = create_engine(self.connection_string, pool_pre_ping=True)
                logger.info(f"MySQL database initialized: {DATABASE_NAME}")
            else:
                raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    @property
    def engine(self):
        """Get SQLAlchemy engine"""
        return self._engine
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            if DATABASE_TYPE == 'sqlite':
                connection = sqlite3.connect(DATABASE_NAME)
                connection.row_factory = sqlite3.Row
            elif DATABASE_TYPE == 'mysql':
                connection = pymysql.connect(
                    host=DATABASE_HOST,
                    user=DATABASE_USER,
                    password=DATABASE_PASSWORD,
                    database=DATABASE_NAME,
                    port=DATABASE_PORT
                )
            yield connection
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query, params=None):
        """Execute SELECT query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_insert(self, query, params=None):
        """Execute INSERT query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.lastrowid
    
    def execute_update(self, query, params=None):
        """Execute UPDATE query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    def execute_delete(self, query, params=None):
        """Execute DELETE query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    def execute_batch(self, query, params_list):
        """Execute batch insert/update"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    @staticmethod
    def init_db():
        """Initialize database schema"""
        db = DatabaseManager()
        try:
            with open('database/schema.sql', 'r') as f:
                schema = f.read()
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                if DATABASE_TYPE == 'mysql':
                    for statement in schema.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
                else:
                    cursor.executescript(schema)
                logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Schema initialization failed: {str(e)}")
            raise
    
    @staticmethod
    def close():
        """Close database connection"""
        if DatabaseManager._engine:
            DatabaseManager._engine.dispose()
            logger.info("Database connections closed")
