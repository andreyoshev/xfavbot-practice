#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import sys
import time
import datetime
import pyrebase
import telebot

# Telegram API Auth
token = 'YOUR_TOKEN'
bot = telebot.TeleBot(token)

# Firebase Init
config = {
    "apiKey": "API_KEY",
    "authDomain": "AUTH_DOMAIN",
    "databaseURL": "DATABASE_URL",
    "storageBucket": "BUCKET",
    "serviceAccount": 'PATH/TO/JSON'
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

# - Start, Help commands

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Закладка-бот! Сохраню для тебя ссылки, сообщения и все такое")
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Bookmarks list:\n/bookmarks")

@bot.message_handler(commands=['bookmarks'])
def send_urls(message):
    chat_id = message.chat.id

    bookmarks = []

    try:
        bookmarks = db.child('urls').child(message.chat.id).get().each()
    except TypeError:
        print(TypeError)

    completeMessage = ''

    if bookmarks:
        for i, bookmark in enumerate(bookmarks, start=1):
            completeMessage += '\U0001F4CC{value} \n'.format(index=i, value=bookmark.val())
            completeMessage += 'Delete: /del{id}'.format(id=bookmark.key().replace('-', '_'))
            completeMessage += '\n\n'

        bot.send_message(chat_id, completeMessage, disable_web_page_preview=True)
    else:
        bot.send_message(chat_id, 'Список пуст.')

@bot.message_handler(content_types=['text'])
def add_bookmark(message):
    chat_id = message.chat.id
    text = ''

    if (message.text[:4] == '/del'):
        key = message.text[4:].replace('_', '-')

        bookmarks = []

        try:
            bookmarks = db.child('urls').child(message.chat.id).get().each()
        except TypeError:
            print(TypeError)

        if bookmarks:
            for bookmark in bookmarks:
                if key == bookmark.key():
                    db.child('urls').child(message.chat.id).child(key).remove()
                    bot.send_message(chat_id, 'Удалено!')
        else:
            bot.send_message(chat_id, 'Закладок нет.')

        return

    if message.forward_from:
        text += message.forward_from.username + ' (' + timeConvert(message.forward_date) + '): \n     ' + message.text
    else:
        text = message.text

    try:
        db.child('urls').child(message.chat.id).push(text)
        bot.send_message(chat_id, 'Добавлено!')
    except AttributeError:
        print(AttributeError)

# Helpers
def timeConvert(timestamp):
    return datetime.datetime.fromtimestamp(
        int(timestamp)
    ).strftime('%a, %d %H:%M')


# Initilizing

print ('Listening ...')

def main_loop():
    bot.polling(True, interval=0, timeout=3)
    while 1:
        time.sleep(3)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)