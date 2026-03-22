import streamlit as st
import pandas as pd
import json
from scrape import (
    scrape_website, extract_body_content, clean_body_content,
    split_dom_content, extract_images
)
from parse import parse_with_gpt_batch, translate_text
from langdetect import detect
from urllib.parse import urlparse, urljoin
import os

st.set_page_config(page_title="AI Web Scraper", page_icon="🌐", layout="wide")

# Custom CSS
st.markdown("""
<style>
.stButton button { background-color: #673AB7; color: white; font-size: 16px; padding: 10px 24px; border-radius: 8px; border: none; }
.stButton button:hover { background-color: #512DA8; }
.footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #263238; color: white; text-align: center; padding: 10px; }
.image-card { border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = ""
if 'parsed_result' not in st.session_state:
    st.session_state.parsed_result = ""
if 'image_data' not in st.session_state:
    st.session_state.image_data = []
if 'raw_html' not in st.session_state:
    st.session_state.raw_html = ""

def is_valid_url(url):
    try:
        result = urlparse(url.strip())
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False

# Sidebar with menu (from image)
with st.sidebar:
    st.header("⚙️ Demonstrations")
    menu_choice = st.radio(
        "Options",
        ["Return R", "Settings", "Print", "Record a screencast",
         "About", "Developer options", "Clear cache C"],
        index=None,
        label_visibility="collapsed"
    )
    
    if menu_choice == "Clear cache C":
        st.session_state.clear()
        st.rerun()
    elif menu_choice == "Print":
        if st.session_state.parsed_result:
            st.download_button("Download Parsed Result",
                               data=st.session_state.parsed_result,
                               file_name="parsed_output.txt")
        else:
            st.warning("No parsed content to print.")
    elif menu_choice == "About":
        st.info("AI Web Scraper v2.0\nRule-based extraction (no AI)")
    elif menu_choice == "Developer options":
        with st.expander("Session State"):
            st.json(st.session_state)
    elif menu_choice == "Settings":
        st.write("Settings would go here.")
    elif menu_choice == "Record a screencast":
        st.write("Recording feature not implemented.")
    elif menu_choice == "Return R":
        st.write("Return R placeholder.")

    st.divider()
    st.header("⚙️ Scraper Settings")
    chunk_size = st.number_input("Chunk Size", min_value=1000, max_value=10000, value=6000, step=500)
    extract_images_option = st.checkbox("Extract Images", value=True)

# Main app
st.title("🌐 AI Web Scraper with Image Extraction")
st.markdown("Scrape websites, extract text content and images, and export as CSV/JSON.")

# Step 1: Scrape Website
st.header("Step 1: Scrape Website")
urls_input = st.text_area("Enter Website URLs (one per line)",
                          placeholder="https://example.com\nhttps://example.org")

if st.button("Scrape Websites"):
    if urls_input:
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
        valid_urls = [u for u in urls if is_valid_url(u)]

        if not valid_urls:
            st.error("Please enter at least one valid URL.")
        else:
            with st.spinner("Scraping..."):
                all_dom, all_raw, images = [], [], []
                for url in valid_urls:
                    raw = scrape_website(url)
                    if raw:
                        all_raw.append(raw)
                        body = extract_body_content(raw)
                        cleaned = clean_body_content(body)
                        all_dom.append(cleaned)
                        if extract_images_option:
                            for img_src in extract_images(raw):
                                if img_src:
                                    full_url = urljoin(url, img_src) if not img_src.startswith(('http','https')) else img_src
                                    images.append({
                                        "source_url": url,
                                        "image_url": full_url,
                                        "filename": full_url.split('/')[-1][:100]
                                    })
                    else:
                        st.error(f"Failed to scrape: {url}")

                if all_dom:
                    st.session_state.dom_content = "\n".join(all_dom)
                    st.session_state.raw_html = "\n".join(all_raw)
                    if images:
                        st.session_state.image_data = images
                        st.success(f"Scraped {len(all_dom)} page(s) with {len(images)} images!")
                    else:
                        st.success(f"Scraped {len(all_dom)} page(s)!")

                    with st.expander("View Text Content"):
                        st.text_area("DOM Content", st.session_state.dom_content, height=300)
                    try:
                        lang = detect(st.session_state.dom_content)
                        st.write(f"Detected Language: {lang}")
                    except:
                        st.warning("Could not detect language")
    else:
        st.warning("Enter at least one URL.")

# Step 2: Parse Content
if st.session_state.dom_content:
    st.header("Step 2: Parse Content")

    parsing_examples = {
        "Extract Headings": "Extract all headings (h1, h2, h3) from the text.",
        "Extract Links": "Extract all links (URLs) from the text.",
        "Extract Prices": "Extract all prices with currency symbols.",
        "Extract Emails": "Extract email addresses.",
        "Extract Phones": "Extract phone numbers.",
        "Arabic Headings": "استخراج جميع العناوين (h1, h2, h3) من النص.",
        "Arabic Links": "استخراج جميع الروابط من النص.",
    }

    example_choice = st.selectbox("Choose example", list(parsing_examples.keys()))
    parse_description = st.text_area("Parsing instructions",
                                     value=parsing_examples[example_choice],
                                     placeholder="Describe what to extract")

    if st.button("Parse Content"):
        if parse_description:
            with st.spinner("Parsing..."):
                chunks = split_dom_content(st.session_state.dom_content, max_length=chunk_size)
                progress_bar = st.progress(0)
                results = []
                for i, chunk in enumerate(chunks):
                    res = parse_with_gpt_batch([chunk], parse_description)
                    results.append(res[0] if res else "")
                    progress_bar.progress((i+1)/len(chunks))
                st.session_state.parsed_result = "\n---\n".join(results)
                st.success("Parsing complete!")
                st.write("Results:", st.session_state.parsed_result)
        else:
            st.warning("Please enter parsing instructions.")

# Step 3: Export Data
if st.session_state.parsed_result or st.session_state.image_data:
    st.header("Step 3: Export Data")

    # Build combined data
    export_data = []
    if st.session_state.parsed_result:
        for line in st.session_state.parsed_result.splitlines():
            if line.strip():
                export_data.append({
                    "type": "text",
                    "content": line.strip(),
                    "source_url": urls_input.split("\n")[0].strip() if urls_input else "",
                    "timestamp": pd.Timestamp.now().isoformat()
                })
    if st.session_state.image_data:
        for img in st.session_state.image_data:
            export_data.append({
                "type": "image",
                "content": img["image_url"],
                "filename": img["filename"],
                "source_url": img["source_url"],
                "timestamp": pd.Timestamp.now().isoformat()
            })

    if export_data:
        df = pd.DataFrame(export_data)
        st.write("Preview:")
        st.dataframe(df)

        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("Download CSV", csv, "scraped_data.csv", "text/csv")
        with col2:
            json_data = df.to_json(orient="records", force_ascii=False)
            st.download_button("Download JSON", json_data, "scraped_data.json", "application/json")

        st.info("💡 For Excel: use 'From Text/CSV' with UTF-8 encoding")

# Image Gallery
if st.session_state.image_data:
    st.header("📸 Extracted Images")
    cols = st.columns(4)
    for idx, img in enumerate(st.session_state.image_data):
        with cols[idx % 4]:
            st.markdown(f"""
            <div class="image-card">
                <img src="{img['image_url']}" style="width:100%; border-radius: 8px;">
                <p style="word-wrap: break-word;">{img['filename']}</p>
                <small><a href="{img['source_url']}" target="_blank">Source</a></small>
            </div>
            """, unsafe_allow_html=True)

# Session management
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Save Session"):
        session = {
            "dom_content": st.session_state.get("dom_content", ""),
            "parsed_result": st.session_state.get("parsed_result", ""),
            "image_data": st.session_state.get("image_data", []),
            "raw_html": st.session_state.get("raw_html", "")
        }
        try:
            with open("session.json", "w", encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False)
            st.success("Session saved!")
        except Exception as e:
            st.error(f"Save error: {e}")
with col2:
    if st.button("Load Session"):
        try:
            with open("session.json", "r", encoding='utf-8') as f:
                session = json.load(f)
            st.session_state.dom_content = session.get("dom_content", "")
            st.session_state.parsed_result = session.get("parsed_result", "")
            st.session_state.image_data = session.get("image_data", [])
            st.session_state.raw_html = session.get("raw_html", "")
            st.success("Session loaded!")
        except FileNotFoundError:
            st.error("No saved session found")
        except Exception as e:
            st.error(f"Load error: {e}")
with col3:
    if st.button("Reset All"):
        st.session_state.clear()
        st.rerun()

# Footer
st.markdown('<div class="footer"><p>Developed with ❤️ | AI Web Scraper</p></div>', unsafe_allow_html=True)