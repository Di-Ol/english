import os
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)



TOKEN = "8638363412:AAGxe58mQ9LCQkIL5s9I4jf4Kdg_qR918aw"



# ======================
# Загрузка слов
# ======================

def load_file(filename):

    words = []

    path = os.path.join(
        os.path.dirname(__file__),
        filename
    )


    if not os.path.exists(path):
        return []


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:


        for line in file:

            if line.strip():

                ru,en,trans = line.strip().split(" - ")

                words.append(
                    {
                        "ru":ru,
                        "en":en.lower(),
                        "trans":trans
                    }
                )

    return words



WORDS = load_file("words.txt")




# ======================
# Сохранение слова
# ======================

def save_learn(word):

    path = os.path.join(
        os.path.dirname(__file__),
        "learn_words.txt"
    )


    existing = load_file(
        "learn_words.txt"
    )


    for w in existing:

        if w["en"] == word["en"]:
            return


    with open(
        path,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{word['ru']} - {word['en']} - {word['trans']}\n"
        )





# ======================
# START
# ======================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    context.user_data["words"] = WORDS
    context.user_data["index"] = 0
    context.user_data["correct"] = 0
    context.user_data["wrong"] = 0



    await update.message.reply_text(
"""
╭━━━━━━━━━━━━━━╮
 🧠 WORD TRAINER
╰━━━━━━━━━━━━━━╯

Начинаем обучение 🚀
"""
    )


    await send_word(
        update,
        context
    )





# ======================
# Отправка слова
# ======================

async def send_word(
    update,
    context
):

    words = context.user_data["words"]

    index = context.user_data["index"]



    if index >= len(words):

        await finish(
            update,
            context
        )

        return



    word = words[index]



    keyboard = [

        [
            InlineKeyboardButton(
                "📚 Выучить слово",
                callback_data=f"learn_{index}"
            )
        ]

    ]



    await update.message.reply_text(

f"""
╭━━━━━━━━━━━━━━╮

📚 {index+1}/{len(words)}

🇷🇺 <b>{word['ru']}</b>


✍️ Напиши перевод:
╰━━━━━━━━━━━━━━╯
""",

parse_mode="HTML",

reply_markup=InlineKeyboardMarkup(
    keyboard
)

)



# ======================
# Кнопка "выучить"
# ======================

async def button_learn(
    update,
    context
):

    query = update.callback_query

    await query.answer()


    index = int(
        query.data.split("_")[1]
    )


    words = context.user_data["words"]

    word = words[index]


    save_learn(word)



    await query.edit_message_text(

f"""
✅ Добавлено в обучение!


🇬🇧 {word['en']}
🔊 {word['trans']}


Теперь слово доступно в:
📚 /learn
"""
)





# ======================
# Проверка ответа
# ======================

async def check_answer(
    update,
    context
):

    answer = (
        update.message.text
        .lower()
        .strip()
    )

    words = context.user_data["words"]
    index = context.user_data["index"]
    word = words[index]

    if answer == word["en"]:

        context.user_data["correct"] += 1

        await update.message.reply_text(

f"""
╭━━━━━━━━━━━━━━╮
       ✅ ВЕРНО
╰━━━━━━━━━━━━━━╯

🇬🇧 {word['en']}
🔊 {word['trans']}
"""

        )

        # Переходим к следующему слову ТОЛЬКО после правильного ответа
        context.user_data["index"] += 1

        await asyncio.sleep(1)

        await send_word(
            update,
            context
        )

    else:

        context.user_data["wrong"] += 1

        await update.message.reply_text(

f"""
╭━━━━━━━━━━━━━━╮
       ❌ ОШИБКА
╰━━━━━━━━━━━━━━╯

Правильно:

🇬🇧 {word['en']}
🔊 {word['trans']}

✍️ Попробуй ещё раз.
"""

        )

        # Индекс НЕ увеличиваем.
        # То же слово будет показано снова.

        await asyncio.sleep(1)

        await send_word(
            update,
            context
        )





# ======================
# Учить сохранённые слова
# ======================

async def learn(
    update,
    context
):

    learn_words = load_file(
        "learn_words.txt"
    )


    if not learn_words:

        await update.message.reply_text(
            "📚 Список пуст"
        )

        return



    context.user_data["words"] = learn_words

    context.user_data["index"] = 0

    context.user_data["correct"] = 0

    context.user_data["wrong"] = 0



    await update.message.reply_text(
        "📚 Повторяем сложные слова"
    )


    await send_word(
        update,
        context
    )





# ======================
# Статистика
# ======================

async def finish(
    update,
    context
):

    total = len(
        context.user_data["words"]
    )

    correct = context.user_data["correct"]

    wrong = context.user_data["wrong"]


    percent = int(
        correct / total * 100
    )



    await update.message.reply_text(

f"""
╭━━━━━━━━━━━━━━╮
       🏆 РЕЗУЛЬТАТ
╰━━━━━━━━━━━━━━╯


📚 Всего:
{total}


✅ Правильно:
{correct}


❌ Ошибки:
{wrong}


🎯 Точность:
{percent}%


🔥 Отличная работа!
"""

)





# ======================
# Запуск
# ======================


app = Application.builder() \
    .token(TOKEN) \
    .build()



app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CommandHandler(
        "learn",
        learn
    )
)



app.add_handler(
    CallbackQueryHandler(
        button_learn
    )
)



app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        check_answer
    )
)



print("🟢 Бот запущен")


app.run_polling()