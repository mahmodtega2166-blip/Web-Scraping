import re
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_with_rules(text, instruction):
    """Extract content using BeautifulSoup and regex based on instruction."""
    if not text or not isinstance(text, str):
        return ""
    try:
        soup = BeautifulSoup(text, 'html.parser')
        instruction = instruction.lower().strip()

        # Headings
        if any(k in instruction for k in ['heading', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings = []
            for h in soup.find_all(re.compile('^h[1-6]$')):
                if h.text.strip():
                    headings.append(f"{h.name.upper()}: {h.text.strip()}")
            return "\n".join(headings) if headings else "No headings found"

        # Links
        elif any(k in instruction for k in ['link', 'url', 'href']):
            links = []
            for a in soup.find_all('a', href=True):
                text = a.text.strip()
                url = a['href'].strip()
                if url.startswith(('http://', 'https://', 'mailto:')):
                    links.append(f"{text} ({url})" if text else url)
            return "\n".join(links) if links else "No links found"

        # Prices
        elif 'price' in instruction:
            text_content = soup.get_text()
            price_regex = r'[\$€£¥]\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            prices = re.findall(price_regex, text_content)
            return "\n".join(prices) if prices else "No prices found"

        # Emails
        elif 'email' in instruction:
            text_content = soup.get_text()
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            emails = re.findall(email_regex, text_content)
            return "\n".join(emails) if emails else "No emails found"

        # Phone numbers
        elif any(k in instruction for k in ['phone', 'number', 'tel']):
            text_content = soup.get_text()
            phone_regex = r'(?:\+?\d{1,2}\s?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b'
            phones = [m.group() for m in re.finditer(phone_regex, text_content)]
            return "\n".join(phones) if phones else "No phone numbers found"

        # Clean text (default)
        else:
            for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
                tag.decompose()
            clean_text = soup.get_text(separator='\n', strip=True)
            return clean_text if clean_text else "No text content found"

    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return "Error during extraction"

def parse_with_gpt_batch(dom_chunks, parse_description, model_name=""):
    """Batch process chunks using rule-based extraction."""
    if not dom_chunks or not parse_description:
        return [""] * len(dom_chunks) if dom_chunks else []
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(
            lambda chunk: extract_with_rules(str(chunk), str(parse_description)),
            dom_chunks
        ))
    return results

def translate_text(text, target_language="en"):
    """Translation not available in rule-based mode."""
    logging.warning("Translation not available")
    return str(text) if text else ""