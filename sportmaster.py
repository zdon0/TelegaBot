import re
import json
from bs4 import BeautifulSoup
import aiohttp
import asyncio


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36 OPR/84.0.4316.31'}

connector = {
    "colors": {
        "red": "color_krasnyi",
        "black": "color_chernyi",
        "white": "color_bezhevyi",
        "green": "color_zelenyi"
    },
    "types": {
        "gorod": "ware_subgrp_ryukzaki_malye,ware_subgrp_ryukzaki_srednie,ware_subgrp_ryukzaki_bolshie",
        "turist": "ware_subgrp_gornye_pokhody,ware_subgrp_mnogodnevnye_pokhody,ware_subgrp_odnodnevnye_pokhody"
    }
}

connector2 = {
    "volume1": {
        "10_ot": 10,
        "15_ot": 15,
        "20_ot": 20
    },
    "volume2": {
        "15_do": 15,
        "20_do": 20,
        "25_do": 25,
        ">25": ""
    },
    "price": {
        "3K": 3000,
        "5K": 5000,
        "10K": 10000,
        ">10K": ""
    }
}


async def get_image(url, session):
    async with session.get(url=url, headers=headers) as response:
        text = await response.text()

    bs = BeautifulSoup(text, 'lxml')
    find = bs.find("img", class_="swiper-lazy sm-image")
    link = find.get("data-src")
    return link


async def page(params, session):
    # print("start:", params["colors"], params["types"])
    volume_from = connector2["volume1"][params["volume_1"]]
    volume_to = connector2["volume2"][params["volume_2"]]
    price_to = connector2["price"][params["price"]]
    color = connector["colors"][params["colors"]]
    type = connector["types"][params["types"]]
    result = []

    blank = f"https://www.sportmaster.ru/catalog/aksessuary/ryukzaki_i_sumki/ryukzaki/?f-id_ware_subgrp={type}" \
            f"&f-volumefrom={volume_from}&f-volumeto={volume_to}" \
            f"&f-priceto={price_to}&f-clr={color}&sortType=BY_POPULARITY"
    # print(blank)
    async with session.get(url=blank, headers=headers) as response:
        # print("connect:", params["colors"], params["types"])
        text = await response.text()

    bs = BeautifulSoup(text, 'lxml')
    find = bs.find('script', text=re.compile('searchResult')).text.replace(r'\u002F', r'/')
    find = find[find.index('{'):find.index(";(function(){var s;(s=document.currentScript")]
    find = json.loads(find)['searchResult']['products']
    # print("process:", params["colors"], params["types"])

    for elem in find:
        name = elem['name']
        link = "https://www.sportmaster.ru" + elem['variants'][0]['url']
        photo = elem['image']

        result += [{
            "name": name,
            "link": link,
            "photo": photo
        }]
    return result


async def parser(loop, params):
    tasks = []
    if not params['colors']:
        params['colors'] = {"red", "black", "white", "green"}
    if not params['types']:
        params['types'] = {"gorod", "turist"}
    if not params['volume_1']:
        params['volume_1'] = '10_ot'
    if not params['volume_2']:
        params['volume_2'] = '>25'
    if not params['price']:
        params['price'] = '>10K'

    async with aiohttp.ClientSession() as session:
        for color in params["colors"]:
            for type in params["types"]:
                loop_params = {}
                for key in params.keys():
                    loop_params[key] = params[key]
                loop_params["colors"] = color
                loop_params["types"] = type
                tasks += [asyncio.ensure_future(page(loop_params, session))]

        result = []
        for elem in loop.run_until_complete(asyncio.gather(*tasks)):
            for item in elem:
                result += [item]
    return result
