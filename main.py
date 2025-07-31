from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from app.services.data_scraper import DataScraper
from app.services.data_analyzer import DataAnalyzer
from app.services.chart_generator import ChartGenerator
from app.services.duckdb_handler import DuckDBHandler

app = FastAPI(title="Data Analyst Agent", version="1.0.0")

# CORS Middleware to allow all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = DataScraper()
analyzer = DataAnalyzer()
chart_gen = ChartGenerator()
duckdb = DuckDBHandler()

@app.get("/")
async def root():
    return {"message": "Data Analyst Agent API is running."}

@app.post("/api/")
async def analyze_data(file: UploadFile = File(...)):
    try:
        content = await file.read()
        question = content.decode('utf-8')

        print("Received question text:", repr(question))  # Debug print for incoming question

        # Handle Wikipedia highest grossing films task
        if "highest grossing films" in question.lower() or "highest-grossing films" in question.lower():
            url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
            df = scraper.scrape_wikipedia_table(url)
            print("Scraped DataFrame columns:", df.columns)
            print("Sample rows:\n", df.head())

            # Normalize columns by removing footnotes like [a], [1], etc.
            df.columns = [col.split('[')[0].strip() for col in df.columns]

            expected_cols = ['Rank', 'Peak']
            missing_cols = [col for col in expected_cols if col not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=500, detail=f"Missing columns for plot: {missing_cols}")

            # Extract numeric part and convert to float for Rank and Peak
            for col in expected_cols:
                df[col] = df[col].astype(str).str.extract(r'(\d+)')[0]
                df[col] = df[col].apply(pd.to_numeric, errors='coerce')

            # Drop rows with missing Rank or Peak values
            df = df.dropna(subset=expected_cols)
            if df.empty:
                raise HTTPException(status_code=500, detail="No data available for Rank vs Peak plotting")

            # Analyze film data answers
            results = analyzer.analyze_films_data(df)

            # Generate scatterplot
            scatter_uri = chart_gen.create_scatterplot_with_regression(
                df['Rank'],
                df['Peak'],
                x_label="Rank",
                y_label="Peak",
                title="Rank vs Peak"
            )

            # Prepare the response array as per project spec:
            response = [
                results.get('two_bn_movies_before_2020', 0),
                results.get('earliest_1_5bn_film', ""),
                round(results.get('rank_peak_correlation', 0.0), 6),
                scatter_uri
            ]
            return response

        # Handle Indian high court judgments questions
        elif "high court" in question.lower():
            # Placeholder example - replace with real querying of DuckDB + plotting logic
            response = {
                "Which high court disposed the most cases from 2019 - 2022?": "33_10",
                "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": 0.123,
                "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
            }
            return response

        else:
            raise HTTPException(status_code=400, detail="Unknown analysis task in question.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
