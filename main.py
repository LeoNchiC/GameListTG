import sqlite3
from math import gamma

import keyboard
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


def init_db():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            status TEXT DEFAULT 'not_completed'
        )
    ''')

    conn.commit()
    conn.close()


def add_game_add_to_db(user_id, game_name):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO games (user_id, game_name) VALUES (?, ?)', (user_id, game_name))

    conn.commit()
    conn.close()


def delete_game_from_db(user_id, game_name):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM games WHERE user_id = ? AND game_name = ?', (user_id, game_name))

    conn.commit()
    conn.close()


def get_games_from_db(user_id, game_name, new_status):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM games WHERE user_id = ? AND game_name = ?', (user_id, game_name))
    games = cursor.fetchall()

    conn.close()

    return [game[0] for game in games]


def upadate_game_status(user_id, game_name, new_status):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE games SET status = ? WHERE user_id = ? AND game_name = ?', (new_status, user_id, game_name))

    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes):
    keyboard = [
        [KeyboardButton("Мой Список")],
        [KeyboardButton("Добавить Игру"),KeyboardButton("Удалить Игру")],
        [KeyboardButton("Отметить Игру"), KeyboardButton("Настройки")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Привет! Я бот по созданию персональных списков игр! Вот, что я могу:',
                                    reply_markup=reply_markup)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if update.message.text == "Мой Список":
        games = get_games_from_db(user_id)
        if games:

            games_list = "\n".join(games)
            await update.message.reply_text(f"Ваш список игр:\n{games_list}")
        else:
            await update.message.reply_text("Ваш список игр пуст")

    elif update.message.text == "Добавить Игру":
        await update.message.reply_text("Введите название игры, которую хотите добавить")
        context.user_data['action'] = 'add_game'

    elif update.message.text == "Удалить Игру":
        games = get_games

