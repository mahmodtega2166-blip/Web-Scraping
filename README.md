# Web Scraping App (Streamlit)

A Python-based web scraping application that extracts data from multiple websites and displays the results through an interactive Streamlit interface.

## Overview
This project performs automated web scraping using Python, processes the extracted data, and presents it in a clean and user-friendly dashboard built with Streamlit.

The app supports scraping from various sources and is designed to be easily extendable.

## Technologies Used
- Python
- Streamlit
- Requests / BeautifulSoup (or your scraping libraries)
- Pandas
- Other dependencies listed in `requirements.txt`

## Project Structure
- **main.py** — Streamlit app entry point  
- **scrape.py** — Handles fetching and scraping website data  
- **parse.py** — Cleans and processes scraped content  
- **test_scrape.py** — Basic tests for scraping functions  
- **requirements.txt** — Project dependencies  
- **.gitignore** — Ignored files and folders  

## How to Run the App
Install dependencies:

```bash
pip install -r requirements.txt

streamlit run main.py
