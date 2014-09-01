import unittest
from bs4 import BeautifulSoup
from isyourauthinyourhistoryyet import github

class TestGithubHTML(unittest.TestCase):
    def test_github_default_to_best_match(self):
        html = github.search_code(language="Python", q="hello world")
        soup = BeautifulSoup(html)
        by_filter = soup.findAll("span", {"class": "js-select-button"})
        self.assertEqual(len(by_filter), 1)
        self.assertEqual(by_filter[0].text, "Best match")
