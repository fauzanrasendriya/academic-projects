# DEKA Norm Database

A PostgreSQL-backed Streamlit dashboard for ingesting, normalizing, and exploring survey norm data.

This project was developed for an academic project based on a case provided by **DEKA Insight**. It transforms multi-project survey data from Excel into a normalized relational database, calculates percentile-based norms, and presents the results through an interactive Streamlit dashboard.

## Architecture

```text
Excel source data
        ↓
Data cleaning and normalization
        ↓
Bulk ingestion
        ↓
Supabase PostgreSQL
        ↓
SQLAlchemy query layer
        ↓
Streamlit dashboard
```

Supabase provides the hosted PostgreSQL database, while Streamlit provides the dashboard interface.

## Project Structure

```text
.
├── app.py
├── data/
│   └── data.xlsx
├── notebooks/
│   └── 01_validasi_ingestion.ipynb
├── scripts/
│   └── init_db.py
├── src/
│   ├── db.py
│   ├── ingest.py
│   ├── queries.py
│   └── schema.py
├── .gitignore
├── requirements.txt
└── README.md
```

| File | Description |
| --- | --- |
| `app.py` | Main Streamlit dashboard |
| `src/db.py` | PostgreSQL connection configuration |
| `src/schema.py` | SQLAlchemy table definitions and constraints |
| `src/ingest.py` | Data cleaning, score normalization, and bulk ingestion |
| `src/queries.py` | Dashboard queries and norm calculations |
| `scripts/init_db.py` | Initializes the PostgreSQL schema |
| `notebooks/01_validasi_ingestion.ipynb` | Notebook for validating the ingestion process |
| `data/data.xlsx` | Confidential source workbook used locally for ingestion |

## Database Schema

The database contains two main tables:

### `projects`

Stores metadata for each survey project, including year, category, sub-category, detail product, test type, methodology, sub-method, and notes. `project_id` is the primary key.

### `responses`

Stores respondent-level measurements, including respondent ID, project ID, segment, demographic attributes, variable name, scale, original score, and normalized score.

`project_id` references `projects.project_id`, forming a one-to-many relationship:

```text
projects (1) ────────< responses (many)
```

During ingestion, the combination of `respondent_id`, `project_id`, `segment`, and `variable_name` is used to identify duplicate responses.

## Data Processing

`src/ingest.py` reads every worksheet from the source workbook, standardizes project and respondent information, detects the measurement scale, normalizes scores, and loads the processed data into PostgreSQL.

Scores are normalized using:

```text
normalized_score = (score - 1) / (scale_max - 1)
```

The original score is retained alongside the normalized score.

The ingestion process is optimized for a remote PostgreSQL database by checking existing records per worksheet, removing duplicate candidates in memory, inserting data in batches, and using PostgreSQL conflict handling.

## Norm Calculation

For each `variable_name` and `scale_max` combination, scores are sorted in descending order and divided into:

- **Top 25%**
- **Average 50%**
- **Bottom 25%**

The dashboard calculates:

- **Base (N)** — number of observations
- **TB%** — percentage at the highest scale value
- **TB2%** — percentage within the two highest scale values
- **TB3%** — percentage within the three highest scale values for supported scales
- **Mean Score** — average score on the original scale

Category, sub-category, detail product, gender, SES, occupation, test type, methodology, sub-method, and actual-age filters are applied before norm calculation. The required scores are retrieved from PostgreSQL and parameter-level norm groups are calculated in memory. Streamlit caching is used to reuse previously calculated filter combinations.

## Dashboard

The Streamlit application contains three pages:

- **Dashboard** — interactive filters for parameter, scale, norm grade, project attributes, demographics, and actual age; results are shown through KPI cards and a norm table.
- **Data** — summary counts for projects, respondents, responses, and parameters, together with the overall norm table.
- **About** — a short description of the dashboard.

## Local Setup

### 1. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase

Create a Supabase project and wait until its PostgreSQL database is ready.

From the Supabase project, open **Connect** and obtain the PostgreSQL connection parameters:

- database user
- database password
- database host
- database port
- database name

Create a `.env` file in the project root:

```env
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
```

These variables are read by `src/db.py` to establish the PostgreSQL connection.

### 4. Prepare the Source Data

Place the authorized source workbook at:

```text
data/data.xlsx
```

The ingestion process reads all worksheets from this workbook.

### 5. Initialize the Database

```bash
python -m scripts.init_db
```

This creates the `projects` and `responses` tables in the configured PostgreSQL database.

### 6. Run the Ingestion

```bash
python -m src.ingest
```

The script processes the workbook and loads new project and response records into PostgreSQL.

### 7. Run the Dashboard

```bash
python -m streamlit run app.py
```

Streamlit will display the local application URL in the terminal.


## Dashboard Availability

This project uses the **Supabase Free Plan** as its hosted PostgreSQL database. Free projects with low activity over a 7-day period may be automatically paused by Supabase.

Because the Streamlit dashboard depends on this database, the dashboard may be temporarily unavailable when the Supabase project is paused due to inactivity. The project must be resumed from Supabase before the dashboard can access the database again.

## Data Availability

The source dataset used in this project is confidential and **cannot be published or redistributed**. Therefore, `data/data.xlsx` is not included with the public project files.

The application code, database schema, ingestion logic, norm calculation, and dashboard implementation can be reviewed independently, but reproducing the populated database requires authorized access to the original source dataset.

## Tech Stack

- Python
- PostgreSQL
- Supabase
- SQLAlchemy
- pandas
- NumPy
- Streamlit
- psycopg2
- python-dotenv
- openpyxl
