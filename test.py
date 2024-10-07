import sqlite3
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Инициализация базы данных
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


# Добавление игры в список
def add_game_to_db(user_id, game_name):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO games (user_id, game_name) VALUES (?, ?)', (user_id, game_name))

    conn.commit()
    conn.close()


# Убираем игры из списка
def delete_game_from_db(user_id, game_name):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM games WHERE user_id = ? AND game_name = ?', (user_id, game_name))

    conn.commit()
    conn.close()


# Получаем список игр
def get_games_from_db(user_id):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('SELECT game_name FROM games WHERE user_id = ?', (user_id,))
    games = cursor.fetchall()

    conn.close()

    return [game[0] for game in games]


def update_game_status(user_id, game_name, new_status):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE games SET status = ? WHERE user_id = ? AND game_name = ?', (new_status, user_id, game_name))

    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("Мой Список")],
        [KeyboardButton("Добавить Игру"), KeyboardButton("Отметить игру"), KeyboardButton("Удалить Игру")],
        [KeyboardButton("Добавить Категорию"), KeyboardButton("Настройки")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Привет! Я бот по созданию персональных списков игр! Вот, что я могу:',
                                    reply_markup=reply_markup)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if update.message.text == "Мой Список":
        games = get_games_from_db(user_id)  # Получаем список игр пользователя из базы данных
        if games:
            # Формируем строку со списком игр
            games_list = "\n".join(games)
            await update.message.reply_text(f"Ваш список игр:\n{games_list}")
        else:
            await update.message.reply_text("Ваш список игр пуст.")  # Если игр нет, отправляем сообщение об этом

    elif update.message.text == "Добавить Игру":
        await update.message.reply_text("Введите название игры, которую хотите добавить.")
        context.user_data['action'] = 'add_game'  # Сохраняем состояние

    elif update.message.text == "Удалить Игру":
        games = get_games_from_db(user_id)  # Получаем список игр пользователя
        if games:
            # Отправляем пользователю список игр для удаления
            games_list = "\n".join(games)
            await update.message.reply_text(
                f"Выберите игру для удаления:\n{games_list}\nНапишите название игры, чтобы удалить её.")
            context.user_data['action'] = 'delete_game'  # Сохраняем состояние
        else:
            await update.message.reply_text("Ваш список игр пуст.")  # Если игр нет, отправляем сообщение об этом

    elif update.message.text == "Отметить игру":
        games = get_games_from_db(user_id)  # Получаем список игр пользователя
        if games:
            # Отправляем пользователю список игр для отметки статуса
            games_list = "\n".join(games)
            await update.message.reply_text(
                f"Выберите игру для отметки:\n{games_list}\nНапишите название игры, чтобы отметить её.")
            context.user_data['action'] = 'mark_game'  # Сохраняем состояние
        else:
            await update.message.reply_text("Ваш список игр пуст.")  # Если игр нет, отправляем сообщение об этом


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    user_input = update.message.text.strip()  # Получаем текстовое сообщение пользователя

    # Если ожидается добавление игры
    if context.user_data.get('action') == 'add_game':
        if user_input:  # Проверяем, что пользователь ввел не пустую строку
            add_game_to_db(user_id, user_input)  # Добавляем игру в базу данных
            await update.message.reply_text(f"Игра '{user_input}' добавлена в ваш список.")  # Подтверждаем добавление
        else:
            await update.message.reply_text("Название игры не может быть пустым. Пожалуйста, введите название.")

        context.user_data['action'] = None  # Сбрасываем состояние

    # Если ожидается удаление игры
    elif context.user_data.get('action') == 'delete_game':
        if user_input:  # Проверяем, что пользователь ввел не пустую строку
            delete_game_from_db(user_id, user_input)  # Удаляем игру из базы данных
            await update.message.reply_text(f"Игра '{user_input}' удалена из вашего списка.")  # Подтверждаем удаление
        else:
            await update.message.reply_text("Название игры не может быть пустым. Пожалуйста, введите название.")

        context.user_data['action'] = None  # Сбрасываем состояние

    # Если ожидается отметка игры
    elif context.user_data.get('action') == 'mark_game':
        if user_input:  # Проверяем, что пользователь ввел не пустую строку
            # Получаем текущий статус игры
            games = get_games_from_db(user_id)
            game_status = next((game[1] for game in games if game[0] == user_input), 'not_completed')

            # Меняем статус игры
            new_status = 'completed' if game_status == 'not_completed' else 'not_completed'
            update_game_status(user_id, user_input, new_status)  # Обновляем статус игры

            await update.message.reply_text(
                f"Игра '{user_input}' теперь {'Пройдена' if new_status == 'completed' else 'Не пройдена'}.")  # Подтверждаем смену статуса
        else:
            await update.message.reply_text("Название игры не может быть пустым. Пожалуйста, введите название.")

        context.user_data['action'] = None  # Сбрасываем состояние


def main():
    init_db()  # Инициализация базы данных
    application = Application.builder().token("7857387449:AAHiRrI6lEXy-_lYyFITae21WszS_xPkjWE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    application.run_polling()


if __name__ == '__main__':
    main()
