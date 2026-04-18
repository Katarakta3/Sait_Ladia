// bd.js - Модуль для работы с базой данных bd.db (Node.js версия с SQLite3)

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

class DatabaseManager {
    constructor(dbName = 'bd.db') {
        this.dbName = dbName;
        this.db = null;
    }

    // Инициализация базы данных SQLite
    async initDatabase() {
        return new Promise((resolve, reject) => {
            try {
                // Создаем или открываем базу данных
                this.db = new sqlite3.Database(this.bd.db, (err) => {
                    if (err) {
                        console.error('❌ Ошибка открытия БД:', err);
                        reject(err);
                    } else {
                        console.log(`✅ База данных "${this.bd.db}" открыта успешно`);
                        resolve(this.db);
                    }
                });
            } catch (error) {
                reject(error);
            }
        });
    }

    // Создание таблицы users
    async createUsersTable() {
        if (!this.db) {
            await this.initDatabase();
        }

        // Определяем структуру таблицы
        const таблица = {
            имя: "users",
            поля: [
                { название: "id", тип: "INTEGER", описание: "номер пользователя", ограничения: "PRIMARY KEY AUTOINCREMENT" },
                { название: "username", тип: "TEXT", описание: "имя пользователя", ограничения: "NOT NULL UNIQUE" },
                { название: "password_hash", тип: "TEXT", описание: "хеш пароля пользователя", ограничения: "NOT NULL" },
                { название: "Administrator", тип: "BOOL", описание: "Администратор", ограничения: "NOT NULL DEFAULT 0" }
            ]
        };

        return new Promise((resolve, reject) => {
            // Генерируем SQL запрос
            const sql = this.generateCreateTableSQL(таблица);
            
            console.log('📝 Выполняется SQL:', sql);
            
            this.db.run(sql, (err) => {
                if (err) {
                    if (err.message.includes('already exists')) {
                        console.log(`ℹ️ Таблица "${таблица.имя}" уже существует в ${this.bd.db}`);
                        resolve(sql);
                    } else {
                        console.error('❌ Ошибка создания таблицы:', err);
                        reject(err);
                    }
                } else {
                    console.log(`✅ Таблица "${таблица.имя}" создана в ${this.bd.db}`);
                    resolve(sql);
                }
            });
        });
    }

    // Генерация SQL запроса для SQLite
    generateCreateTableSQL(table) {
        const поляSQL = table.поля.map(поле => {
            // Конвертируем типы для SQLite
            let тип = поле.тип;
            if (тип.includes('VARCHAR')) тип = 'TEXT';
            if (тип === 'INT') тип = 'INTEGER';
            if (тип === 'BOOL') тип = 'INTEGER';
            
            // Конвертируем ограничения
            let ограничения = поле.ограничения || '';
            ограничения = ограничения.replace('AUTO_INCREMENT', 'AUTOINCREMENT');
            
            return `    ${поле.название} ${тип} ${ограничения}`.trim();
        }).join(',\n');
        
        return `CREATE TABLE IF NOT EXISTS ${table.имя} (\n${поляSQL}\n);`;
    }

  

    // Получение всех пользователей
    async getAllUsers() {
        if (!this.db) {
            await this.initDatabase();
        }

        return new Promise((resolve, reject) => {
            const sql = `SELECT * FROM users`;
            
            this.db.all(sql, [], (err, rows) => {
                if (err) {
                    console.error('❌ Ошибка получения пользователей:', err);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }


    // Получение информации о БД
    getDBInfo() {
        return {
            name: this.dbName,
            path: path.resolve(this.dbName),
            size: fs.existsSync(this.dbName) ? fs.statSync(this.dbName).size : 0
        };
    }

    // Закрытие базы данных
    async close() {
        return new Promise((resolve, reject) => {
            if (this.db) {
                this.db.close((err) => {
                    if (err) {
                        reject(err);
                    } else {
                        console.log('👋 База данных закрыта');
                        resolve();
                    }
                });
            } else {
                resolve();
            }
        });
    }
}

module.exports = { DatabaseManager };
