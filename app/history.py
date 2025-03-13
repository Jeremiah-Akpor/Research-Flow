import sqlite3
import streamlit as st
import logging
from logging.handlers import RotatingFileHandler
# import app.state_manager as state_manager
import json

# Configure logging
log_file = "app.log"
handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=0)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
for h in logger.handlers[:]:
    logger.removeHandler(h)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class ChatHistory:
    def __init__(self):
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()

        # Create chat_sessions table with a timestamp column
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                file_name TEXT,   -- Added column for the uploaded file name
                file_id TEXT,     -- Added column for the uploaded file id
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create user_inputs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        """)

        # Create chat_messages table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                user_input_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                edited_code TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id),
                FOREIGN KEY (user_input_id) REFERENCES user_inputs (id)
            )
        """)

        self.conn.commit()
        self.conn.close()

    def fetch_chat_sessions(self):
        """
        Fetch all chat sessions ordered by timestamp (newest first).
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            SELECT title FROM chat_sessions 
            ORDER BY timestamp DESC
        """)
        sessions = [row[0] for row in self.cursor.fetchall()]
        self.conn.close()
        return sessions

    def create_chat_session(self, title):
        try:
            self.conn = sqlite3.connect("app/data/chat_history.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
            self.conn.commit()
            logging.info(f"Chat session '{title}' created successfully!")
        except sqlite3.IntegrityError:
            st.error(f"Chat session '{title}' already exists!")
        finally:
            self.conn.close()

    def delete_chat_session(self, title):
        try:
            self.conn = sqlite3.connect("app/data/chat_history.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT id FROM chat_sessions WHERE title = ?", (title,))
            session = self.cursor.fetchone()
            if session:
                session_id = session[0]
                self.cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
                self.cursor.execute("DELETE FROM user_inputs WHERE session_id = ?", (session_id,))
                self.cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
                self.conn.commit()
                st.success(f"Chat session '{title}' and its messages deleted successfully!")
            else:
                st.warning(f"Chat session '{title}' not found!")
        except Exception as e:
            st.error(f"Error deleting chat session: {e}")
        finally:
            self.conn.close()

    def add_user_input(self, session_title, content):
        """
        Add a user input to the user_inputs table and update the session's timestamp.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()

        # Get the session ID
        self.cursor.execute("SELECT id FROM chat_sessions WHERE title = ?", (session_title,))
        session = self.cursor.fetchone()
        if not session:
            raise ValueError(f"Session with title '{session_title}' not found.")
        session_id = session[0]

        # Insert user input
        self.cursor.execute(
            "INSERT INTO user_inputs (session_id, content) VALUES (?, ?)",
            (session_id, content)
        )

        # Update the timestamp for the session
        self.cursor.execute(
            "UPDATE chat_sessions SET timestamp = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )

        self.conn.commit()
        user_input_id = self.cursor.lastrowid
        self.conn.close()
        return user_input_id
    
    def get_user_input_id(self, session_title, content):
        """
        Get the user input ID for a specific user input content.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()

        # Get the session ID
        self.cursor.execute("SELECT id FROM chat_sessions WHERE title = ?", (session_title,))
        session = self.cursor.fetchone()
        if not session:
            raise ValueError(f"Session with title '{session_title}' not found.")
        session_id = session[0]

        # Get the user input ID
        self.cursor.execute(
            "SELECT id FROM user_inputs WHERE session_id = ? AND content = ?",
            (session_id, content)
        )
        user_input = self.cursor.fetchone()
        if not user_input:
            raise ValueError(f"User input with content '{content}' not found.")
        user_input_id = user_input[0]
        self.conn.close()
        return user_input_id

    def add_ai_response(self, session_title, user_input_id, content, version=1):
        """
        Add an AI response linked to a specific user input.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()

        # Get the session ID
        self.cursor.execute("SELECT id FROM chat_sessions WHERE title = ?", (session_title,))
        session = self.cursor.fetchone()
        if not session:
            raise ValueError(f"Session with title '{session_title}' not found.")
        session_id = session[0]

        # Insert AI response
        self.cursor.execute(
            "INSERT INTO chat_messages (session_id, user_input_id, role, content, version, edited_code) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, user_input_id, "ai", content, version, "")
        )
        self.conn.commit()
        self.conn.close()
    
    def update_user_input(self, user_input_id, content):
        """
        Update the content of a user input.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE user_inputs SET content = ? WHERE id = ?", (content, user_input_id))
        self.conn.commit()
        self.conn.close()

    def get_ai_responses(self, user_input_id):
        """
        Retrieve all AI responses for a specific user input, ordered by version.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            SELECT content, version FROM chat_messages
            WHERE user_input_id = ?
            ORDER BY version ASC
        """, (user_input_id,))
        responses = self.cursor.fetchall()
        self.conn.close()
        return responses
    
    def update_ai_response(self, user_input_id, version, content):
        """
        Update the content of an AI response.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE chat_messages SET content = ? WHERE user_input_id = ? AND version = ?", (content, user_input_id, version))
        self.conn.commit()
        self.conn.close()
    
    def update_ai_response_code(self, user_input_id, version, edited_code):
        """
        Update the content of an AI response.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE chat_messages SET edited_code = ? WHERE user_input_id = ? AND version = ?", (edited_code, user_input_id, version))
        self.conn.commit()
        self.conn.close()

    def fetch_chat_messages(self, session_title):
        """
        Fetch all messages for a given chat session.
        """
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            SELECT ui.content AS user_input, cm.role, cm.content AS message, cm.version, cm.edited_code 
            FROM user_inputs ui
            LEFT JOIN chat_messages cm ON ui.id = cm.user_input_id
            INNER JOIN chat_sessions cs ON ui.session_id = cs.id
            WHERE cs.title = ?
            ORDER BY ui.id, cm.version ASC
        """, (session_title,))
        messages = self.cursor.fetchall()
        self.conn.close()
        return messages

    def load_chat_into_session_state(self, selected_chat):
        
        st.session_state["messages"] = []

        messages = self.fetch_chat_messages(selected_chat)
        user = ""
        for user_input, role, message, version, edited_code in messages:
            user_input_id = self.get_user_input_id(selected_chat, user_input)
            ai_responses = self.get_ai_responses(user_input_id)
            max_version = len(ai_responses)
            if user_input != user:
                user_in = json.loads(user_input)
                st.session_state["messages"].append({
                    "role": "user",
                    "content": user_in["Query"],
                    # "web_search": user_in["WebSearch"],
                    # "advanced_search": user_in["AdvanceSearch"],
                    "version": 1,
                    "user_input_id": user_input_id,
                })
                user = user_input
            
            if role == "ai" and version == max_version:
                if edited_code != "":
                    message = f"{message}\n\n <strong>Edited Code:<strong> \n {edited_code}"
                st.session_state["messages"].append({
                        "user_input_id": user_input_id,
                        "user_input": user_input,
                        "role": role,
                        "content": message,
                        "version": version,
                        # "show_code_editor": False,
                        # "edited_code": edited_code,
                        
                    })
    
    def load_chat_history(self, selected_chat):
        
        msg = []

        messages = self.fetch_chat_messages(selected_chat)
        user = ""
        for user_input, role, message, version, edited_code in messages:
            user_input_id = self.get_user_input_id(selected_chat, user_input)
            ai_responses = self.get_ai_responses(user_input_id)
            max_version = len(ai_responses)
            if user_input != user:
                user_in = json.loads(user_input)
                msg.append({
                    "role": "user",
                    "content": user_in["Query"],
                })
                user = user_input
            
            if role == "ai" and version == max_version:
                msg.append({
                        "role": role,
                        "content": message,
                    })
        return msg
    
    def change_chat_name(self, old_name, new_name):
        self.conn = sqlite3.connect("app/data/chat_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE chat_sessions SET title = ? WHERE title = ?", (new_name, old_name))
        self.conn.commit()
        self.conn.close()
        logging.info(f"Chat session '{old_name}' renamed to '{new_name}'.")
    
    def save_file_info(self, session_title: str, file_name: str, file_id: str):
        """
        Save the file name and file ID for a chat session identified by session_title.
        If the session exists, update its file_name and file_id columns.
        """
        db_path: str = "app/data/chat_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = """
            UPDATE chat_sessions 
            SET file_name = ?, file_id = ? 
            WHERE title = ?
        """
        cursor.execute(query, (file_name, file_id, session_title))
        conn.commit()
        conn.close()

    def load_file_info(self, session_title: str, ):
        """
        Load and return the file name and file ID for the chat session identified by session_title.
        Returns a tuple (file_name, file_id), or (None, None) if the session is not found.
        """
        db_path: str = "app/data/chat_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT file_name, file_id 
            FROM chat_sessions 
            WHERE title = ?
        """
        cursor.execute(query, (session_title,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"file_name": result[0], "file_id": result[1]}
        else:
            return {}
            
        

    


# 
#import sqlite3

# def update_database_schema():
#         conn = sqlite3.connect("app/data/chat_history.db")
#         cursor = conn.cursor()

#         # Add a 'version' column to 'chat_messages' if it doesn't exist
#         cursor.execute("""
#         PRAGMA table_info(chat_messages)
#         """)
#         columns = [col[1] for col in cursor.fetchall()]

#         if "version" not in columns:
#             cursor.execute("""
#             ALTER TABLE chat_messages ADD COLUMN version INTEGER DEFAULT 1
#             """)
#             print("Added 'version' column to 'chat_messages'.")
#         else:
#             print("'version' column already exists in 'chat_messages'.")

#         conn.commit()
#         conn.close()
    

# if __name__ == "__main__":
#     update_database_schema()
    