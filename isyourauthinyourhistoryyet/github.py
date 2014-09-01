import urlparse
import requests
from bs4 import BeautifulSoup as BS

GITHUB_URL = "https://github.com/"

def search_code(language, query, page):
    search_url = GITHUB_URL + "search?l={}&q={}&p={}&ref=advsearch&type=Code&utf8=%E2%9C%93"
    r = requests.get(search_url.format(language, query, page))
    return r.text

def get_repo_link(item):
    href = item.find("p").a["href"]
    return urlparse.urljoin(GITHUB_URL, href)

def get_code_list(html):
    soup = BS(html)
    code_list_items = soup.findAll("div",
            {"class": "code-list-item"})
    return code_list_items

def search(language="Python", q="hello world", max_page=None):
    not_max_yet = True
    page_counter = 1
    while not_max_yet:
        html = search_code(language, q, page_counter)
        for item in get_code_list(html):
            yield get_repo_link(item)
        if max_page:
            not_max_yet = page_counter + 1 <= max_page
        page_counter += 1
