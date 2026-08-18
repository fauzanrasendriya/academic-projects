import re

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db import get_engine
from src.schema import Project, Response

METADATA_COLS = [
    "SbjNum",
    "No Project",
    "Category",
    "Sub-Category",
    "Detail Product",
    "Gender",
    "Actual Age",
    "SES",
    "Occupation",
    "Type of Study",
    "Test Type",
    "Methodology",
    "Sub-Method",
    "# of Product",
    "Sequence",
]

VARIABLE_CANON = {
    "aftert\\aste": "aftertaste",
    "aftertaste.1": "aftertaste",
    "cofee aroma": "coffee aroma",
    "coffee taste.1": "coffee taste",
    "color.1": "color",
    "overal liking": "overall liking",
    "overal taste": "overall taste",
    "popcorn caramel ttaste": "popcorn caramel taste",
    "purchase intent w/ price.1": "purchase intent w/ price",
    "sovouriness": "savoriness",
    "balance taste": "balanced taste",
    "ease to bite": "easy to bite",
}

GENDER_CANON = {
    "laki-laki": "Male",
    "male": "Male",
    "perempuan": "Female",
    "female": "Female",
}

SES_CANON = {
    "a1": "Upper 1 (A)",
    "a2": "Upper 2 (B)",
    "b": "Upper 2 (B)",
    "upper 1 (a)": "Upper 1 (A)",
    "upper 2 (b)": "Upper 2 (B)",
    "middle 1 (c1)": "Middle 1 (C1)",
    "middle 2 (c2)": "Middle 2 (C2)",
    "middle 2 ()": "Middle 2 (C2)",
    "lower 1 (d)": "Lower 1 (D)",
}

BATCH_SIZE = 5000


def extract_scale(col_name: str) -> int | None:
    match = re.search(r"(\d+)\s*pts", col_name, re.IGNORECASE)
    return int(match.group(1)) if match else None


def normalize_score(score, scale_max: int) -> float:
    return round((score - 1) / (scale_max - 1), 4)


def clean_project_id(raw: str) -> str:
    return str(raw).strip()


def clean_respondent_id(raw) -> str | None:
    try:
        return str(int(float(str(raw).strip())))
    except (ValueError, TypeError):
        return None


def _clean_optional(value):
    return None if pd.isna(value) else str(value).strip()


def _clean_gender(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return GENDER_CANON.get(value.lower(), value)


def _clean_ses(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return SES_CANON.get(value.lower(), value)


def _clean_age(value):
    if pd.isna(value):
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def _variable_metadata(score_cols):
    metadata = {}
    for col in score_cols:
        scale_max = extract_scale(col)
        if scale_max is None:
            continue

        variable_name = re.sub(
            r"\s*-?\s*\d+\s*pts?", "", col, flags=re.IGNORECASE
        ).strip().lower()
        variable_name = re.sub(r"\s+", " ", variable_name)
        variable_name = VARIABLE_CANON.get(variable_name, variable_name)
        metadata[col] = (variable_name, scale_max)
    return metadata


def _chunks(records, size=BATCH_SIZE):
    for start in range(0, len(records), size):
        yield records[start : start + size]


def load_sheet(
    sheet_name: str, df: pd.DataFrame, engine, segment: str | None = None
) -> dict:
    """Clean one worksheet and bulk-load new projects and responses."""
    df = df.loc[:, df.columns.notna()]
    df = df.loc[:, [c for c in df.columns if isinstance(c, str) and c.strip() != ""]]

    score_cols = [c for c in df.columns if c not in METADATA_COLS]
    variable_meta = _variable_metadata(score_cols)
    stats = {"sheet": sheet_name, "projects": 0, "responses": 0, "skipped": 0}

    project_records = {}
    candidate_responses = []
    seen_candidate_keys = set()

    for row in df.to_dict("records"):
        raw_pid = row.get("No Project")
        if pd.isna(raw_pid):
            stats["skipped"] += 1
            continue

        project_id = clean_project_id(raw_pid)
        respondent_id = clean_respondent_id(row.get("SbjNum"))
        if respondent_id is None:
            stats["skipped"] += 1
            continue

        if project_id not in project_records:
            year_match = re.search(r"(\d{4})", project_id)
            project_records[project_id] = {
                "project_id": project_id,
                "year": int(year_match.group(1)) if year_match else None,
                "category": _clean_optional(row.get("Category")),
                "sub_category": _clean_optional(row.get("Sub-Category")),
                "detail_product": _clean_optional(row.get("Detail Product")),
                "test_type": _clean_optional(row.get("Test Type")),
                "methodology": _clean_optional(row.get("Methodology")),
                "sub_method": _clean_optional(row.get("Sub-Method")),
            }

        gender = _clean_gender(row.get("Gender"))
        age = _clean_age(row.get("Actual Age"))
        ses = _clean_ses(row.get("SES"))
        occupation = _clean_optional(row.get("Occupation"))

        for col, (variable_name, scale_max) in variable_meta.items():
            raw_score = row.get(col)
            if pd.isna(raw_score):
                continue

            try:
                score_val = float(raw_score)
            except (ValueError, TypeError):
                continue

            key = (respondent_id, project_id, segment, variable_name)
            if key in seen_candidate_keys:
                continue
            seen_candidate_keys.add(key)

            candidate_responses.append(
                {
                    "respondent_id": respondent_id,
                    "project_id": project_id,
                    "segment": segment,
                    "variable_name": variable_name,
                    "scale_max": scale_max,
                    "score": score_val,
                    "score_normalized": normalize_score(score_val, scale_max),
                    "gender": gender,
                    "actual_age": age,
                    "ses": ses,
                    "occupation": occupation,
                }
            )

    if not project_records:
        return stats

    project_ids = list(project_records)

    # One lookup replaces session.get() for every source row.
    with engine.connect() as conn:
        existing_projects = set(
            conn.execute(
                select(Project.project_id).where(Project.project_id.in_(project_ids))
            ).scalars()
        )

        # One lookup replaces a SELECT for every response. This also preserves
        # idempotency when segment is NULL, which a regular PostgreSQL UNIQUE
        # constraint alone does not guarantee because NULL values are distinct.
        existing_response_keys = set(
            conn.execute(
                select(
                    Response.respondent_id,
                    Response.project_id,
                    Response.segment,
                    Response.variable_name,
                ).where(Response.project_id.in_(project_ids))
            ).all()
        )

    new_projects = [
        record
        for project_id, record in project_records.items()
        if project_id not in existing_projects
    ]
    new_responses = [
        record
        for record in candidate_responses
        if (
            record["respondent_id"],
            record["project_id"],
            record["segment"],
            record["variable_name"],
        )
        not in existing_response_keys
    ]

    with engine.begin() as conn:
        if new_projects:
            stmt = pg_insert(Project).on_conflict_do_nothing(
                index_elements=[Project.project_id]
            )
            for batch in _chunks(new_projects):
                conn.execute(stmt, batch)

        if new_responses:
            stmt = pg_insert(Response).on_conflict_do_nothing(
                constraint="uq_response"
            )
            for batch in _chunks(new_responses):
                conn.execute(stmt, batch)

    stats["projects"] = len(new_projects)
    stats["responses"] = len(new_responses)
    return stats


def run_ingestion(filepath: str):
    engine = get_engine()
    xl = pd.ExcelFile(filepath)

    # Mapping sheet -> segment for projects with multiple respondent segments.
    segment_map = {
        "Parma Moms": "moms",
        "Parma Kids": "kids",
    }

    print(f"Processing {len(xl.sheet_names)} sheets...\n")
    total_responses = 0

    for sheet_name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet_name, header=1)
        segment = segment_map.get(sheet_name)
        result = load_sheet(sheet_name, df, engine, segment=segment)
        print(
            f"[{result['sheet']:<15}] projects: {result['projects']:>3} | "
            f"responses: {result['responses']:>6} | skipped: {result['skipped']:>3}"
        )
        total_responses += result["responses"]

    print(f"\nDone. Total responses inserted: {total_responses:,}")


if __name__ == "__main__":
    run_ingestion("data/data.xlsx")
