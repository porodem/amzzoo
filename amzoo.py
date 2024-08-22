#telegram zoo game


import telebot

# https://pypi.org/project/emoji/
import emoji

from datetime import datetime, timedelta
from telebot import types
from telebot.util import update_types
from pprint import pprint # to investigate what inside objects

print('- - - - - S T A R T E D - - - - - - ')

f = open("token.txt","r")
token = f.readline()
token = token.rstrip() # read about function
print(token, type(token))
f.close()
bot = telebot.TeleBot(token, parse_mode=None)





my_pets_command = types.BotCommand('show_pets','Показать питомцев')
bc_a = types.BotCommand('fun','anekdot')
bot.set_my_commands([my_pets_command,bc_a])

# legacy func from previous project
@bot.message_handler(regexp=".*(pet|пет).*")
def attach_ls(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('show pets'))
    msg = bot.send_message(message.chat.id, "choose type shit", reply_markup=markup)

#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    print('---------- ANYTHING -----------')
    bot.reply_to(message,emoji.emojize('Python is :thumbs_up:'))

bot.infinity_polling()


