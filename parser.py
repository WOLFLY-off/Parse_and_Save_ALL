import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from io import StringIO
import re


class AutoParser:
    def __init__(self, user_url: str, timeout: int = 10):
        self.url = user_url
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }

        response = requests.get(self.url, headers=self.headers, timeout=timeout)
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        self.html_code = response.text
        self.soup = BeautifulSoup(self.html_code, "html.parser")
    
    # 1. Таблицы (Pandas)
    def parse_tables(self):
        parsed_tables = []
        try:
            tables = pd.read_html(StringIO(self.html_code))
            for idx, df in enumerate(tables):
                df_clean = df.fillna("")
                parsed_tables.append({
                    "table_id": idx + 1,
                    "headers": [str(col) for col in df_clean.columns],
                    "rows": df_clean.values.tolist(),
                })
            return parsed_tables
        except ValueError:
            return []

    # 2. Изображения (Images)
    def parse_image(self):
            images = []
            for img in self.soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src:
                    full_url = urljoin(self.url, src)
                    alt = img.get("alt", "").strip() or "Без описания"
                    images.append({"url": full_url, "alt": alt})
            # Ограничим до первых 30 изображений, чтобы не перегружать DOM
            # (Let’s limit it to the first 30 images so as not to overload the DOM.)
            images = images[:30]
            return images

    # 3. Email
    def parse_email(self):
        raw_text = self.soup.get_text()
            
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", raw_text))
        for a in self.soup.find_all("a", href=True):
            if a["href"].startswith("mailto:"):
                emails.add(a["href"].replace("mailto:", "").split("?")[0])

        clean_emails = list(emails)[:15]
        return clean_emails

    # 4. Телефоны (Phones)
    def parse_phones(self):
        raw_text = self.soup.get_text()

        phones = set(re.findall(r"\+?\d[\d\s\-\(\)]{8,}\d", raw_text))
        for a in self.soup.find_all("a", href=True):
            if a["href"].startswith("tel:"):
                phones.add(a["href"].replace("tel:", ""))
    
        clean_phones = list({p.strip() for p in phones if len(re.sub(r"\D", "", p)) >= 10})[:15]
        return clean_phones

    # 5. Ссылки (Links)
    def parse_link(self):
        links = []
        for a in self.soup.find_all("a", href=True):
            href = a["href"].strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                full_link = urljoin(self.url, href)
                text = a.get_text().strip() or full_link
                links.append({"text": text[:50], "url": full_link})
    
        links = links[:20]  # Первые 20 (First 20)
        return links

    # 6. Текст (Text)
    def parse_txt(self):
        for tag in self.soup(["script", "style", "noscript"]):
            tag.extract()
        text = self.soup.get_text(separator="\n", strip=True)
        clean_text = text[:800]

        return clean_text

    # Сразу всё (Everything at once)
    def parse_all(self):
        return {
            "tables": self.parse_tables(),
            "images": self.parse_image(),
            "emails": self.parse_email(),
            "phones": self.parse_phones(),
            "links": self.parse_link(),
            "text_preview": self.parse_txt(),
        }