import unittest
try:
    from unitest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock
from bs4 import BeautifulSoup as BS

from isyourauthinyourhistoryyet import github

class TestMockGithubHTML(unittest.TestCase):

    @patch("requests.get")
    def test_1search_code_returns_text(self, requests):
        requests.return_value = MagicMock(text="123")
        html = github.search_code()
        self.assertEqual(html, "123")

    def test_get_repo_link_with_beginning_slash(self):
        a = {"href": "/name/repo"}
        item = MagicMock()
        item.find.return_value = MagicMock(a=a)
        link = github.get_repo_link(item)
        self.assertEqual(link,
            github.GITHUB_URL + "name/repo")

class TestGithubHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = github.search_code(language="Python", q="hello world")
        cls.soup = BS(html)
        
    def test_github_default_to_best_match(self):
        by_filter = self.soup.findAll("span", {"class": "js-select-button"})
        self.assertEqual(len(by_filter), 1)
        self.assertEqual(by_filter[0].text, "Best match")

    def test_search_page_is_on_page_1_by_default(self):
        current = self.soup.findAll("em", {"class": "current"})
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].text, "1")

    def test_search_page2_is_on_page2(self):
        html = github.search_code(language="Python", q="hello world",
                    page=2)
        soup = BS(html)
        current = soup.findAll("em", {"class": "current"})
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].text, "2")

    def test_code_list_element_has_title(self):
        code_list_items = self.soup.findAll("div",
            {"class": "code-list-item"})
        # Ensure there are at least 1 item
        self.assertTrue(len(code_list_items) > 0)
        # <p class="title"><a href="/user/repo">user/repo</a>....</p>
        repo_href = code_list_items[0].find("p").a
        self.assertTrue(repo_href)
        self.assertEqual(repo_href["href"], "/" + repo_href.text)
