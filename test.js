// test.js - минимальный тест
const sqlite3 = require('sqlite3');
console.log('1. SQLite3 загружен');

const db = new sqlite3.Database('test.db');
console.log('2. Файл test.db создан/открыт');

db.run('CREATE TABLE IF NOT EXISTS test (id INTEGER)', () => {
    console.log('3. Таблица создана');
    
    db.all('SELECT * FROM test', (err, rows) => {
        console.log('4. Запрос выполнен, rows:', rows);
        db.close();
        console.log('5. Соединение закрыто');
    });
});