import json
import shutil
import sqlite3
from os import path

from bs4 import BeautifulSoup
from requests_cache import CachedSession

conn = sqlite3.connect('database.db')

session = CachedSession()

base_url = "https://www.wixosstcg.eu"
query = "/Carddb?nomecarta=&cerca=true&ordina=cardid&page=%s"

database = {}

# Hardcoded range because lazy
i = 1
while True:
    req = session.get(base_url + query % i)
    soup = BeautifulSoup(req.content, 'html.parser')
    cards = soup.find('div', class_='risultati')
    if not cards:
        break
    for card in cards.find_all('a', class_='preview'):
        href = card['href']
        cardreq = session.get(base_url + href)
        cardsoup = BeautifulSoup(cardreq.content, 'html.parser')
        container = cardsoup.find('main', id='main-content')
        img_href = container.find('img')['src']
        cardid = img_href.split('/')[2]
        img_path = f'images/{cardid}.png'

        # Download img
        if not path.exists(img_path):
            img_res = session.get(base_url + img_href, stream=True)
            with open(img_path, 'wb') as out_file:
                shutil.copyfileobj(img_res.raw, out_file)

        # Write cardinfo to db
        cardinfo = container.find(
            'div', class_='col-md-6 padding-top-30').find_all('div')
        database[cardid] = {}
        for key, value in zip(cardinfo[0::2], cardinfo[1::2]):
            stripped_key = key.get_text().strip()
            stripped_value = value.get_text().strip()
            database[cardid][stripped_key] = stripped_value
    i += 1

with open('database.json', 'w', encoding='utf8') as outfile:
    json.dump(database, outfile, ensure_ascii=False)
