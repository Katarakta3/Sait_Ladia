from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'секретный_ключ_12345'


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
    return send_from_directory('.', 'index.html')

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