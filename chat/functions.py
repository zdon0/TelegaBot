import asyncio

from aiogram.utils import emoji


async def waiter(ans, text="Поиск"):
    c = 1
    while True:
        s = '.' * c
        await ans.edit_text(text=f'{text}{s}')
        await asyncio.sleep(.5)
        c = (c + 1) % 4


async def changer(ans, filters):

    connector = {
        "colors": {
            "red": emoji.emojize(":red_circle:"),
            "black": emoji.emojize(":black_circle:"),
            "white": emoji.emojize(":white_circle:"),
            "green": emoji.emojize(":green_circle:")
        },
        "volumes_1": {"10_ot": "10", "15_ot": "15", "20_ot": "20"},
        "volumes_2": {"15_do": "15", "20_do": "20", "25_do": "25", ">25": "Без ограничений"},
        "chars": {"gorod": "Городской" + emoji.emojize(":cityscape:"),
                  "turist": "Туристический" + emoji.emojize(":national_park:")},
        "prices": {"3K": "3.000", "5K": "5.000", "10K": "10.000", ">10K": "Без ограничений"},
    }

    await ans.edit_text(
        text=f'Цвет: {"".join(list(map(lambda x: connector["colors"][x], filters["colors"])))}' \
             f'\nТип: {", ".join(list(map(lambda x: connector["chars"][x], filters["types"])))}' \
             f'\nОбъем ОТ: {connector["volumes_1"][filters["volume_1"]] if filters["volume_1"] else " "}' \
             f'\nОбъем ДО: {connector["volumes_2"][filters["volume_2"]] if filters["volume_2"] else " "}' \
             f'\nЦена: {connector["prices"][filters["price"]] if filters["price"] else " "}')
