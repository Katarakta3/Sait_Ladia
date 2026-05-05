from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'секретный_ключ_12345'


LOGIN_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Вход в систему</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; min-height: 100vh; height: 100%; }
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
        h2 { text-align: center; color: #333; margin-bottom: 50px; font-size: 48px; }
        .input-group { margin-bottom: 30px; }
        label { display: block; font-size: 24px; margin-bottom: 10px; color: #555; font-weight: bold; }
        input {
            width: 100%;
            padding: 25px;
            border: 3px solid #ddd;
            border-radius: 15px;
            font-size: 24px;
        }
        input:focus { border-color: #9b59b6; outline: none; }
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
        }
        button:hover { background: #8e44ad; }
        .info { margin-top: 40px; font-size: 22px; color: #666; text-align: center; background: #f8f9fa; padding: 30px; border-radius: 20px; }
        .info-title { font-size: 26px; color: #333; border-bottom: 3px solid #9b59b6; padding-bottom: 15px; margin-bottom: 20px; }
        .admin-info { background: #f1c40f; color: #333; padding: 20px; border-radius: 15px; margin: 20px 0; font-weight: bold; font-size: 24px; }
        .user-info { background: #ecf0f1; padding: 15px; border-radius: 12px; margin: 10px 0; font-size: 22px; }
        strong { color: #9b59b6; font-size: 24px; }
        .flash-message { color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .error-message { background: #e74c3c; }
        .success-message { background: #27ae60; }
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
            <div class="user-info">Логин: <strong>admin</strong> | Пароль: <strong>admin</strong></div>
            <div style="margin: 30px 0; border-top: 2px dashed #ddd;"></div>
            <div class="admin-info" style="background: #3498db;">👤 ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ</div>
            <div class="user-info">Логин: <strong>ivan</strong> | Пароль: <strong>123456</strong></div>
            <div class="user-info">Логин: <strong>maria</strong> | Пароль: <strong>qwerty</strong></div>
            <div class="user-info">Логин: <strong>petr</strong> | Пароль: <strong>password</strong></div>
        </div>
    </div>
</body>
</html>'''

def check_user(username, password):
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
    session.clear()
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
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
        flash(f'Добро пожаловать, {username}!', 'success')
        
        if user['is_admin']:
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('user_main_page'))
    else:
        flash('❌ Неверное имя пользователя или пароль', 'error')
        return redirect(url_for('login_page'))

@app.route('/user_main')
def user_main_page():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    
    if session.get('is_admin', False):
        return redirect(url_for('admin_panel'))
    
    return send_from_directory('Main', 'Sait.html')

@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    
    if not session.get('is_admin', False):
        flash('Доступ запрещён. Только для администратора', 'error')
        return redirect(url_for('user_main_page'))
    
    return send_from_directory('Main', 'admin.html')

@app.route('/Main/<path:filename>')
def serve_static(filename):
    return send_from_directory('Main', filename)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login_page'))

@app.route('/about')
def about():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    return send_from_directory('Main', 'about.html')

@app.route('/contacts')
def contacts():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    return send_from_directory('Main', 'contacts.html')

@app.route('/tours')
def tours():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    return send_from_directory('Main', 'tours.html')

@app.route('/tour-Baikal')
def tour_baikal():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    return send_from_directory('Main', 'tour-Baikal.html')

@app.route('/tour-karelia')
def tour_karelia():
    if 'username' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login_page'))
    return send_from_directory('Main', 'tour-karelia.html')

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 СЕРВЕР ЗАПУЩЕН")
    print("=" * 50)
    print("📱 Ссылка: http://127.0.0.1:5000")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)