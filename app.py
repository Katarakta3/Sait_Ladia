from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'секретный_ключ_12345'

# HTML страница входа
HTML_СТРАНИЦА = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Вход в систему</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            min-height: 100vh;
            height: 100%;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #71b7e6, #9b59b6);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .login-box {
            background: white;
            padding: 80px;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            width: 90%;
            max-width: 800px;
            margin: 20px;
        }
        
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 50px;
            font-size: 48px;
        }
        
        .input-group {
            margin-bottom: 30px;
        }
        
        label {
            display: block;
            font-size: 24px;
            margin-bottom: 10px;
            color: #555;
            font-weight: bold;
        }
        
        input {
            width: 100%;
            padding: 25px;
            border: 3px solid #ddd;
            border-radius: 15px;
            font-size: 24px;
            transition: all 0.3s;
        }
        
        input:focus {
            border-color: #9b59b6;
            outline: none;
            box-shadow: 0 0 0 4px rgba(155, 89, 182, 0.2);
        }
        
        button {
            width: 100%;
            padding: 30px;
            background: #9b59b6;
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            margin: 40px 0 30px 0;
            transition: all 0.3s;
            letter-spacing: 2px;
        }
        
        button:hover {
            background: #8e44ad;
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .info {
            margin-top: 40px;
            font-size: 22px;
            color: #666;
            text-align: center;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 20px;
            border: 2px solid #e9ecef;
        }
        
        .info-title {
            font-size: 26px;
            color: #333;
            border-bottom: 3px solid #9b59b6;
            padding-bottom: 15px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .admin-info {
            background: #f1c40f;
            color: #333;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            font-weight: bold;
            font-size: 24px;
        }
        
        .user-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 12px;
            margin: 10px 0;
            font-size: 22px;
        }
        
        strong {
            color: #9b59b6;
            font-size: 24px;
        }
        
        .flash-message {
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 18px;
            text-align: center;
        }
        
        .error-message {
            background: #e74c3c;
        }
        
        .success-message {
            background: #27ae60;
        }
        
        @media (max-width: 768px) {
            .login-box {
                padding: 40px;
                width: 95%;
            }
            
            h2 {
                font-size: 36px;
            }
            
            input, button {
                padding: 20px;
                font-size: 20px;
            }
            
            .info {
                font-size: 18px;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 Вход в систему</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message {% if category == 'success' %}success-message{% else %}error-message{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form action="/login" method="POST">
            <div class="input-group">
                <label>Имя пользователя:</label>
                <input type="text" name="username" placeholder="Введите логин" required autofocus>
            </div>
            
            <div class="input-group">
                <label>Пароль:</label>
                <input type="password" name="password" placeholder="Введите пароль" required>
            </div>
            
            <button type="submit">➡️ ВОЙТИ В СИСТЕМУ</button>
        </form>
        
        <div class="info">
            <div class="info-title">📋 Тестовые данные</div>
            <div class="admin-info">👑 АДМИНИСТРАТОР</div>
            <div class="user-info">Логин: <strong>admin</strong> | Пароль: <strong>admin123</strong></div>
            <div style="margin: 30px 0; border-top: 2px dashed #ddd;"></div>
            <div class="admin-info" style="background: #3498db;">👤 ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ</div>
            <div class="user-info">Логин: <strong>ivan</strong> | Пароль: <strong>123456</strong></div>
            <div class="user-info">Логин: <strong>maria</strong> | Пароль: <strong>qwerty</strong></div>
            <div class="user-info">Логин: <strong>petr</strong> | Пароль: <strong>password</strong></div>
        </div>
    </div>
</body>
</html>'''

# Страница профиля для администратора
АДМИН_ПРОФИЛЬ = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Админ-панель</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #71b7e6, #9b59b6);
            margin: 0;
            padding: 50px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .profile-box {
            background: white;
            padding: 50px;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #9b59b6;
            margin-bottom: 30px;
        }
        .info {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            text-align: left;
        }
        .info p {
            font-size: 20px;
            margin: 15px 0;
        }
        .badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            margin-top: 20px;
            background: #f1c40f;
            color: #333;
        }
        button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background: #c0392b;
        }
        .admin-panel {
            background: #f9f9f9;
            border: 2px solid #f1c40f;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            text-align: left;
        }
        .admin-panel h3 {
            color: #f1c40f;
            margin-bottom: 15px;
        }
        .admin-panel p {
            margin: 10px 0;
            font-size: 16px;
        }
        .user-list {
            background: #ecf0f1;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .user-item {
            padding: 8px;
            border-bottom: 1px solid #bdc3c7;
            display: flex;
            justify-content: space-between;
        }
        .user-item:last-child {
            border-bottom: none;
        }
        .back-button {
            background: #3498db;
            margin-top: 20px;
        }
        .back-button:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="profile-box">
        <h1>👑 Панель администратора</h1>
        <div class="info">
            <p><strong>👤 Имя пользователя:</strong> {{ username }}</p>
            <p><strong>🎭 Статус:</strong> <span style="color: #f1c40f; font-weight: bold;">👑 Администратор</span></p>
        </div>
        
        <div class="badge">
            👑 Администратор
        </div>
        
        <div class="admin-panel">
            <h3>🔧 Управление системой</h3>
            <p>✓ У вас есть полный доступ к системе</p>
            <p>✓ Вы можете управлять пользователями</p>
            <p>✓ Доступны все функции администрирования</p>
            
            <div class="user-list">
                <h4>📋 Список пользователей:</h4>
                {% for user in users %}
                <div class="user-item">
                    <span>{{ user[0] }}</span>
                    <span>{% if user[1] %}👑 Админ{% else %}👤 Пользователь{% endif %}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <form action="/logout" method="POST">
            <button type="submit">🚪 Выйти из системы</button>
        </form>
        
        <button class="back-button" onclick="window.location.href='/site'">◀ Назад на сайт</button>
    </div>
</body>
</html>'''


def check_user(username, password):
    """Проверка пользователя в базе данных"""
    conn = sqlite3.connect('bd.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, Administrator 
        FROM users 
        WHERE username = ? AND password_hash = ?
    ''', (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'is_admin': bool(user[2])
        }
    return None


@app.route('/')
def login_page():
    """Страница входа"""
    if 'username' in session:
        if session.get('is_admin', False):
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('user_site'))
    return render_template_string(HTML_СТРАНИЦА)


@app.route('/login', methods=['POST'])
def login():
    """Обработка формы входа"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Пожалуйста, заполните все поля', 'error')
        return redirect(url_for('login_page'))
    
    user = check_user(username, password)
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        
        if user['is_admin']:
            flash(f'👑 Добро пожаловать, администратор {username}!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash(f'👋 Добро пожаловать, {username}!', 'success')
            return redirect(url_for('user_site'))
    else:
        flash('❌ Неверное имя пользователя или пароль', 'error')
        return redirect(url_for('login_page'))


@app.route('/admin')
def admin_panel():
    """Страница для администратора"""
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    
    if not session.get('is_admin', False):
        flash('Доступ запрещен. Требуются права администратора', 'error')
        return redirect(url_for('user_site'))
    
    conn = sqlite3.connect('bd.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, Administrator FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return render_template_string(
        АДМИН_ПРОФИЛЬ,
        username=session['username'],
        users=users
    )


@app.route('/site')
def user_site():
    """Стартовая страница для обычных пользователей"""
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    
    # Проверяем, что это обычный пользователь, а не админ
    if session.get('is_admin', False):
        flash('Администраторы не могут заходить на эту страницу', 'error')
        return redirect(url_for('admin_panel'))
    
    # Путь к файлу: папка Main, файл Sait.html
    file_path = os.path.join('Main', 'Sait.html')
    
    # Проверяем существование файла
    if os.path.exists(file_path):
        return send_from_directory('Main', 'Sait.html')
    else:
        return f"Файл не найден: {file_path}", 404


@app.route('/Main/<path:filename>')
def serve_Main_files(filename):
    """Раздача статических файлов из папки Main (CSS, изображения и т.д.)"""
    return send_from_directory('Main', filename)


@app.route('/<page>')
def serve_page(page):
    """Универсальный маршрут для всех страниц из папки Main"""
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    
    # Список возможных страниц
    pages = ['about', 'contacts', 'tours', 'tour-Baikal', 'tour-karelia']
    
    if page in pages:
        file_path = os.path.join('Main', f'{page}.html')
        if os.path.exists(file_path):
            return send_from_directory('Main', f'{page}.html')
    
    return f"Страница '{page}' не найдена", 404


@app.route('/logout', methods=['POST'])
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 СЕРВЕР ЗАПУЩЕН!")
    print("=" * 50)
    print("📱 Откройте браузер и перейдите по адресу:")
    print("   http://127.0.0.1:5000")
    print("\n📌 Маршруты:")
    print("   • /              - страница входа")
    print("   • /site          - Sait.html (главная страница)")
    print("   • /admin         - админ-панель")
    print("   • /about         - О нас")
    print("   • /contacts      - Контакты")
    print("   • /tours         - Туры и экскурсии")
    print("   • /tour-Baikal   - Тур на Байкал")
    print("   • /tour-karelia  - Тур в Карелию")
    print("   • /Main/<file>   - статические файлы (CSS, изображения)")
    print("\n🛑 Для остановки сервера нажмите Ctrl+C")
    print("=" * 50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

