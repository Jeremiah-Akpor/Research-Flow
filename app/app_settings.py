import sqlite3
import streamlit as st


class AppSettings:
    def __init__(self, db_path="app/data/settings.db"):
        self.db_path = db_path
        self._create_table()


        self.DIFY_API_URL = self.get_setting("DIFY_API_URL", "http://localhost:8000/v1")
        self.DIFY_API_KEY = self.get_setting("DIFY_API_KEY", "")
        self.SELECTED_CHAT = self.get_setting("SELECTED_CHAT", "")
        self.CONVERSATION_ID = self.get_setting("CONVERSATION_ID", "")

    def _create_table(self):
        """Create settings table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def get_setting(self, key, default=None):
        """Retrieve a setting value from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the value
            else:
                return default

    def set_setting(self, key, value):
        """Save or update a setting value in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            conn.commit()

    def save(self):
        """Save all settings to the database."""

        self.set_setting("DIFY_API_URL", self.DIFY_API_URL)
        self.set_setting("DIFY_API_KEY", self.DIFY_API_KEY)
        self.set_setting("SELECTED_CHAT", self.SELECTED_CHAT)
        self.set_setting("CONVERSATION_ID", self.CONVERSATION_ID)



