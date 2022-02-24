import shutil
import sqlite3
import warnings
from os import path

import pandas as pd
from bs4 import BeautifulSoup
from requests_cache import CachedSession

warnings.filterwarnings("ignore")

base_url = 'https://www.wixosstcg.eu'
query = '/Carddb?nomecarta=&cerca=true&ordina=cardid&page=%s'
session = CachedSession()


def main():
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
            img_path = f'images/{cardid}.png'

            # Download img
            if not path.exists(img_path):
                img_res = session.get(base_url + img_href, stream=True)
                with open(img_path, 'wb') as out_file:
                    shutil.copyfileobj(img_res.raw, out_file)

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
    df = pd.DataFrame(database)
    conn = sqlite3.connect('database.db')
    df.to_sql("cards", conn, if_exists='replace', method='multi', index=False)


if __name__ == '__main__':
    main()
