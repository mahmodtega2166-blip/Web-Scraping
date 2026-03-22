import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_website(website):
    try:
        logging.info(f"Scraping website: {website}")
        headers = {"User-Agent": UserAgent().random}
        response = requests.get(website, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping website: {e}")
        return None

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    if not dom_content:
        return []
    return [dom_content[i:i+max_length] for i in range(0, len(dom_content), max_length)]

def extract_images(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    images = soup.find_all("img")
    image_urls = [img.get("src") for img in images if img.get("src")]
    return image_urls