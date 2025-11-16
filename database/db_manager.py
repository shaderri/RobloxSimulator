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
    
    # Таблица пользователей
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
            total_game_visits INTEGER DEFAULT 0,
            created_at TEXT,
            avatar_url TEXT,
            balance INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица друзей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_nickname TEXT,
            friend_username TEXT,
            created_at TEXT
        )
    ''')
    
    # Таблица постов
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
    
    # Таблица игр
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
            created_at TEXT
        )
    ''')
    
    # Таблица игровых сессий (для реальной статистики)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            player_id INTEGER,
            session_start TEXT,
            session_end TEXT,
            robux_spent INTEGER DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')
    
    # Таблица лайков/дизлайков игр
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            reaction TEXT,
            created_at TEXT,
            UNIQUE(game_id, user_id),
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')
    
    # Таблица избранного
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            created_at TEXT,
            UNIQUE(game_id, user_id),
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')
    
    # Таблица групп
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            photo_id TEXT,
            title TEXT,
            description TEXT,
            created_at TEXT
        )
    ''')
    
    # Таблица участников групп
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            joined_at TEXT,
            UNIQUE(group_id, user_id),
            FOREIGN KEY (group_id) REFERENCES groups(id)
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
            avatar_url = ?
        WHERE user_id = ?
    ''', (
        data['nickname'], 1 if data['premium'] else 0,
        data['value'], data['rap'], data['friends'],
        data['followers'], data['following'],
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
    
    # Генерация реакций (4-5 знаков)
    reactions = {
        'shrug': random.randint(1000, 9999),
        'shocked': random.randint(1000, 9999),
        'christmas': random.randint(1000, 9999),
        'comments': random.randint(1000, 9999)
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


def get_game_by_title(user_id, title):
    """Получить игру по названию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM games 
        WHERE user_id = ? AND title = ? AND status = 'approved'
    ''', (user_id, title))
    game = cursor.fetchone()
    conn.close()
    return game


def get_game_stats(game_id):
    """Получить реальную статистику игры"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Активные сессии (игроки онлайн)
    cursor.execute('''
        SELECT COUNT(DISTINCT player_id) FROM game_sessions
        WHERE game_id = ? AND session_end IS NULL
    ''', (game_id,))
    online_players = cursor.fetchone()[0]
    
    # Всего визитов
    cursor.execute('''
        SELECT COUNT(*) FROM game_sessions WHERE game_id = ?
    ''', (game_id,))
    total_visits = cursor.fetchone()[0]
    
    # Лайки
    cursor.execute('''
        SELECT COUNT(*) FROM game_reactions 
        WHERE game_id = ? AND reaction = 'like'
    ''', (game_id,))
    likes = cursor.fetchone()[0]
    
    # Дизлайки
    cursor.execute('''
        SELECT COUNT(*) FROM game_reactions 
        WHERE game_id = ? AND reaction = 'dislike'
    ''', (game_id,))
    dislikes = cursor.fetchone()[0]
    
    # Фавориты
    cursor.execute('''
        SELECT COUNT(*) FROM game_favorites WHERE game_id = ?
    ''', (game_id,))
    favorites = cursor.fetchone()[0]
    
    # Заработано Robux
    cursor.execute('''
        SELECT SUM(robux_spent) FROM game_sessions WHERE game_id = ?
    ''', (game_id,))
    earned = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'online_players': online_players,
        'total_visits': total_visits,
        'likes': likes,
        'dislikes': dislikes,
        'favorites': favorites,
        'earned': earned
    }


def update_game_status(game_id, status):
    """Обновить статус игры и запустить симуляцию игроков"""
    import random
    import re
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE games SET status = ? WHERE id = ?', (status, game_id))
    
    if status == 'approved':
        # Получаем данные игры для анализа
        cursor.execute('SELECT title, description, plot FROM games WHERE id = ?', (game_id,))
        game = cursor.fetchone()
        
        if game:
            title = game[0].lower()
            description = game[1].lower()
            plot = game[2].lower()
            
            # Ключевые слова популярных жанров
            popular_keywords = [
                'obby', 'simulator', 'tycoon', 'roleplay', 'rp', 'adventure',
                'horror', 'parkour', 'race', 'battle', 'shooter', 'fps',
                'anime', 'survival', 'zombie', 'adopt', 'pet', 'tower defense',
                'dungeon', 'prison', 'jailbreak', 'murder', 'mystery',
                'admin', 'god', 'speed', 'fly', 'rich', 'money', 'millionaire'
            ]
            
            # Негативные слова (плохие игры)
            negative_keywords = [
                'test', 'тест', 'testing', 'пробная', 'первая игра',
                'не доделана', 'бета', 'alpha', 'альфа', 'черновик',
                'draft', 'wip', 'в разработке', 'плохая', 'bad'
            ]
            
            # Подсчет популярности
            popularity_score = 0
            
            # Проверяем наличие популярных ключевых слов
            text_combined = f"{title} {description} {plot}"
            for keyword in popular_keywords:
                if keyword in text_combined:
                    popularity_score += 1
            
            # Проверяем наличие негативных слов
            for keyword in negative_keywords:
                if keyword in text_combined:
                    popularity_score -= 2
            
            # Длина описания влияет на качество
            if len(description) > 50:
                popularity_score += 1
            if len(plot) > 100:
                popularity_score += 1
            
            # Красивое название (с большой буквы, без цифр в начале)
            if game[0][0].isupper() and not game[0][0].isdigit():
                popularity_score += 1
            
            # Определяем начальные параметры игры
            if popularity_score >= 4:
                # Хитовая игра!
                base_players = random.randint(500, 2000)
                visit_multiplier = random.uniform(5.0, 10.0)
                like_rate = random.uniform(0.85, 0.95)
            elif popularity_score >= 2:
                # Популярная игра
                base_players = random.randint(100, 500)
                visit_multiplier = random.uniform(3.0, 6.0)
                like_rate = random.uniform(0.75, 0.85)
            elif popularity_score >= 0:
                # Обычная игра
                base_players = random.randint(20, 100)
                visit_multiplier = random.uniform(1.5, 3.0)
                like_rate = random.uniform(0.65, 0.75)
            else:
                # Непопулярная игра
                base_players = random.randint(1, 20)
                visit_multiplier = random.uniform(0.5, 1.5)
                like_rate = random.uniform(0.40, 0.60)
            
            # Генерируем начальную статистику
            initial_visits = int(base_players * visit_multiplier)
            total_reactions = int(initial_visits * random.uniform(0.3, 0.5))
            likes = int(total_reactions * like_rate)
            dislikes = total_reactions - likes
            favorites = int(initial_visits * random.uniform(0.05, 0.15))
            
            # Заработок зависит от популярности
            if popularity_score >= 4:
                earned = int(initial_visits * random.uniform(5, 15))
            elif popularity_score >= 2:
                earned = int(initial_visits * random.uniform(2, 8))
            else:
                earned = int(initial_visits * random.uniform(0.5, 3))
            
            # Создаем фейковые сессии игроков
            session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Добавляем активных игроков (онлайн)
            online_count = min(base_players, int(base_players * random.uniform(0.3, 0.7)))
            for _ in range(online_count):
                fake_player_id = random.randint(100000, 999999)
                robux_spent = random.randint(0, 100) if random.random() > 0.7 else 0
                cursor.execute('''
                    INSERT INTO game_sessions (game_id, player_id, session_start, robux_spent)
                    VALUES (?, ?, ?, ?)
                ''', (game_id, fake_player_id, session_start, robux_spent))
            
            # Добавляем завершенные сессии (визиты)
            for _ in range(initial_visits - online_count):
                fake_player_id = random.randint(100000, 999999)
                session_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                robux_spent = random.randint(0, 50) if random.random() > 0.8 else 0
                cursor.execute('''
                    INSERT INTO game_sessions (game_id, player_id, session_start, session_end, robux_spent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (game_id, fake_player_id, session_start, session_end, robux_spent))
            
            # Добавляем лайки
            for _ in range(likes):
                fake_player_id = random.randint(100000, 999999)
                cursor.execute('''
                    INSERT OR IGNORE INTO game_reactions (game_id, user_id, reaction, created_at)
                    VALUES (?, ?, 'like', ?)
                ''', (game_id, fake_player_id, session_start))
            
            # Добавляем дизлайки
            for _ in range(dislikes):
                fake_player_id = random.randint(100000, 999999)
                cursor.execute('''
                    INSERT OR IGNORE INTO game_reactions (game_id, user_id, reaction, created_at)
                    VALUES (?, ?, 'dislike', ?)
                ''', (game_id, fake_player_id, session_start))
            
            # Добавляем фавориты
            for _ in range(favorites):
                fake_player_id = random.randint(100000, 999999)
                cursor.execute('''
                    INSERT OR IGNORE INTO game_favorites (game_id, user_id, created_at)
                    VALUES (?, ?, ?)
                ''', (game_id, fake_player_id, session_start))
    
    conn.commit()
    conn.close()


def simulate_game_activity(game_id):
    """Симуляция активности игроков в игре (вызывается периодически)"""
    import random
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем текущую статистику
    cursor.execute('SELECT COUNT(*) FROM game_sessions WHERE game_id = ? AND session_end IS NULL', (game_id,))
    current_online = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM game_sessions WHERE game_id = ?', (game_id,))
    total_visits = cursor.fetchone()[0]
    
    # Естественное изменение онлайна
    change = random.randint(-5, 10)
    new_online_target = max(1, current_online + change)
    
    session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if change > 0:
        # Добавляем новых игроков
        for _ in range(change):
            fake_player_id = random.randint(100000, 999999)
            robux_spent = random.randint(0, 50) if random.random() > 0.9 else 0
            cursor.execute('''
                INSERT INTO game_sessions (game_id, player_id, session_start, robux_spent)
                VALUES (?, ?, ?, ?)
            ''', (game_id, fake_player_id, session_start, robux_spent))
    else:
        # Завершаем сессии некоторых игроков
        cursor.execute('''
            SELECT id FROM game_sessions 
            WHERE game_id = ? AND session_end IS NULL 
            LIMIT ?
        ''', (game_id, abs(change)))
        sessions_to_end = cursor.fetchall()
        
        session_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for session in sessions_to_end:
            cursor.execute('''
                UPDATE game_sessions SET session_end = ? WHERE id = ?
            ''', (session_end, session[0]))
            
            # Иногда игроки ставят лайк/дизлайк
            if random.random() > 0.7:
                cursor.execute('SELECT player_id FROM game_sessions WHERE id = ?', (session[0],))
                player_id = cursor.fetchone()[0]
                reaction = 'like' if random.random() > 0.3 else 'dislike'
                cursor.execute('''
                    INSERT OR IGNORE INTO game_reactions (game_id, user_id, reaction, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (game_id, player_id, reaction, session_end))
    
    conn.commit()
    conn.close()


def get_pending_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
    game = cursor.fetchone()
    conn.close()
    return game


def create_group(user_id, photo_id, title, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')
    
    cursor.execute('''
        INSERT INTO groups (user_id, photo_id, title, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, photo_id, title, description, created_at))
    group_id = cursor.lastrowid
    
    # Автоматически добавляем создателя в участники
    cursor.execute('''
        INSERT INTO group_members (group_id, user_id, joined_at)
        VALUES (?, ?, ?)
    ''', (group_id, user_id, created_at))
    
    conn.commit()
    conn.close()
    return group_id


def get_group_stats(group_id):
    """Получить статистику группы"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM group_members WHERE group_id = ?', (group_id,))
    members = cursor.fetchone()[0]
    
    conn.close()
    return members


def get_group(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
    group = cursor.fetchone()
    conn.close()
    return group


def add_game_visit(game_id, player_id):
    """Добавить визит в игру (для статистики)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO game_sessions (game_id, player_id, session_start)
        VALUES (?, ?, ?)
    ''', (game_id, player_id, session_start))
    
    # Обновляем общий счетчик визитов пользователя
    cursor.execute('''
        UPDATE users SET total_game_visits = total_game_visits + 1
        WHERE user_id = ?
    ''', (player_id,))
    
    conn.commit()
    conn.close()


def get_user_total_visits(user_id):
    """Получить общее количество визитов в играх пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT total_game_visits FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0