import logging
import sqlite3
from datetime import datetime, timedelta
import requests
import certifi
from decimal import Decimal
import random
import string
import time
import threading
import psutil
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import asyncio
import aiosqlite
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio


def create_database():
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  # Создание таблицы users, если она ещё не существует
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        expiration_date DATETIME
    );
    ''')

  conn.commit()
  conn.close()


create_database()

# Функция для проверки статуса подписки
def check_subscription_status(user_id):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      days_left = (date - current_date).days
      status = f"<b>🦎 Triton Botnet \n\n📘 У вас присутствует активная подписка\n📘 У вас осталось {days_left} дней\n\n🆔 Ваш ID: {user_id}\n\n⚙️ Админ: @tritonbotnetsupport \n💙.Наш канал: @TritonBotnet\n💙 Приятного пользования</b>"
    else:
      status = f"<b>🦎 Triton Botnet \n\n📘 У вас истекла подписка.\n\n🆔 Ваш ID: {user_id}\n\n⚙️ Админ: @TritonBotnetSupport \n💙 Наш канал: @TritonBotnet\n💙 Приятного пользования </b>"
  else:
    status = f"<b>🦎 Triton Botnet \n\n📘 У вас отсутствует подписка.\n\n🆔 Ваш ID: {user_id}\n\n⚙️ Админ: @TritonBotnetSupport \n💙Наш канал: @TritonBotnet\n💙 Приятного пользования </b>"

  conn.close()
  return status

def check_subscription(user_id):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()
  conn.close()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      return True
    else:
      return False
  else:
    return False

def generate_payment_link(payment_system, amount):
    api_url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}
    data = {
        "asset": payment_system,
        "amount": float(amount)
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        json_data = response.json()
        invoice = json_data.get("result")
        payment_link = invoice.get("pay_url")
        invoice_id = invoice.get("invoice_id")
        return payment_link, invoice_id
    else:
        return None, None

def get_invoice_status(invoice_id):
    api_url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            invoices = json_data.get("result")
            if invoices and 'items' in invoices and invoices['items']:
                status = invoices['items'][0]['status']
                payment_link = invoices['items'][0]['pay_url']
                amount = Decimal(invoices['items'][0]['amount'])
                return status, payment_link, amount

    return None, None, None

def get_exchange_rates():
    api_url = "https://pay.crypt.bot/api/getExchangeRates"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            return json_data["result"]
    return []

def convert_to_crypto(amount, asset):
    rates = get_exchange_rates()
    rate = None
    for exchange_rate in rates:
        if exchange_rate["source"] == asset and exchange_rate["target"] == 'USD':
            rate = Decimal(str(exchange_rate["rate"]))
            break

    if rate is None:
        raise ValueError(f"🦎 Не удалось найти курс обмена для {asset}")

    amount = Decimal(str(amount))
    return amount / rate

# все нужные переменные
Crypto_Pay_API_Token = "293590:AAlt71MpjmpzLgJRsltIgbjVMcRyxZXwfif"
API_TOKEN = '8042077927:AAGHIDBtb8i4iCn1mNKzSljC2PrPxY34LIQ'
admin_id = 6323126879
log_chat_id = -4109056193
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
emails = ['anonymous854785@gmail.com:wmth dinz jiek nhfy', 'zlotema12@gmail.com:xxie yzkz wdyk ugxm', 'maybelox231@gmail.com:auov fern blju utwf', 'andeybirum@gmail.com:ouho uujv htlm rwaz', 'faverokstandof@gmail.com:nrsg kchi etta uuzh', 'faveroktt@gmail.com:dywo rgle jjwl hhbq', 'mksmksergeev@gmail.com:ycmw rqii rcbd isfd', 'maksimafanacefish@gmail.com:hdpn tbfp acwv jyro']
recipient = 'sms@telegram.org, dmca@telegram.org, abuse@telegram.org, sticker@telegram.org, stopCA@telegram.org, recover@telegram.org, support@telegram.org, security@telegram.org'

# мой любымый стартик
async def start_cmd(message):
    register = await check_user(message.chat.id)
    if not register:
        with open('had2.jpg', 'rb') as had:
            await message.answer_photo(
                photo=had,
                caption='<b> 🦎 Приветствуем вас в Triton Botnet!</b>',
                parse_mode='HTML'
            )

del_markup = types.InlineKeyboardMarkup(row_width=2)
del_button = types.InlineKeyboardButton("❌ Назад", callback_data="del")
del_markup.add(del_button)

back_markup = types.InlineKeyboardMarkup(row_width=2)
back_button = types.InlineKeyboardButton("❌ Назад", callback_data="back")
back_markup.add(back_button)

@dp.message_handler(commands=['start'])
async def home(message: types.Message):
    await start_cmd(message)
    if check_subscription(message.chat.id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        chanell = types.InlineKeyboardButton("🦎 Наш канал", url='https://t.me/TritonBotnet')
        cabinet = types.InlineKeyboardButton("📊 Профиль", callback_data='cabinet')
        snosermail = types.InlineKeyboardButton("💣 Отправка жалоб", callback_data='snoser')
        soglas = types.InlineKeyboardButton("💙 Пользовательское соглашение", url='https://telegra.ph/Polzovatelskoe-soglashenie-Picklmail-02-21')
        markup.add(chanell, cabinet, snosermail)
        with open('had2.jpg', 'rb') as had:
            await message.answer_photo(
                photo=had,
                caption='<b>🦎 Triton Botnet Menu!\n\n🦎 Вы находитесь в главном меню\n🦎 Ниже предоставлены кнопки для удобного управления\n\n💙 Удачного пользования! </b>',
                reply_markup=markup, parse_mode='HTML'
            )
    else:
        markup = types.InlineKeyboardMarkup()
        cabinet = types.InlineKeyboardButton("📊 Профиль", callback_data='cabinet')
        chanell = types.InlineKeyboardButton("🦎 Наш канал", url='https://t.me/TritonBotnet')
        my_sub = types.InlineKeyboardButton("💸 Подписка", callback_data='my_sub')
        soglas = types.InlineKeyboardButton("💙 Пользовательское соглашение", url='https://telegra.ph/Polzovatelskoe-soglashenie-Picklmail-02-21')
        markup.add(chanell, cabinet, my_sub)
        with open('had2.jpg', 'rb') as had:
            await message.answer_photo(
                photo=had,
                caption='<b>🦎 Triton Botnet Menu!\n\n🦎 Вы находитесь в главном меню\n🦎 Ниже предоставлены кнопки для удобного управления\n\n💙 Удачного пользования </b>',
                reply_markup=markup, parse_mode='HTML'
            )
# мая любимая админка
with open('blacklisted_channels.txt', 'r') as file:
    blacklisted_channels = [channel.strip() for channel in file.readlines()]

@dp.message_handler(commands=['admin'])
async def admin_cmd(message: types.Message):
    if message.chat.id == admin_id:
        markup = types.InlineKeyboardMarkup(row_width=1)
        send_sub = types.InlineKeyboardButton("💎Выдать подписку", callback_data='send_sub')
        send_message = types.InlineKeyboardButton("💎Сделать рассылку", callback_data='send_message1')
        usercounts = types.InlineKeyboardButton("💎Статистика", callback_data='usercounts')
        send_database = types.InlineKeyboardButton("💎Отправить базу данных", callback_data='send_database')
        edit_sub = types.InlineKeyboardButton("💎Продлить сабам", callback_data='edit_sub')
        edit_whitelist = types.InlineKeyboardButton("💎Внести в белый лист", callback_data='whitelist_edit')
        markup.add(send_sub, send_message, usercounts, send_database, edit_sub, edit_whitelist)  # Добавляем кнопку в разметку
        with open('had2.jpg', 'rb') as had:
            await message.answer_photo(photo=had, caption='<b>💎 Админ-меню: </b>', reply_markup=markup, parse_mode='HTML')
    else:
        with open('had2.jpg', 'rb') as had:
            await message.answer_photo(photo=had, caption='<b>❌  Я не понимаю вас.</b>', parse_mode='HTML')

@dp.callback_query_handler(text='snoser')
async def snoser(call: CallbackQuery):
    if not check_subscription(call.message.chat.id):
        await bot.send_message(call.message.chat.id, "<b>❌ В доступе отказано! Купите подписку.</b>", parse_mode='HTML')
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    pysto1 = types.InlineKeyboardButton(text="📘 Канал", callback_data="pysto21")
    pysto2 = types.InlineKeyboardButton(text="📘 Бота", callback_data="pysto22")
    pysto3 = types.InlineKeyboardButton(text="📘 Аккаунт", callback_data="pysto23")
    back_button = types.InlineKeyboardButton(text="🏠Главное меню", callback_data="home")
    keyboard.add(pysto1, pysto2, pysto3, back_button)
    
    with open('had2.jpg', 'rb') as photo:
        await bot.send_photo(call.message.chat.id, photo, caption="<b>🦎 Выберите что вы хотели бы снести:</b>", parse_mode='HTML', reply_markup=keyboard)
    
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.callback_query_handler(text='pysto21')
async def pysto21(call: CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    price_list_sn = types.InlineKeyboardButton(text="🦎 Снос канала услуг", callback_data="snos_price")
    price_list_sn2 = types.InlineKeyboardButton(text="🦎 Снос за живодерство", callback_data="snos_price2")
    snos_dox_sn = types.InlineKeyboardButton(text="🦎 Снос за личные данные", callback_data="snos_dox")
    snos_files_sn = types.InlineKeyboardButton(text="🦎 Снос за файлы", callback_data="snos_files")
    snos_swat_sn = types.InlineKeyboardButton(text="🦎 Схемы абуза/мануалы", callback_data="snos_swat")
    snos_narko_sn = types.InlineKeyboardButton(text="🦎 Снос за наркотики", callback_data="snos_narko")
    snos_porno_sn = types.InlineKeyboardButton(text="🦎 Снос за порнографию", callback_data="snos_porno")
    snos_sxemok_sn = types.InlineKeyboardButton(text="🦎 Снос за щитпостинг", callback_data="snos_sxemok")
    back_button = types.InlineKeyboardButton(text="❌ Назад", callback_data="snoser")
    keyboard.add(price_list_sn, price_list_sn2, snos_dox_sn, snos_files_sn, snos_swat_sn, snos_narko_sn, snos_porno_sn, snos_sxemok_sn, back_button)
    
    with open('had2.jpg', 'rb') as photo:
        await bot.send_photo(call.message.chat.id, photo, caption="<b>🦎 Выберите нарушение за которое можно снести канал:</b>", parse_mode='HTML', reply_markup=keyboard)
    
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.callback_query_handler(text='pysto22')
async def pysto22(call: CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    snos_narkobot_sn = types.InlineKeyboardButton(text="🦎 Снос OSINT-бота", callback_data="snos_narkobot")
    snos_doxbot_sn = types.InlineKeyboardButton(text="🦎 Снос за личные данные", callback_data="snos_doxbot")
    back_button = types.InlineKeyboardButton(text="❌Назад", callback_data="snoser")
    keyboard.add(snos_narkobot_sn, snos_doxbot_sn, back_button)
    
    with open('had2.jpg', 'rb') as photo:
        await bot.send_photo(call.message.chat.id, photo, caption="<b>🦎 Выберите нарушение за которое можно снести бота:</b>", parse_mode='HTML', reply_markup=keyboard)
    
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.callback_query_handler(text='pysto23')
async def pysto23(call: CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    snos_virta_sn = types.InlineKeyboardButton(text="🦎 Снос за терроризм", callback_data="snos_virta")
    snos_zapret_sn = types.InlineKeyboardButton(text="🦎 Снос за нарушение закона", callback_data="snos_zapret")
    snos_spam_sn = types.InlineKeyboardButton(text="🦎 Снос за спам", callback_data="snos_spam")
    snos_osk_ugroza_sn = types.InlineKeyboardButton(text="🦎 Снос за насилие", callback_data="snos_osk_ugroza")
    snos_loznau_sn = types.InlineKeyboardButton(text="🦎 Снос за фейк профиль", callback_data="snos_loznau")
    snos_hacker_sn = types.InlineKeyboardButton(text="🦎 Не нравится", callback_data="snos_hacker")
    back_button = types.InlineKeyboardButton(text="❌ Назад", callback_data="snoser")
    keyboard.add(snos_virta_sn, snos_zapret_sn, snos_spam_sn, snos_osk_ugroza_sn, snos_loznau_sn, snos_hacker_sn, back_button)
    
    with open('had2.jpg', 'rb') as photo:
        await bot.send_photo(call.message.chat.id, photo, caption="<b>🦎 Выберите нарушение за которое можно снести аккаунт:</b>", parse_mode='HTML', reply_markup=keyboard)
    
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@dp.callback_query_handler(lambda call: call.data == 'cabinet')
async def cabinet(call: types.CallbackQuery):
    user_id = call.message.chat.id
    status = await check_subscription_status(user_id)  # Добавляем await здесь
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 Приобрести подписку", callback_data="buy_subscription"))
    markup.add(types.InlineKeyboardButton("⚙️ Поддержка", url='https://t.me/TritonBotnetSupport'))
    markup.add(types.InlineKeyboardButton("❌ Назад", callback_data="back"))
    await bot.edit_message_caption(chat_id=user_id, message_id=call.message.message_id, caption=status, reply_markup=markup, parse_mode='HTML')

@dp.callback_query_handler(lambda call: call.data == 'buy_subscription')
async def buy_subscription(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    subscription_options = [
        ("🦎 15 дней - 3,5$", "buy_15"),
        ("🦎 1 месяц - 5$", "buy_30"),
        ("🦎 2 месяца - 8$", "buy_60"),
        ("🦎 3 месяца - 12$", "buy_90"),
        ("🦎 Навсегда - 35$", "buy_lifetime")
    ]
    for option_text, callback_data in subscription_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption="⌛️ Выберите срок подписки:", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def subscription_duration_selected(call: types.CallbackQuery):
    duration = call.data
    markup = types.InlineKeyboardMarkup()
    currency_options = [
        ("💵 USDT", "currency_USDT_" + duration),
        ("💎 TON", "currency_TON_" + duration),
        ("🪙 BTC", "currency_BTC_" + duration),
        ("💶 ETH", "currency_ETH_" + duration)
    ]
    for option_text, callback_data in currency_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption="💸 Выберите валюту для оплаты:", reply_markup=markup)

class MyState(StatesGroup):
    ask_violation_link = State()
    ask_complaints_count = State()
    process_report = State()
    ask_violation_link2 = State()
    ask_complaints_count2 = State()
    process_report2 = State()

@dp.callback_query_handler(lambda call: call.data == 'snos_price')
async def handle_inline_button_click(call: types.CallbackQuery):
    user_id = call.from_user.id
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.send_message(chat_id=user_id, text='<b>🦎 Отправьте ссылку на канал, который вы хотите снести:</b>', parse_mode='HTML')
    await MyState.ask_violation_link.set()

@dp.message_handler(state=MyState.ask_violation_link)
async def ask_violation_link(message: types.Message, state: FSMContext):
    channel_link = message.text
    contains_blacklisted_keyword = any(keyword in channel_link for keyword in blacklisted_channels)
    if contains_blacklisted_keyword:
        await message.answer('<b>❌ Эту ссылку нельзя указывать.\n🦎 Она находится в системе белого листа</b>', parse_mode='HTML')
    else:
        await state.update_data(channel_link=channel_link)
        await message.answer('<b>🦎 Пожалуйста, отправьте ссылку на нарушение:</b>', parse_mode='HTML')
        await MyState.ask_complaints_count.set()

@dp.message_handler(state=MyState.ask_complaints_count)
async def ask_complaints_count(message: types.Message, state: FSMContext):
    violation_link = message.text
    contains_blacklisted_keyword = any(keyword in violation_link for keyword in blacklisted_channels)
    if contains_blacklisted_keyword:
        await message.answer('<b>❌ Эту ссылку нельзя указывать.\n🦎 Она находится в системе белого листа</b>', parse_mode='HTML')
    else:
        await state.update_data(violation_link=violation_link)
        await message.answer('<b>🦎 Пожалуйста, укажите количество аккаунтов для отправки жалоб (максимум 700):</b>', parse_mode='HTML')
        await MyState.process_report.set()
        

@dp.message_handler(state=MyState.process_report)
async def process_report(message: types.Message, state: FSMContext):
    complaints_count = int(message.text)  # Преобразуем текст введенный пользователем в целое число

    data = await state.get_data()
    violation_link = data.get('violation_link')
    channel_link = data.get('channel_link')
    
    body = f'Здравствуйте! в данном телеграмм канале {channel_link} публикуются посты о продаже запрещенных услуг одно из них лжеминирование, а также нахождения информации о человеке, вот доказательства:\n {violation_link} \nПрошу заблокировать данный канал со связью нарушения правил мессенджера. Спасибо за ранее.'
    
    await message.answer('<b>🦎 Жалобы начинают отправляться. Пожалуйста, подождите...</b>', parse_mode='HTML')

    async def send_complaints_async(email_data, complaints_count, body, violation_link, channel_link):
        email, password = email_data.split(':')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        for _ in range(complaints_count):
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = recipient
            msg['Subject'] = f'Нарушение правил, каналом: {channel_link}'
            msg.attach(MIMEText(body, 'plain'))

            try:
                server.login(email, password)
                server.send_message(msg)
            except smtplib.SMTPAuthenticationError:
                print(f'Authentication error for email: {email}')
            
        server.quit()

    tasks = [asyncio.create_task(send_complaints_async(email_data, complaints_count, body, violation_link, channel_link)) for email_data in emails]
    await asyncio.gather(*tasks)

    # Send final message to the user
    final_message = f'<b>🦎 Triton Botnet Log\n\n🦎 Количество жалоб: {complaints_count}\n🦎 Канал: {channel_link}\n🦎 Ответ от сервера: жалобы успешно отправлены\n\n🦎 Канал будет заблокирован через несколько часов.</b>'
    await bot.send_message(message.from_user.id, final_message, parse_mode='HTML')
    
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'snos_price2')
async def handle_inline_button_click(call: types.CallbackQuery):
    user_id = call.from_user.id
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.send_message(chat_id=user_id, text='<b>🦎 Отправьте ссылку на канал, который вы хотите снести:</b>', parse_mode='HTML')
    await MyState.ask_violation_link2.set()

@dp.message_handler(state=MyState.ask_violation_link2)
async def ask_violation_link2(message: types.Message, state: FSMContext):
    channel_link = message.text
    contains_blacklisted_keyword = any(keyword in channel_link for keyword in blacklisted_channels)
    if contains_blacklisted_keyword:
        await message.answer('<b>❌ Эту ссылку нельзя указывать.\n🦎 Она находится в системе белого листа</b>', parse_mode='HTML')
    else:
        await state.update_data(channel_link=channel_link)
        await message.answer('<b>🦎 Пожалуйста, отправьте ссылку на нарушение:</b>', parse_mode='HTML')
        await MyState.ask_complaints_count2.set()

@dp.message_handler(state=MyState.ask_complaints_count2)
async def ask_complaints_count2(message: types.Message, state: FSMContext):
    violation_link = message.text
    contains_blacklisted_keyword = any(keyword in violation_link for keyword in blacklisted_channels)
    if contains_blacklisted_keyword:
        await message.answer('<b>❌ Эту ссылку нельзя указывать.\n🦎 Она находится в системе белого листа</b>', parse_mode='HTML')
    else:
        await state.update_data(violation_link=violation_link)
        await message.answer('<b>🦎 Пожалуйста, укажите количество аккаунтов для отправки жалоб (максимум 700):</b>', parse_mode='HTML')
        await MyState.process_report2.set()
        
@dp.message_handler(state=MyState.process_report2)
async def process_report2(message: types.Message, state: FSMContext):
    complaints_count = int(message.text) # Преобразуем текст введенный пользователем в целое число
    data = await state.get_data()
    violation_link = data.get('violation_link')
    channel_link = data.get('channel_link')

    body = f'Здравствуйте! В данном канале - {channel_link} Размещена продажа деанонимизации, и лжеминирования от лица другого человека. Это нарушает правила! Так же там размещено много чего не законного! Посмотреть на эти нарушения вы можете посмотреть по этой ссылке - {violation_link} , и убедиться что, размещённое сообщение в данном канале, полностью нарушает правила Telegram. Я требую чтобы вы с этим разобрались! Спасибо за ранее!'

    await message.answer('<b>🦎 Жалобы начинают отправляться. Пожалуйста, подождите...</b>', parse_mode='HTML')

    async def send_complaints_async2(email_data, complaints_count, body, violation_link, channel_link):
        email, password = email_data.split(':')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        for _ in range(complaints_count):
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = recipient
            msg['Subject'] = f'Нарушение правил, каналом: {channel_link}'
            msg.attach(MIMEText(body, 'plain'))

            try:
                server.login(email, password)
                server.send_message(msg)
            except smtplib.SMTPAuthenticationError:
                print(f'Authentication error for email: {email}')

            await asyncio.sleep(0)  # Освобождаем основной поток выполнения

        server.quit()

    tasks = [asyncio.create_task(send_complaints_async2(email_data, complaints_count, body, violation_link, channel_link)) for email_data in emails]
    await asyncio.gather(*tasks)

    # Send final message to the user
    final_message = f'<b>🦎 Triton Botnet Log\n=============================\n🦎 Количество жалоб: {complaints_count}\n🦎 Канал: {channel_link}\n🦎 Ответ от сервера: жалобы успешно отправлены\n\nКанал будет заблокирован через несколько часов.</b>'
    await bot.send_message(message.from_user.id, final_message, parse_mode='HTML')

    await state.finish()












































@dp.callback_query_handler(lambda call: call.data.startswith('currency_'))
async def currency_selected(call: types.CallbackQuery):
    parts = call.data.split('_')
    currency = parts[1]
    duration_parts = parts[2:]
    duration = "_".join(duration_parts)

    amount = get_amount_by_duration(duration.replace('buy_', ''))
    
    try:
        print(amount, currency)
        converted_amount = convert_to_crypto(amount, currency)
        payment_link, invoice_id = generate_payment_link(currency, converted_amount)
        if payment_link and invoice_id:
            markup = types.InlineKeyboardMarkup()
            check_payment_button = types.InlineKeyboardButton("💸 Проверить оплату", callback_data=f"check_payment:{call.from_user.id}:{invoice_id}")
            markup.add(check_payment_button)
            
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption=f"💸 Счет для оплаты:\n{payment_link}", reply_markup=markup)
        else:
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="❌ Не удалось создать счет для оплаты. Пожалуйста, попробуйте позже.")
    except ValueError as e:
        await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              caption=str(e))

def get_amount_by_duration(duration):
    prices = {
        '7': 1,
        '15': 3.5,
        '30': 5,
        '60': 8,
        '90': 12,
        'lifetime': 35
    }
    return prices.get(duration, 0)

@dp.callback_query_handler(lambda call: call.data.startswith('check_payment:'))
async def check_payment(call: types.CallbackQuery):
    _, user_id_str, invoice_id_str = call.data.split(':')
    user_id = int(user_id_str)
    invoice_id = invoice_id_str

    if user_id == call.from_user.id:
        status, payment_link, amount = get_invoice_status(invoice_id)
        
        if status == "paid":
            duration_days = get_duration_by_amount(amount)
            expiration_date = datetime.now() + timedelta(days=duration_days)
            add_subscription(user_id, expiration_date)

            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="✅ Оплата подтверждена. Подписка активирована. Спасибо за покупку.")
        else:
            await bot.answer_callback_query(call.id, "❌ Оплата не найдена. Пожалуйста, проверьте позже или свяжитесь с поддержкой.")
    else:
        await bot.answer_callback_query(call.id, "❌ Вы не можете проверить эту оплату.", show_alert=True)

def get_duration_by_amount(amount):
    amount = round(amount, 2)
    if amount <= 1:
        return 7
    elif amount <= 2:
        return 15
    elif amount <= 3:
        return 30
    elif amount <= 6:
        return 60
    elif amount <= 9:
        return 90
    elif amount >= 20:
        return 365 * 99
    else:
        return 0

@dp.callback_query_handler(lambda call: True)
async def handle_inline_button_click(call: types.CallbackQuery):
    user_id = call.message.chat.id
    if call.data == 'send_sub':
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=call.message.message_id,
            caption='<b>✍ Укажите ID пользователя и кол-во дней через пробел:</b>',
            parse_mode='HTML'
        )
        await GiveSubState.WaitingForUserData.set()
    elif call.data == 'my_sub':
        with open('had2.jpg', 'rb') as had:
            await bot.send_photo(user_id, had, await check_subscription_status(user_id), reply_markup=del_markup, parse_mode='HTML')
    elif call.data == 'del':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await dp.storage.reset_data(chat=call.message.chat.id)
    elif call.data == 'back':
        await home(call.message)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == 'send_message1':
	    state = dp.get_current().data.get("state")
	    if state is None:
	        state = dp.current_state(chat=call.message.chat.id, user=call.from_user.id)
	    await send_message2(call, state)
    elif call.data == 'usercounts':
        total_users, subscribed_users = await get_user_counts()
        await bot.send_message(user_id, f'<b>🦎 Triton Botnet\n🦎 Количество пользователей: {total_users}\n🦎 Пользователи с подпиской: {subscribed_users}</b>', parse_mode='HTML')
    elif call.data == 'home':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await home(call.message)

async def check_user(user_id):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
    existing_user = cursor.fetchone()

    if existing_user:
        return True
    else:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id, ))
        conn.commit()
        await bot.send_message(
            log_chat_id,
            f'<b>🦎 Зарегистрирован новый <a href="tg://openmessage?user_id={user_id}">пользователь</a></b>\nID: <code>{user_id}</code>',
            parse_mode='HTML'
        )
        return False

    conn.close()

async def check_subscription_status(user_id):
    async with aiosqlite.connect('database2.db') as conn:
        cursor = await conn.cursor()

        await cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                            (user_id, ))
        subscription = await cursor.fetchone()

        if subscription:
            expiration_date = subscription[0]
            date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
            current_date = datetime.now()

            if current_date <= date:
                days_left = (date - current_date).days
                status = f"<b>🦎 Triton Botnet\n\n📘 У вас присутствует активная подписка\n📘 У вас осталось {days_left} дней\n\n🆔 Ваш ID: {user_id}\n\n⚙️ Админ: @TritonBotnetSupport \n💙 Наш канал: @TritonBotnet\n💙 Приятного пользования</b>"
            else:
                status = f"<b>🦎 Triton Botner\n\n📘 У вас истекла подписка.\n\n🆔 ВашID: {user_id}\n\n⚙️ Админ: @TritonBotnetSupport \n💙 Наш канал: @TritonBotnet\n💙 Приятного пользования </b>"
        else:
            status = f"<b>🦎 Triton Botnet\n\n📘 У вас отсутствует подписка.\n\n🆔 Ваш ID: {user_id}\n\n⚙️ Админ: @TritonBotnetSupport \n💙 Наш канал: @TritonBotnet\n💙 Приятного пользования </b>"

    return status

class GiveSubState(StatesGroup):
    WaitingForUserData = State()

@dp.callback_query_handler(lambda call: call.data == 'give_sub')
async def handle_inline_button_click(call: types.CallbackQuery):
    await call.message.answer("Введите данные для выдачи подписки в формате: <b>user_id days</b>", parse_mode='HTML')
    await GiveSubState.WaitingForUserData.set()

@dp.message_handler(state=GiveSubState.WaitingForUserData)
async def process_subscription_data(message: types.Message, state: FSMContext):
    if message.text:
        data = message.text.split(' ')
        expiration_date = datetime.now() + timedelta(days=int(data[1]))
        add_subscription(data[0], expiration_date)
        
        await message.answer(f"<b>✅ Вам выдана подписка на {data[1]} дней.\n✅ Пропишите /start чтобы подписка была активирована</b>", parse_mode='HTML')
        
        await state.finish()
    else:
        pass

def add_subscription(user_id, expiration_date):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute(
      "INSERT OR REPLACE INTO subscriptions (user_id, expiration_date) VALUES (?, ?)",
      (user_id, expiration_date))
  conn.commit()
  conn.close()

class SendMessageState(StatesGroup):
    WaitingForMessage = State()

@dp.callback_query_handler(lambda call: call.data == 'send_message2')
async def send_message2(call: types.CallbackQuery, state: FSMContext):
    if state is None:
        state = dp.current_state(chat=call.message.chat.id, user=call.from_user.id)
        
    user_id = call.message.chat.id
    sent_message = await bot.send_message(user_id, "💎 Введите сообщение для отправки пользователям:")
    
    await state.set_state(SendMessageState.WaitingForMessage)
    await state.update_data(user_id=user_id, sent_message_id=sent_message.message_id)

async def send_message_to_users(text):
    # Подключение к базе данных
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    # Получение всех user_id из базы данных
    cursor.execute('SELECT user_id FROM users')
    rows = cursor.fetchall()
    
    # Рассылка сообщений каждому user_id
    for row in rows:
        user_id = row[0]
        try:
            await bot.send_message(user_id, text)
        except aiogram.utils.exceptions.BotBlocked as e:
            print(f'Пользователь с айди {user_id} заблокировал бота. Сообщение не отправлено.')
    
    # Закрытие соединения с базой данных
    conn.close()

@dp.message_handler(state=SendMessageState.WaitingForMessage)
async def process_sent_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data['user_id']
        sent_message_id = data['sent_message_id']
    
    text = message.text
    await send_message_to_users(text)
    await bot.delete_message(user_id, sent_message_id)
    await message.reply('💎 Сообщение отправлено пользователям.')
    await state.finish()

class EditSubscriptionState(StatesGroup):
    WaitingForDuration = State()
    WaitingForCustomDuration = State()

async def send_database_callback(call: types.CallbackQuery):
    with open('database2.db', 'rb') as db_file:
        await bot.send_document(call.message.chat.id, db_file)

async def send_subscription_callback(call: types.CallbackQuery):
    msg = await bot.send_message(call.message.chat.id, "На сколько дней продлить подписки? (Введите число)")
    await state.set_state(EditSubscriptionState.WaitingForDuration)
    await state.update_data(message_id=msg.message_id)

@dp.message_handler(state=EditSubscriptionState.WaitingForDuration)
async def process_subscription_duration_step(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    duration = 1

    if message.text == 'Другое количество дней':
        msg = await bot.send_message(chat_id, "Введите количество дней для продления подписок:")
        await state.set_state(EditSubscriptionState.WaitingForCustomDuration)
        await state.update_data(message_id=msg.message_id)
    else:
        if message.text == '3 дня':
            duration = 3
        elif message.text == '7 дней':
            duration = 7

        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, expiration_date FROM subscriptions WHERE expiration_date > datetime("now")')
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            current_expiration_date = datetime.strptime(user[1], '%Y-%m-%d %H:%M:%S.%f')
            new_expiration_date = current_expiration_date + timedelta(days=duration)
            cursor.execute('UPDATE subscriptions SET expiration_date = ? WHERE user_id = ?', (new_expiration_date, user_id))

        await bot.send_message(chat_id, f"🦎 Подписки успешно продлены на {duration} дней")

        conn.commit()
        conn.close()

@dp.message_handler(state=EditSubscriptionState.WaitingForCustomDuration)
async def process_custom_subscription_duration_step(message: types.Message, state: FSMContext):
    chat_id = message.chat.id

    try:
        duration = int(message.text)

        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()

        cursor.execute('SELECT user_id, expiration_date FROM subscriptions WHERE expiration_date > datetime("now")')
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            current_expiration_date = datetime.strptime(user[1], '%Y-%m-%d %H:%M:%S')
            new_expiration_date = current_expiration_date + timedelta(days=duration)
            cursor.execute('UPDATE subscriptions SET expiration_date = ? WHERE user_id = ?', (new_expiration_date, user_id))

        await bot.send_message(chat_id, f"🦎 Подписки успешно продлены на {duration} дней")

        conn.commit()
        conn.close()
    except ValueError:
        await bot.send_message(chat_id, "Пожалуйста, введите число")
































async def get_user_counts():
    # Create a new connection and cursor within the function
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Get total user count
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    # Get subscribed user count
    cursor.execute('SELECT COUNT(*) FROM subscriptions')
    subscribed_users = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    return total_users, subscribed_users

async def send_log(log_text):
    await asyncio.sleep(5)
    await bot.send_message(log_chat_id, log_text)

if __name__ == '__main__':
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)