import pandas as pd
import numpy as np

class DataAnalyzer:
    def analyze_films_data(self, df: pd.DataFrame):
        results = {}

        df_clean = self.clean_and_convert(df)

        # 1. Count movies with Worldwide gross >= $2b released before 2020
        two_bn_before_2020 = df_clean[
            (df_clean['Worldwide gross'] >= 2_000_000_000) &
            (df_clean['Year'] < 2020)
        ].shape[0]
        results['two_bn_movies_before_2020'] = two_bn_before_2020

        # 2. Find earliest film grossed over $1.5b
        over_1_5bn = df_clean[df_clean['Worldwide gross'] >= 1_500_000_000]
        earliest_film = ""
        if not over_1_5bn.empty:
            earliest_film = over_1_5bn.loc[over_1_5bn['Year'].idxmin(), 'Title']
        results['earliest_1_5bn_film'] = earliest_film

        # 3. Correlation between Rank and Peak
        correlation = 0.0
        if 'Rank' in df_clean.columns and 'Peak' in df_clean.columns:
            correlation = df_clean['Rank'].corr(df_clean['Peak'])
            if pd.isna(correlation):
                correlation = 0.0
        results['rank_peak_correlation'] = correlation

        return results

    def clean_and_convert(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Normalize columns (strip footnotes)
        df.columns = [col.split('[')[0].strip() for col in df.columns]

        # Convert numeric columns safely, extract digits if needed
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')

        for col in ['Rank', 'Peak']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.extract(r'(\d+)')[0], errors='coerce')

        if 'Worldwide gross' in df.columns:
            df['Worldwide gross'] = self.parse_currency(df['Worldwide gross'])

        # Remove rows missing any of the key numeric data
        df = df.dropna(subset=['Year', 'Rank', 'Peak', 'Worldwide gross'], how='any')

        return df

    def parse_currency(self, s: pd.Series) -> pd.Series:
        def convert_value(val):
            if pd.isna(val) or val == '':
                return 0.0
            val = val.replace('$', '').replace(',', '').lower().strip()
            multiplier = 1
            if "billion" in val:
                multiplier = 1_000_000_000
                val = val.replace("billion", "").strip()
            elif "million" in val:
                multiplier = 1_000_000
                val = val.replace("million", "").strip()
            try:
                return float(val) * multiplier
            except:
                return 0.0
        return s.apply(convert_value)
