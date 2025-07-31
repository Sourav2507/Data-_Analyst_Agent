import requests
from bs4 import BeautifulSoup
import pandas as pd

class DataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })

    def scrape_wikipedia_table(self, url: str) -> pd.DataFrame:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tables with class 'wikitable'
            tables = soup.find_all('table', class_='wikitable')
            if not tables:
                raise Exception("No wikitable found on the page")

            # Define expected keywords for flexible matching in headers
            expected_keywords = {
                'rank': None,
                'peak': None,
                'title': None,
                'film': None,
                'gross': None,
                'worldwide gross': None,
                'year': None,
            }

            for table in tables:
                headers_raw = [th.get_text(strip=True) for th in table.find_all('th')]
                headers = [header.lower() for header in headers_raw]

                # Map to store found columns keyword -> index
                found_cols = {}

                # Search headers for each expected keyword
                for kw in expected_keywords:
                    for idx, header in enumerate(headers):
                        if kw in header:
                            found_cols[kw] = idx
                            break  # only first match per keyword

                # Require: rank, peak, (title or film), gross/worldwide gross, year
                if ('rank' in found_cols and 
                    'peak' in found_cols and
                    ('title' in found_cols or 'film' in found_cols) and
                    ('gross' in found_cols or 'worldwide gross' in found_cols) and
                    'year' in found_cols):

                    rows = []
                    header_len = len(headers_raw)
                    for tr in table.find_all('tr')[1:]:  # skip header row
                        cells = tr.find_all(['td', 'th'])
                        if len(cells) != header_len:
                            continue
                        row = [cell.get_text(strip=True) for cell in cells]
                        rows.append(row)

                    df = pd.DataFrame(rows, columns=headers_raw)
                    if not df.empty:
                        return self.clean_dataframe(df)

            raise Exception("No suitable table found containing expected columns")

        except Exception as e:
            raise Exception(f"Error scraping Wikipedia table: {str(e)}")

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove footnotes like [1], [a], etc. and strip whitespace
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(r'\[.*?\]', '', regex=True)
                df[col] = df[col].str.replace('\n', ' ', regex=False)
                df[col] = df[col].str.strip()
        return df
