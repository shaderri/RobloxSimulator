import sqlite3
import json
from datetime import datetime
from config import DB_PATH, DEFAULT_BALANCE
import os


def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT,
            premium INTEGER DEFAULT 0,
            value INTEGER DEFAULT 0,
            rap INTEGER DEFAULT 0,
            friends INTEGER DEFAULT 0,
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            visits INTEGER DEFAULT 0,
            created_at TEXT,
            avatar_url TEXT,
            balance INTEGER DEFAULT 0,
            last_daily TEXT,
            total_earned INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_nickname TEXT,
            friend_username TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            content TEXT,
            reactions TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            photo_id TEXT,
            title TEXT,
            description TEXT,
            plot TEXT,
            gamepasses TEXT,
            status TEXT DEFAULT 'moderation',
            online_players INTEGER DEFAULT 0,
            visits INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            favorites INTEGER DEFAULT 0,
            earned INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            photo_id TEXT,
            title TEXT,
            description TEXT,
            members INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y')
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, created_at, balance)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, created_at, DEFAULT_BALANCE))
    conn.commit()
    conn.close()


def update_user_account(user_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET
            nickname = ?, premium = ?, value = ?, rap = ?,
            friends = ?, followers = ?, following = ?,
            visits = ?, avatar_url = ?
        WHERE user_id = ?
    ''', (
        data['nickname'], 1 if data['premium'] else 0,
        data['value'], data['rap'], data['friends'],
        data['followers'], data['following'], data['visits'],
        data['avatar_url'], user_id
    ))
    conn.commit()
    conn.close()


def get_user_balance(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def add_friend(user_id, friend_nickname, friend_username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')
    cursor.execute('''
        INSERT INTO friendships (user_id, friend_nickname, friend_username, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, friend_nickname, friend_username, created_at))
    conn.commit()
    conn.close()


def create_post(user_id, username, content):
    import random
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')
    reactions = {
        'laugh': random.randint(1000, 9999),
        'love': random.randint(1000, 9999),
        'fire': random.randint(1000, 9999),
        'comments': random.randint(500, 5000)
    }
    cursor.execute('''
        INSERT INTO posts (user_id, username, content, reactions, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, content, json.dumps(reactions), created_at))
    conn.commit()
    conn.close()
    return reactions


def create_game(user_id, username, photo_id, title, description, plot, gamepasses):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')
    cursor.execute('''
        INSERT INTO games (user_id, username, photo_id, title, description, plot, gamepasses, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, photo_id, title, description, plot, gamepasses, created_at))
    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return game_id


def get_game(user_id, title):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM games 
        WHERE user_id = ? AND title = ? AND status = 'approved'
    ''', (user_id, title))
    game = cursor.fetchone()
    conn.close()
    return game


def get_pending_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
    game = cursor.fetchone()
    conn.close()
    return game


def update_game_status(game_id, status):
    import random
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if status == 'approved':
        cursor.execute('''
            UPDATE games SET status = ?, online_players = ?, visits = ?,
                likes = ?, dislikes = ?, favorites = ?, earned = ?
            WHERE id = ?
        ''', (status, random.randint(10, 500), random.randint(1000, 50000),
              random.randint(100, 5000), random.randint(10, 500),
              random.randint(50, 2000), random.randint(500, 10000), game_id))
    else:
        cursor.execute('UPDATE games SET status = ? WHERE id = ?', (status, game_id))
    conn.commit()
    conn.close()


def create_group(user_id, photo_id, title, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')
    cursor.execute('''
        INSERT INTO groups (user_id, photo_id, title, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, photo_id, title, description, created_at))
    group_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return group_id


def get_group(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
    group = cursor.fetchone()
    conn.close()
    return group