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

            # Find all tables with class wikitable (ignore sortable)
            tables = soup.find_all('table', class_='wikitable')
            if not tables:
                raise ValueError("No wikitable found on the page")

            expected_cols = {'Rank', 'Peak', 'Title', 'Worldwide gross', 'Year'}
            for table in tables:
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                # Check if table has all expected columns
                if expected_cols.issubset(set(headers)):
                    rows = []
                    for tr in table.find_all('tr')[1:]:  # skip header row
                        cells = tr.find_all(['td', 'th'])
                        if len(cells) != len(headers):
                            continue
                        row = [cell.get_text(strip=True) for cell in cells]
                        rows.append(row)

                    df = pd.DataFrame(rows, columns=headers)
                    return self.clean_dataframe(df)

            raise ValueError("No suitable table found with expected columns")

        except Exception as e:
            raise Exception(f"Error scraping Wikipedia table: {str(e)}")

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove footnote references like [1], [a], etc. and strip extra whitespace
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(r'\[.*?\]', '', regex=True)
                df[col] = df[col].str.replace('\n', ' ', regex=False)
                df[col] = df[col].str.strip()
        return df
