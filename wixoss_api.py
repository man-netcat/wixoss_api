import json
import os
import shutil
from os import path
import types

from bs4 import BeautifulSoup
from requests_cache import CachedSession


def make_json():
    session = CachedSession()
    base_url = 'https://www.wixosstcg.eu'
    query = '/Carddb?nomecarta=&cerca=true&ordina=cardid&page=%s'

    database = []

    i = 1
    while True:
        req = session.get(base_url + query % i)
        soup = BeautifulSoup(req.content, 'html.parser')
        cards = soup.find('div', class_='risultati')

        # Reached end of pages
        if not cards:
            break

        for card in cards.find_all('a', class_='preview'):
            href = card['href']
            cardreq = session.get(base_url + href)
            cardsoup = BeautifulSoup(cardreq.content, 'html.parser')

            # Get main data container
            container = cardsoup.find('main', id='main-content')

            # Get card id
            img_href = container.find('img')['src']
            cardid = img_href.split('/')[2]

            # Write cardinfo to db
            cardinfo = container.find(
                'div', class_='col-md-6 padding-top-30').find_all('div')
            cardentry = {'Card Id': cardid}
            for key, value in zip(cardinfo[0::2], cardinfo[1::2]):
                stripped_key = key.get_text().strip()
                stripped_value = value.get_text().strip()
                cardentry[stripped_key] = stripped_value
            database.append(cardentry)
        i += 1

    session.close()

    # Write dict to json
    with open('database.json', 'w', encoding='utf8') as f:
        json.dump(database, f, ensure_ascii=False)


def download_images():
    session = CachedSession()
    base_url = 'https://www.wixosstcg.eu'
    query = '/Carddb?nomecarta=&cerca=true&ordina=cardid&page=%s'

    i = 1
    while True:
        req = session.get(base_url + query % i)
        soup = BeautifulSoup(req.content, 'html.parser')
        cards = soup.find('div', class_='risultati')

        # Reached end of pages
        if not cards:
            break

        for card in cards.find_all('a', class_='preview'):
            href = card['href']
            cardreq = session.get(base_url + href)
            cardsoup = BeautifulSoup(cardreq.content, 'html.parser')

            # Get main data container
            container = cardsoup.find('main', id='main-content')

            # Get image properties
            img_href = container.find('img')['src']
            cardid = img_href.split('/')[2]
            img_path = f'images/{cardid}.png'

            # Download img
            if not path.exists(img_path):
                img_res = session.get(base_url + img_href, stream=True)
                with open(img_path, 'wb') as out_file:
                    shutil.copyfileobj(img_res.raw, out_file)
        i += 1

    session.close()


def main():
    if not path.exists('database.json'):
        make_json()

    if not path.exists('images'):
        os.mkdir('images')
        download_images()


if __name__ == '__main__':
    main()
