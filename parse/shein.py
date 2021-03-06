import asyncio
import json
import re
from random import randint

import aiohttp
from bs4 import BeautifulSoup

connector = {
    "values": {
        "colors": {
            "white": "White",
            "black": "Black",
            "red": "Red",
            "green": "Green"
        }
    },
    "ids": {
        "colors": {
            "black": "27_112",
            "white": "27_103-27_739",
            "red": "27_144-27_544",
            "green": "27_81-27_334-27_1000"
        }
    },
    "price": {
        "3K": 3000,
        "5K": 5000,
        "10K": 10000,
        ">10K": ""
    }

}


async def get_image(url, session):
    async with session.get(url=url) as response:
        text = await response.text()
    bs = BeautifulSoup(text, "lxml")
    find = bs.find("script", text=re.compile("window.goodsDetailv2SsrData"))
    start = find.text.index('origin_image":"//')
    result = find.text[start+len('origin_image":"//'):start+150]
    result = result[:result.index('"')]
    return "https://"+result


async def page(params, session):
    color_val = connector["values"]["colors"][params["colors"]]
    color_ids = connector["ids"]["colors"][params["colors"]]
    price = connector["price"][params["price"]]

    blank = f'https://ru.shein.com/Men-Backpacks-c-2126.html?attr_values={color_val}&attr_ids={color_ids}&max_price={price}&exc_attr_id={randint(20, 2000)}'

    async with session.get(url=blank, headers={}, timeout=5) as response:
        bs = BeautifulSoup(await response.text(), 'lxml')

    find = bs.find("script", text=re.compile("gbCommonInfo.pageType = 'goodsList'")).text
    find = find[find.index('{'):]
    find = json.loads(find)["results"]["goods"]
    result = []
    for elem in find:
        result += [{
            "name": elem['goods_name'].capitalize(),
            "photo": elem['goods_img'][2:],
            "link": "https://ru.shein.com" + elem['pretreatInfo']['goodsDetailUrl']
        }]
    return result


async def parser(params):
    tasks = []
    if params["types"] == {"turist"}:
        return []
    if not params['colors']:
        params['colors'] = {"red", "black", "white", "green"}
    if not params['types']:
        params['types'] = {"gorod", "turist"}
    if not params['price']:
        params['price'] = '>10K'
    async with aiohttp.ClientSession() as session:
        for color in params["colors"]:
            loop_params = {}
            for key in params.keys():
                loop_params[key] = params[key]

            loop_params["colors"] = color
            tasks += [asyncio.ensure_future(page(loop_params, session))]

        result = []
        for elem in await asyncio.gather(*tasks):
            for item in elem:
                result += [item]
    return result
