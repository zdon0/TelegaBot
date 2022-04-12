import asyncio
import json
import logging
from random import shuffle

import aiohttp
import nest_asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.exceptions import RetryAfter

import chat
import markups
import shein
import sportmaster

logging.basicConfig(level=logging.INFO)
with open('token', 'r') as file:
    bot = Bot(token=file.readline().strip())
dp = Dispatcher(bot)

don_id = 453_998_679
kamol_id = 786_806_009
colors = {'red', 'black', 'white', 'green'}
chars = {'gorod', 'turist'}
volumes_1 = {'10_ot', '15_ot', '20_ot'}
volumes_2 = {'15_do', '20_do', '25_do', '>25'}
prices = {'3K', '5K', '10K', '>10K'}

try:
    with open('database.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for key in list(data.keys()):
        data[int(key)] = dict(**data[key])
        data.pop(key)
        for backfilter in ["colors", "types"]:
            data[int(key)]["filters"][backfilter] = set(data[int(key)]["filters"][backfilter])
        for i in range(len(data[int(key)]["like"])):
            data[int(key)]["like"][i] = tuple(data[int(key)]["like"][i])

        data[int(key)]["like"] = set(data[int(key)]["like"])

except:
    data = dict()

colors_markup = markups.colors1()
types_markup = markups.types1()
volumeFrom_markup = markups.volume1()
volumeTo_markup = markups.volume2()
price_markup = markups.price1()
like_markup = markups.like()
dislike_markup = markups.dislike()
reply_markup = markups.reply_keyboard()

markups = [colors_markup, types_markup, volumeFrom_markup, volumeTo_markup, price_markup]
texts = ['Выберите цвет', 'Выберите тип рюкзака', 'Объем в литрах', 'Объем в литрах', 'Выберите цену']


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(text='Вас приветствует MIKA Bot!', reply_markup=reply_markup)
    data[message.chat.id] = {
        "ans": None,
        "name": message.chat.full_name,
        "link": message.chat.username,
        "i": 0,
        "filters": {'colors': set(), 'types': set(), 'volume_1': set(), 'volume_2': set(), 'price': set()},
        "stop": False,
        "like": set()
    }


@dp.message_handler(commands='stop')
async def stop(message):
    data[message.chat.id]["stop"] = True


@dp.message_handler(commands='help')
async def help(message):
    await message.answer(text=
                         "Справка:\n" \
                         "1)Чтобы добавить рюкзак в список желаний, нажмите на кнопку с красным сердцем под нужным рюкзаком\n" \
                         "2)Чтобы очистить список желаний, нажмите на пункт /clear в левом нижнем меню или пропишите /clear в чат\n" \
                         "3)Чтобы остановить процесс поиска, нажмите на пункт /stop в левом нижнем меню или пропишите /stop в чат")


@dp.message_handler(commands='clear')
async def clear(message: types.Message):
    data[message.chat.id]['like'].clear()
    await message.answer(text="Список очищен")


@dp.message_handler(content_types='text', text="Парсер рюкзака")
async def backpack(message: types.Message):
    await message.answer(text='Выберите цвет', reply_markup=colors_markup)
    ans = await message.answer(text=f'Цвет: \nТип: \nОбъем ОТ: \nОбъем ДО: \nЦена: ')
    data[message.chat.id]["ans"] = ans
    data[message.chat.id]['i'] = 0
    data[message.chat.id]["stop"] = False
    await chat.changer(data[message.chat.id]["ans"], data[message.chat.id]["filters"])


@dp.message_handler(content_types='text', text="Список желаний")
async def show_like(message: types.Message):
    if len(data[message.chat.id]["like"]) == 0:
        await message.answer(text="Список пуст")
        return
    loop = asyncio.get_event_loop()
    ans = await message.answer(text="Загрузка")
    waiter = loop.create_task(chat.waiter(ans, text="Загрузка"))

    bags = list(data[message.chat.id]["like"])
    sportmaster_bags = list(filter(lambda x: "sport" in x[0], bags))
    shein_bags = list(filter(lambda x: "shein" in x[0], bags))

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.ensure_future(sportmaster.get_image(bag[0], session)) for bag in sportmaster_bags]
        tasks += [asyncio.ensure_future(shein.get_image(bag[0], session)) for bag in shein_bags]
        result = loop.run_until_complete(asyncio.gather(*tasks))

    waiter.cancel()
    await ans.delete()
    for i in range(len(bags)):
        elem = bags[i]
        image_link = result[i]
        try:
            await message.answer_photo(photo=image_link, caption=f"[{elem[1]}]({elem[0]})",
                                       parse_mode="Markdown", disable_notification=True, reply_markup=dislike_markup)
        except RetryAfter as error:
            await asyncio.sleep(error.timeout)
            await message.answer_photo(photo=image_link, caption=f"[{elem[1]}]({elem[0]})",
                                       parse_mode="Markdown", disable_notification=True, reply_markup=dislike_markup)
        except:
            continue
        finally:
            await asyncio.sleep(.1)


@dp.message_handler(content_types='text')
async def not_ready(message: types.Message):
    print(f"{message.from_user.full_name}: {message.text}")
    await message.reply(text="Всему свое время")


@dp.callback_query_handler(lambda call: call.data in colors)
async def call_handler_colors(call: types.CallbackQuery):
    if call.data in data[call.from_user.id]['filters']['colors']:
        data[call.from_user.id]['filters']['colors'].remove(call.data)
    else:
        data[call.from_user.id]['filters']['colors'].add(call.data)

    await chat.changer(data[call.from_user.id]["ans"], data[call.from_user.id]["filters"])


@dp.callback_query_handler(lambda call: call.data in chars)
async def call_handler_chars(call: types.CallbackQuery):
    if call.data in data[call.from_user.id]['filters']['types']:
        data[call.from_user.id]['filters']['types'].remove(call.data)
    else:
        data[call.from_user.id]['filters']['types'].add(call.data)

    await chat.changer(data[call.from_user.id]["ans"], data[call.from_user.id]["filters"])


@dp.callback_query_handler(lambda call: call.data in volumes_1)
async def call_handler_volumes1(call: types.CallbackQuery):
    if data[call.from_user.id]['filters']['volume_1'] == call.data:
        data[call.from_user.id]['filters']['volume_1'] = set()
    else:
        data[call.from_user.id]['filters']['volume_1'] = call.data

    await chat.changer(data[call.from_user.id]["ans"], data[call.from_user.id]["filters"])


@dp.callback_query_handler(lambda call: call.data in volumes_2)
async def call_handler_volumes2(call: types.CallbackQuery):
    if data[call.from_user.id]['filters']['volume_2'] == call.data:
        data[call.from_user.id]['filters']['volume_2'] = set()
    else:
        data[call.from_user.id]['filters']['volume_2'] = call.data

    await chat.changer(data[call.from_user.id]["ans"], data[call.from_user.id]["filters"])


@dp.callback_query_handler(lambda call: call.data in prices)
async def call_handler_prices(call: types.CallbackQuery):
    if data[call.from_user.id]['filters']['price'] == call.data:
        data[call.from_user.id]['filters']['price'] = set()
    else:
        data[call.from_user.id]['filters']['price'] = call.data

    await chat.changer(data[call.from_user.id]["ans"], data[call.from_user.id]["filters"])


@dp.callback_query_handler(lambda call: call.data == "next")
async def call_handler_next(call: types.CallbackQuery):
    await call.message.edit_text(text=texts[data[call.from_user.id]['i'] + 1],
                                 reply_markup=markups[data[call.from_user.id]['i'] + 1])
    data[call.from_user.id]['i'] += 1


@dp.callback_query_handler(lambda call: call.data == "back")
async def call_handler_back(call: types.CallbackQuery):
    await call.message.edit_text(text=texts[data[call.from_user.id]['i'] - 1],
                                 reply_markup=markups[data[call.from_user.id]['i'] - 1])
    data[call.from_user.id]['i'] -= 1


@dp.callback_query_handler(lambda call: call.data == "parse")
async def call_handler_parse(call: types.CallbackQuery):
    loop = asyncio.get_event_loop()
    waiter = loop.create_task(chat.waiter(call.message))

    filters = dict()
    for key in data[call.from_user.id]["filters"].keys():
        filters[key] = data[call.from_user.id]["filters"][key]

    if not filters["colors"]:
        filters["colors"] = colors
    if not filters["types"]:
        filters["types"] = chars
    if not filters["volume_1"]:
        filters["volume_1"] = "10_ot"
    if not filters["volume_2"]:
        filters["volume_2"] = ">25"
    if not filters["price"]:
        filters["price"] = ">10K"

    if filters != data[call.from_user.id]["filters"]:
        await chat.changer(data[call.from_user.id]['ans'], filters)

    tasks = [asyncio.ensure_future(f) for f in [sportmaster.parser(loop, filters),
                                                shein.parser(loop, filters)]]

    result = []
    for elem in loop.run_until_complete(asyncio.gather(*tasks)):
        for item in elem:
            result.append(item)
    shuffle(result)
    waiter.cancel()
    await call.message.delete()
    for elem in result:
        if data[call.message.chat.id]["stop"]:
            break
        try:
            await call.message.answer_photo(photo=elem["photo"], caption=f"[{elem['name']}]({elem['link']})",
                                            parse_mode="Markdown", disable_notification=True,
                                            reply_markup=like_markup
                                            if tuple([elem['link'], elem['name']])
                                               not in data[call.message.chat.id]["like"]
                                            else dislike_markup)
        except RetryAfter as error:
            await asyncio.sleep(error.timeout)
            await call.message.answer_photo(photo=elem["photo"], caption=f"[{elem['name']}]({elem['link']})",
                                            parse_mode="Markdown", disable_notification=True,
                                            reply_markup=like_markup
                                            if tuple([elem['link'], elem['name']])
                                               not in data[call.message.chat.id]["like"]
                                            else dislike_markup)
        except:
            pass
        finally:
            await asyncio.sleep(.1)
    await data[call.from_user.id]["ans"].reply(text="Поиск завершен")
    data[call.message.chat.id]["stop"] = False


@dp.callback_query_handler(lambda call: call.data == "like")
async def call_handler_like(call: types.CallbackQuery):
    link = call.message['caption_entities'][0]["url"]
    name = call.message['caption']
    data[call.from_user.id]["like"].add(tuple([link, name]))
    await call.message.edit_reply_markup(reply_markup=dislike_markup)


@dp.callback_query_handler(lambda call: call.data == "dislike")
async def call_handler_dislike(call: types.CallbackQuery):
    link = call.message['caption_entities'][0]["url"]
    name = call.message.values["caption"]
    try:
        data[call.from_user.id]["like"].remove(tuple([link, name]))
    except KeyError:
        pass
    finally:
        await call.message.edit_reply_markup(reply_markup=like_markup)


def main():
    nest_asyncio.apply()
    executor.start_polling(dp)
    for key in data.keys():
        data[key]['ans'] = None
    with open('database.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=lambda x: list(x))
    # asyncio.run(bot.send_document(chat_id=-1001745130102, document=types.InputFile("./database.json")))


if __name__ == '__main__':
    main()
