from aiogram import types
from aiogram.utils import emoji


back_button = types.InlineKeyboardButton(text='next➡', callback_data='next')
next_button = types.InlineKeyboardButton(text='⬅back', callback_data='back')

ways = [next_button, back_button]


def reply_keyboard():
    button = types.KeyboardButton(text='Парсер рюкзака')
    like_button = types.KeyboardButton(text='Список желаний')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(button)
    markup.add(like_button)
    return markup


def volume1():
    buttons = [
        types.InlineKeyboardButton(text='От 10', callback_data='10_ot'),
        types.InlineKeyboardButton(text='От 15', callback_data='15_ot'),
        types.InlineKeyboardButton(text='От 20', callback_data='20_ot')
    ]
    volume_1_keyboard = types.InlineKeyboardMarkup()
    volume_1_keyboard.add(*buttons)
    volume_1_keyboard.add(*ways)
    return volume_1_keyboard


def volume2():
    buttons = [
        types.InlineKeyboardButton(text='До 15', callback_data='15_do'),
        types.InlineKeyboardButton(text='До 20', callback_data='20_do'),
        types.InlineKeyboardButton(text='До 25', callback_data='25_do'),
    ]
    inf = types.InlineKeyboardButton(text='Без ограничений', callback_data='>25')
    volume_2_keyboard = types.InlineKeyboardMarkup()
    volume_2_keyboard.add(*buttons)
    volume_2_keyboard.add(inf)
    volume_2_keyboard.add(*ways)
    return volume_2_keyboard


def types1():
    buttons = [
        types.InlineKeyboardButton(text='Городской' + emoji.emojize(":cityscape:"), callback_data='gorod'),
        types.InlineKeyboardButton(text='Туристический' + emoji.emojize(":national_park:"), callback_data='turist')
    ]
    types_keyboard = types.InlineKeyboardMarkup()
    types_keyboard.add(*buttons)
    types_keyboard.add(*ways)
    return types_keyboard


def colors1():
    buttons_1 = [
        types.InlineKeyboardButton(text='Черный' + emoji.emojize(":black_circle:"), callback_data='black'),
        types.InlineKeyboardButton(text='Белый' + emoji.emojize(":white_circle:"), callback_data='white')
    ]
    buttons_2 = [
        types.InlineKeyboardButton(text='Зелёный' + emoji.emojize(":green_circle:"), callback_data='green'),
        types.InlineKeyboardButton(text='Красный' + emoji.emojize(":red_circle:"), callback_data='red')
    ]
    colors_keyboard = types.InlineKeyboardMarkup()
    colors_keyboard.add(*buttons_1)
    colors_keyboard.add(*buttons_2)
    colors_keyboard.add(back_button)
    return colors_keyboard


def price1():
    pars = types.InlineKeyboardButton(text='Поиск', callback_data='parse')

    buttons = [
        types.InlineKeyboardButton(text='До 3.000', callback_data='3K'),
        types.InlineKeyboardButton(text='До 5.000', callback_data='5K'),
        types.InlineKeyboardButton(text='До 10.000', callback_data='10K'),
        types.InlineKeyboardButton(text='Без ограничений', callback_data='>10K')
    ]
    price_keyboard = types.InlineKeyboardMarkup()
    price_keyboard.add(*buttons)
    price_keyboard.add(next_button, pars)
    return price_keyboard


def like():
    button = types.InlineKeyboardButton(text=emoji.emojize(":red_heart:"), callback_data='like')
    like_keyboard = types.InlineKeyboardMarkup()
    like_keyboard.add(button)
    return like_keyboard


def dislike():
    button = types.InlineKeyboardButton(text=emoji.emojize(":broken_heart:"), callback_data='dislike')
    dislike_keyboard = types.InlineKeyboardMarkup()
    dislike_keyboard.add(button)
    return dislike_keyboard
