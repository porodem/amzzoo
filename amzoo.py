#telegram zoo game


import telebot

from datetime import datetime, timedelta
from telebot import types
from telebot.util import update_types
from pprint import pprint # to investigate what inside objects


f = open("token.txt","r")
token = f.readline()
token = token.rstrip() # read about function
print(token, type(token))
f.close()
bot = telebot.TeleBot(token, parse_mode=None)





my_pets_command = types.BotCommand('show_pets','Показать питомцев')
bc_a = types.BotCommand('fun','anekdot')
bot.set_my_commands([my_pets_command,bc_a])


#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    print('---------- ANYTHING -----------')

bot.infinity_polling()


