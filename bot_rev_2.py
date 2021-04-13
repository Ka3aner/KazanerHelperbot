import telebot
import json
bot = telebot.TeleBot('1648049575:AAHXqNdI4iA7f0h-kdpGRYpM4Kdfy_Pri64')

markup = telebot.types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Привет, я бот - планировщик! Я помогу тебе запоминать твои дела! Я умею добавлять задачи в список дел, а также удалять выполненные и изменять, если требуется. Начнём? Выбери опцию из предложенного меню.\
""", reply_markup=markup)

markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
itembtn1 = telebot.types.KeyboardButton('Список задач')
itembtn2 = telebot.types.KeyboardButton('Добавить задачу')
itembtn3 = telebot.types.KeyboardButton('Удалить задачу')
itembtn4 = telebot.types.KeyboardButton('Изменить задачу')
markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'список задач':
        worklist(message)
    elif message.text.lower() == 'добавить задачу':
        message = bot.send_message(message.chat.id, "Какое дело добавляем, командир?")
        bot.register_next_step_handler(message, get_work)
    elif message.text.lower() == 'удалить задачу':
        worklist(message)
        markup_delete = telebot.types.ReplyKeyboardMarkup(row_width=2)
        with open('database.json', 'r', encoding="utf-8") as f:
            database = json.load(f)
        try:
            list = database['persons'][str(message.chat.id)]
            f.close()
        except KeyError:
            pass
        else:
            for i in range(0, len(list)):
                itembtn = telebot.types.KeyboardButton(i+1)
                markup_delete.add(itembtn)
            message = bot.send_message(message.chat.id, "Что удаляем?", reply_markup=markup_delete)
            bot.register_next_step_handler(message, delete_work)
    elif message.text.lower() == 'изменить задачу':
        worklist(message)
        markup_edit = telebot.types.ReplyKeyboardMarkup(row_width=2)
        with open('database.json', 'r', encoding="utf-8") as f:
            database = json.load(f)
        try:
            list = database['persons'][str(message.chat.id)]
            f.close()
        except KeyError:
            pass
        else:
            for i in range(0, len(list)):
                itembtn = telebot.types.KeyboardButton(i + 1)
                markup_edit.add(itembtn)
            message = bot.send_message(message.chat.id, """\
            Изменения - это хорошо. Нечего сидеть на месте! Напиши номер задачи, которую нужно удалить.
            """, reply_markup=markup_edit)
            bot.register_next_step_handler(message, edit_work)
    else:
        bot.send_message(message.chat.id, "Кажется ты написал что-то другое, а не выбрал опцию... Выбери опцию правильно", reply_markup=markup)
        

def worklist(message):
    with open('database.json', 'r', encoding="utf-8") as f:
        database = json.load(f)
    try:
        list = database['persons'][str(message.chat.id)]
    except KeyError:
        bot.send_message(message.chat.id, "Кажется, у вас ещё нет добавленных задач. Давайте сначала добавим первую задачу в список!")
    else:
        f.close()
        answer = 'Список ваших текущих задач:\n'
        if len(list) == 0:
            bot.send_message(message.chat.id, 'Ваш список дел пуст. Нажмите "Добавить задачу" и занесите первую задачу в список!')
        else:
            for i in range(0, len(list)):
                answer += f'{i + 1}. {list[i]}\n'
            bot.send_message(message.chat.id, answer)

def get_work(message):
    work = message.text
    try:
        work_str = str(work)
    except:
        bot.send_message(message.chat.id, "Мне кажется, что задача должна быть описана текстом. Давай попробуй ввести её ещё раз.")
    else:
        with open('database.json', 'r', encoding="utf-8") as f:
            database = json.load(f)
        if str(message.chat.id) in database['persons']:
            database['persons'][str(message.chat.id)].append(work)
        else:
            database['persons'][str(message.chat.id)] = []
            database['persons'][str(message.chat.id)].append(work)
        with open('database.json', 'w', encoding="utf-8") as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        f.close()
        bot.send_message(message.chat.id, "Это очень важное дело! И оно уже в твоём списке!")
        worklist(message)

def delete_work(message):
    try:
        num = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Нужно ввести только номер задачи цифрой. Повторите удаление", reply_markup=markup)
    else:
        with open('database.json', 'r', encoding="utf-8") as f:
            database = json.load(f)
        try:
            database['persons'][str(message.chat.id)].remove(database['persons'][str(message.chat.id)][num-1])
        except IndexError:
            bot.send_message(message.chat.id, "В вашем списке нет задачи с выбранным номером. Повторите удаление", reply_markup=markup)
        except KeyError:
            bot.send_message(message.chat.id, "Кажется, у вас ещё нет добавленных задач. Давайте сначала добавим первую задачу в список!")
        else:
            with open('database.json', 'w', encoding="utf-8") as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            f.close()
            bot.send_message(message.chat.id, "Задача успешно удалена!", reply_markup=markup)
            worklist(message)

def edit_work(message):
    global N
    try:
        N = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Нужно ввести только номер задачи цифрой. Повторите изменение", reply_markup=markup)
    else:
        message = bot.send_message(message.chat.id, "Введите новый текст задачи", reply_markup=markup)
        bot.register_next_step_handler(message, edit_work_step2)

def edit_work_step2(message):
    text = message.text
    with open('database.json', 'r', encoding="utf-8") as f:
        database = json.load(f)
    try:
        database['persons'][str(message.chat.id)][N - 1] = text
    except IndexError:
        bot.send_message(message.chat.id, "В вашем списке нет задачи с выбранным номером. Повторите изменение", reply_markup=markup)
    except KeyError:
        bot.send_message(message.chat.id, "Кажется, у вас ещё нет добавленных задач. Давайте сначала добавим первую задачу в список!")
    else:
        with open('database.json', 'w', encoding="utf-8") as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        bot.send_message(message.chat.id, "Ого, это название намного круче! Так и запишем", reply_markup=markup)
        worklist(message)

bot.polling()
