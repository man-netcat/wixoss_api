# API for the WIXOSS card game

WIXOSS API fetching data from https://www.wixosstcg.eu/

Included are a database builder + card image downloader and an API for card search.

Usage: First run download_data.py to build the database, then run wixoss_api.py.

API supports `id`, `level`, `limits`, `type`, `class`, `rarity` and `color`.

For disjunctive search, use `&or` (AND is default)
