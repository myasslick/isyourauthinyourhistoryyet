import os
import unittest
try:
    from unitest.mock import patch, MagicMock, call
except ImportError:
    from mock import patch, MagicMock, call
from bs4 import BeautifulSoup as BS

from isyourauthinyourhistoryyet import github

FIXTURE_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
     "fixtures")

class TestMockGithubHTML(unittest.TestCase):

    @patch("requests.get")
    def test_1search_code_returns_text(self, requests):
        requests.return_value = MagicMock(text="123")
        html = github.search_code("Python", "hello world", 1)
        self.assertEqual(html, "123")

    def test_get_repo_link_with_beginning_slash(self):
        a = {"href": "/name/repo"}
        item = MagicMock()
        item.find.return_value = MagicMock(a=a)
        link = github.get_repo_link(item)
        self.assertEqual(link,
            github.GITHUB_URL + "name/repo")

    @patch("isyourauthinyourhistoryyet.github.BS")
    def test_get_code_list(self, bs):
        html = "html"
        bs.return_value.findAll.return_value = range(0,2)
        code_items = github.get_code_list(html)
        self.assertEqual(code_items, range(0,2))

    @patch("isyourauthinyourhistoryyet.github.get_repo_link")
    @patch("isyourauthinyourhistoryyet.github.get_code_list")
    @patch("isyourauthinyourhistoryyet.github.search_code")
    def test_search_max_2(self, search_code, get_code_list, get_repo_link):
        html = "html"
        search_code.return_value = html
        code_lists = [
            ["/user1/repo1"],
            ["/user2/repo2"]
        ]
        link_lists = [link for links in code_lists for link in links]
        get_code_list.side_effect = code_lists
        get_repo_link.side_effect = link_lists

        generator = github.search(max_page=2)
        self.assertEqual(generator.next(), link_lists[0])
        self.assertEqual(generator.next(), link_lists[1])
        self.assertRaises(StopIteration, generator.next)

        get_code_list.assert_has_calls([call(html), call(html)])
        get_repo_link.assert_has_calls(
            [
                call(code_lists[0][0]),
                call(code_lists[1][0])
            ]
        )
class TestGithubHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = github.search_code("Python", "hello world", 1)
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
        html = github.search_code("Python", "hello world", 2)
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

    @patch("isyourauthinyourhistoryyet.github.search_code")
    def test_search_page_1_2(self, search_code):
        file1 = os.path.join(FIXTURE_DIR, "hello_world_page_1.html")
        fil2 = os.path.join(FIXTURE_DIR, "hello_world_page_2.html")

        with open(file1, "r") as f:
            f1 = f.read()
        with open(fil2, "r") as f:
            f2 = f.read()
        search_code.side_effect = [f1, f2]
        # there are 10 repo links per each file
        links = []
        for link in github.search(max_page=2):
            links.append(link)
        self.assertEqual(len(links), 20)
        self.assertEqual(links[0], "https://github.com/palodequeso/Element-Games-Engine")
        self.assertEqual(links[19], "https://github.com/ordavidil/hackita")
