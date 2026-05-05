
const sqlite3 = require('sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'bd.db');
console.log('📁 Создаю базу данных:', dbPath);

const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    
    db.run(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            Administrator INTEGER NOT NULL DEFAULT 0
        )
    `);
    console.log('✅ Таблица users создана');
    
    db.run(`DELETE FROM users`);
    console.log('✅ Таблица очищена');
    
    const users = [
        ['admin', 'admin', 1],  // admin
        ['ivan', '123456', 0],
        ['maria', 'qwerty', 0],
        ['petr', 'password', 0]
    ];
    
    const stmt = db.prepare("INSERT INTO users (username, password_hash, Administrator) VALUES (?, ?, ?)");
    
    users.forEach(user => {
        stmt.run(user, function(err) {
            if (err) {
                console.log(`❌ Ошибка добавления ${user[0]}:`, err.message);
            }
        });
    });
    
    stmt.finalize();
    console.log('✅ Пользователи добавлены');
    
    db.all(`SELECT id, username, Administrator FROM users`, (err, rows) => {
        if (err) {
            console.log('❌ Ошибка чтения:', err);
        } else {
            console.log('\n🎉 БАЗА ДАННЫХ ГОТОВА!');
            console.log('📁 Файл: bd.db');
            console.log('📊 Таблица: users');
            console.log('📝 Список пользователей:');
            console.log('ID | Имя      | Администратор');
            console.log('-----------------------------');
            rows.forEach(row => {
                console.log(`${row.id.toString().padEnd(3)} | ${row.username.padEnd(8)} | ${row.Administrator ? '✅ Да' : '❌ Нет'}`);
            });
        }
    });
});

setTimeout(() => {
    db.close();
    console.log('\n👋 Соединение закрыто');
}, 1000);