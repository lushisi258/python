import mysql.connector
from mysql.connector import Error
from datetime import datetime

class ChatDatabase:
    def __init__(self, db_name, host, user, password):
        self.db_name = db_name
        self.host = host
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self.connect_to_database()
        self.create_tables()

    def connect_to_database(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name,
                # 设置字符集为utf8mb4
                charset='utf8mb4',
                collation='utf8mb4_general_ci'
            )
            if self.conn.is_connected():
                print(f"Connected to MariaDB database {self.db_name}")
                self.cursor = self.conn.cursor()
        except Error as e:
            print(f"Error while connecting to MariaDB: {e}")

    def create_tables(self):
        # 创建用户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                openid VARCHAR(255) PRIMARY KEY, 
                prompt VARCHAR(255)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
        ''')

        # 创建点对点消息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS c2c_messages (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                user_openid VARCHAR(255), 
                content TEXT,
                timestamp VARCHAR(255),
                FOREIGN KEY (user_openid) REFERENCES user(openid)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
        ''')

        # 创建群组消息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_messages (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                group_openid VARCHAR(255), 
                content TEXT,
                timestamp VARCHAR(255),
                FOREIGN KEY (group_openid) REFERENCES user(openid)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
        ''')

        self.conn.commit()

    # 添加用户，如果已经存在则忽略
    def add_user(self, openid):
        self.cursor.execute("INSERT IGNORE INTO user (openid) VALUES (%s)", 
                            (openid,))
        self.conn.commit()

    # 设置prompt
    def set_prompt(self, openid, remaining):
        self.cursor.execute("REPLACE INTO user (openid, prompt) VALUES (%s, %s)", 
                            (openid, remaining))
        self.conn.commit()

    # 录入c2c消息
    def add_c2c_message(self, user_openid, content):
        self.add_user(user_openid)
        timestamp = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO c2c_messages (user_openid, content, timestamp) VALUES (%s, %s, %s)", 
                            (user_openid, content, timestamp))
        self.conn.commit()

    # 录入群组消息
    def add_group_message(self, group_openid, content):
        self.add_user(group_openid)
        timestamp = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO group_messages (group_openid, content, timestamp) VALUES (%s, %s, %s)", 
                            (group_openid, content, timestamp))
        self.conn.commit()

    # 读取prompt
    def get_prompt(self, openid):
        self.cursor.execute("SELECT prompt FROM user WHERE openid = %s", (openid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # 读取limit条c2c消息并返回消息列表
    def get_c2c_messages(self, user_openid, limit=10):
        self.cursor.execute("""
            SELECT * FROM c2c_messages 
            WHERE user_openid = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (user_openid, limit))
        messages = self.cursor.fetchall()
        return [msg[2] for msg in messages[::-1]]   # 将结果反转为正序

    # 读取群组消息
    def get_group_messages(self, group_openid, limit=10):
        self.cursor.execute("""
            SELECT * FROM group_messages 
            WHERE group_openid = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (group_openid, limit))
        messages = self.cursor.fetchall()
        return [msg[2] for msg in messages[::-1]] 
    
    # 清空c2c消息
    def clear_c2c_messages(self, user_openid):
        self.cursor.execute("DELETE FROM c2c_messages WHERE user_openid = %s", (user_openid,))
        self.conn.commit()

    # 清空群组消息
    def clear_group_messages(self, group_openid):
        self.cursor.execute("DELETE FROM group_messages WHERE group_openid = %s", (group_openid,))
        self.conn.commit()

    def close(self):
        self.conn.close()