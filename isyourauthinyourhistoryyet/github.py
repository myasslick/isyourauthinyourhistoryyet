import requests
from bs4 import BeautifulSoup

GITHUB_URL = "https://github.com/"

def search_code(language="Python", q="hello world", page=1):
    search_url = GITHUB_URL + "search?l={}&q={}&p={}&ref=advsearch&type=Code&utf8=%E2%9C%93"
    r = requests.get(search_url.format(language, q, page))
    return r.text
