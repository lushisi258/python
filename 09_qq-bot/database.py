import sqlite3
from datetime import datetime

class ChatDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 创建用户表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user
                               (openid TEXT PRIMARY KEY, 
                                prompt TEXT)''')
        # 创建点对点消息表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS c2c_messages
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                user_openid TEXT, 
                                content TEXT,
                                timestamp TEXT,
                                FOREIGN KEY (user_openid) REFERENCES user(openid))''')
        # 创建群组消息表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS group_messages
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                group_openid TEXT, 
                                content TEXT,
                                timestamp TEXT,
                                FOREIGN KEY (group_openid) REFERENCES user(openid))''')
        self.conn.commit()

    # 添加用户，如果已经存在则忽略
    def add_user(self, openid):
        self.cursor.execute("INSERT OR IGNORE INTO user (openid) VALUES (?)", 
                            (openid,))
        self.conn.commit()

    # 设置prompt
    def set_prompt(self, openid, remaining):
        self.cursor.execute("INSERT OR REPLACE INTO user (openid, prompt) VALUES (?, ?)", 
                            (openid, remaining))
        self.conn.commit()

    # 录入c2c消息
    def add_c2c_message(self, user_openid, content):
        self.add_user(user_openid)
        timestamp = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO c2c_messages (user_openid, content, timestamp) VALUES (?, ?, ?)", 
                            (user_openid, content, timestamp))
        self.conn.commit()

    # 录入群组消息
    def add_group_message(self, group_openid, content):
        self.add_user(group_openid)
        timestamp = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO group_messages (group_openid, content, timestamp) VALUES (?, ?, ?)", 
                            (group_openid, content, timestamp))
        self.conn.commit()

    # 读取prompt
    def get_prompt(self, openid):
        self.cursor.execute("SELECT prompt FROM user WHERE openid = ?", (openid,))
        result = self.cursor.fetchone()
        print("database prompt result:", result)
        return result[0] if result else None

    # 读取limit条c2c消息并返回消息列表
    def get_c2c_messages(self, user_openid, limit=10):
        self.cursor.execute("""
            SELECT * FROM c2c_messages 
            WHERE user_openid = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_openid, limit))
        messages = self.cursor.fetchall()
        return [msg[2] for msg in messages[::-1]]   # 将结果反转为正序

    # 读取群组消息
    def get_group_messages(self, group_openid, limit=10):
        self.cursor.execute("""
            SELECT * FROM group_messages 
            WHERE group_openid = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (group_openid, limit))
        messages = self.cursor.fetchall()
        return [msg[2] for msg in messages[::-1]] 
    
    # 清空c2c消息
    def clear_c2c_messages(self, user_openid):
        self.cursor.execute("DELETE FROM c2c_messages WHERE user_openid = ?", (user_openid,))
        self.conn.commit()

    # 清空群组消息
    def clear_group_messages(self, group_openid):
        self.cursor.execute("DELETE FROM group_messages WHERE group_openid = ?", (group_openid,))
        self.conn.commit()


    def close(self):
        self.conn.close()