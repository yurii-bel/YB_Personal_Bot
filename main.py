from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook
from bs4 import BeautifulSoup as bs

import os
import requests
import logging

# BOT
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


# BBC News Ukraine
response = requests.get('https://www.bbc.com/ukrainian')
doc = bs(response.content, 'html.parser')

info = ['<u><b>Останні Новини</b></u>']
news_headers = []
news_links = []

links = doc.find_all('a', { 'class': 'bbc-1fxtbkn evnt13t0' })

for link in links:
    news_headers.append(link.text)
    news_links.append('https://www.bbc.com' + link['href'])

for i in range(len(news_headers)):
    info.append(f'\n<b>{news_headers[i]}</b>{news_links[i]}')

# TSN Statistics + News
responseTSN = requests.get('https://tsn.ua/ru')
docTSN = bs(responseTSN.content, 'html.parser')

infoTSN = docTSN.find_all(class_ = 'l-gap-2 c-banner__extra__unit')
outputTSN = ['<u><b>Військові втрати країни загарбника Росії у війні з Україною</b></u>']
for i in range(len(infoTSN)):
    infotext = ' '.join(infoTSN[i].contents[0])
    infovalue = ' '.join(infoTSN[i].contents[1])
    outputTSN.append(f'\n{infotext}: <b>{infovalue}</b>')

# Online Translations (YouTube)    
onlineT = ['<u><b>Онлайн Трансляції</b></u>', '\n<b>Україна 24: </b>https://www.youtube.com/watch?v=IgSn1Z2rq6E', '\n<b>1+1: </b>https://www.youtube.com/watch?v=lhs2JS_f9bI', '\n<b>Freedom 24/7 UA: </b>https://www.youtube.com/watch?v=QCYZSItNniE']


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()
#------------------------------------------------ NEWS


# ----------------------CLIENT 
# buttons
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) # one_time_keyboard=True
    buttons = ["Останні 5 новин", "Військові втрати загарбника", "Онлайн трансляції"]
    keyboard.add(*buttons)
    await message.answer("Виберіть тип подачі новин, натиснувши відповідну кнопку.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Останні 5 новин")
async def lastfive(message: types.Message):
    await bot.send_message(message.from_user.id, ' '.join(info[0:5]))

@dp.message_handler(lambda message: message.text == "Військові втрати загарбника")
async def lastfive(message: types.Message):
    await bot.send_message(message.from_user.id, ' '.join(outputTSN))

@dp.message_handler(lambda message: message.text == "Онлайн трансляції")
async def lastfive(message: types.Message):
    await bot.send_message(message.from_user.id, ' '.join(onlineT))

@dp.message_handler(commands=['help'])
async def commands_start(message : types.Message):
        await message.reply('Команди бота: \n/start \n/help \nТелеграм розробника: @RichDoc888 \nПосилання на бота: https://t.me/YBpersonalbot')


# ----------------------GENERAL

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
