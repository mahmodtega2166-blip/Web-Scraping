import unittest
from scrape import extract_body_content, clean_body_content, split_dom_content

class TestScrape(unittest.TestCase):
    def test_extract_body_content(self):
        html = "<html><body><p>Test content</p></body></html>"
        result = extract_body_content(html)
        self.assertIn("Test content", result)

    def test_clean_body_content(self):
        body = "<body><script>alert('test');</script><p>Test content</p></body>"
        result = clean_body_content(body)
        self.assertNotIn("alert", result)
        self.assertIn("Test content", result)

    def test_split_dom_content(self):
        content = "a" * 10000
        chunks = split_dom_content(content, max_length=3000)
        self.assertEqual(len(chunks), 4)
        self.assertEqual(len(chunks[0]), 3000)
        self.assertEqual(len(chunks[3]), 1000)

if __name__ == "__main__":
    unittest.main()