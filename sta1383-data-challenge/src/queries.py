import pandas as pd
from sqlalchemy import func, select

from src.db import get_engine
from src.schema import Project, Response

NORM_COLUMNS = [
    "Parameter",
    "Skala",
    "Norm Grade",
    "Base (N)",
    "TB%",
    "TB2%",
    "TB3%",
    "Mean Score",
]


def _score_query(
    variable_names=None,
    scale_max=None,
    gender=None,
    ses=None,
    category=None,
    sub_category=None,
    detail_product=None,
    occupation=None,
    test_type=None,
    methodology=None,
    sub_method=None,
    age_min=None,
    age_max=None,
    year=None,
):
    stmt = (
        select(Response.variable_name, Response.scale_max, Response.score)
        .join(Project, Response.project_id == Project.project_id)
    )

    if variable_names:
        stmt = stmt.where(Response.variable_name.in_(variable_names))
    if scale_max:
        stmt = stmt.where(Response.scale_max == scale_max)
    if gender:
        stmt = stmt.where(Response.gender == gender)
    if ses:
        stmt = stmt.where(Response.ses == ses)
    if category:
        stmt = stmt.where(Project.category == category)
    if sub_category:
        stmt = stmt.where(Project.sub_category == sub_category)
    if detail_product:
        stmt = stmt.where(Project.detail_product == detail_product)
    if occupation:
        stmt = stmt.where(Response.occupation == occupation)
    if test_type:
        stmt = stmt.where(Project.test_type == test_type)
    if methodology:
        stmt = stmt.where(Project.methodology == methodology)
    if sub_method:
        stmt = stmt.where(Project.sub_method == sub_method)
    if age_min is not None:
        stmt = stmt.where(Response.actual_age >= age_min)
    if age_max is not None:
        stmt = stmt.where(Response.actual_age <= age_max)
    if year:
        stmt = stmt.where(Project.year == year)

    return stmt


def _compute_stats(scores: pd.Series, scale_max: int) -> dict:
    n = len(scores)
    if n == 0:
        return {
            "base_n": 0,
            "tb_pct": None,
            "t2b_pct": None,
            "t3b_pct": None,
            "mean_score": None,
        }

    return {
        "base_n": n,
        "tb_pct": round((scores >= scale_max).sum() / n * 100, 1),
        "t2b_pct": round((scores >= scale_max - 1).sum() / n * 100, 1),
        "t3b_pct": (
            round((scores >= scale_max - 2).sum() / n * 100, 1)
            if scale_max >= 7
            else None
        ),
        "mean_score": round(float(scores.mean()), 2),
    }


def _norm_result(variable_name: str, scale_max: int, scores: pd.Series) -> dict:
    scores = pd.to_numeric(scores, errors="coerce").dropna().sort_values(ascending=False)
    if scores.empty:
        return {}

    total_n = len(scores)
    top_n = max(1, round(total_n * 0.25))
    avg_n = max(1, round(total_n * 0.50))

    top_scores = scores.iloc[:top_n]
    avg_scores = scores.iloc[top_n : top_n + avg_n]
    bot_scores = scores.iloc[top_n + avg_n :]

    return {
        "variable_name": variable_name,
        "scale_max": scale_max,
        "total_n": total_n,
        "top_25": _compute_stats(top_scores, scale_max),
        "avg_50": _compute_stats(avg_scores, scale_max),
        "bot_25": _compute_stats(bot_scores, scale_max),
    }


def get_norm_table(
    variable_names=None,
    scale_max=None,
    gender=None,
    ses=None,
    category=None,
    sub_category=None,
    detail_product=None,
    occupation=None,
    test_type=None,
    methodology=None,
    sub_method=None,
    age_min=None,
    age_max=None,
    year=None,
):
    """Return the full norm table using a single score query."""
    engine = get_engine()
    stmt = _score_query(
        variable_names=variable_names,
        scale_max=scale_max,
        gender=gender,
        ses=ses,
        category=category,
        sub_category=sub_category,
        detail_product=detail_product,
        occupation=occupation,
        test_type=test_type,
        methodology=methodology,
        sub_method=sub_method,
        age_min=age_min,
        age_max=age_max,
        year=year,
    )

    with engine.connect() as conn:
        df = pd.read_sql(stmt, conn)

    if df.empty:
        return pd.DataFrame(columns=NORM_COLUMNS)

    rows = []
    grouped = df.groupby(["variable_name", "scale_max"], sort=True, observed=True)

    for (variable_name, group_scale), group in grouped:
        result = _norm_result(variable_name, int(group_scale), group["score"])
        if not result:
            continue

        mapping = {
            "Top 25%": result["top_25"],
            "Average 50%": result["avg_50"],
            "Bottom 25%": result["bot_25"],
        }

        for grade, stats in mapping.items():
            if stats["base_n"] == 0:
                continue
            rows.append(
                {
                    "Parameter": result["variable_name"],
                    "Skala": f"{result['scale_max']}pts",
                    "Norm Grade": grade,
                    "Base (N)": stats["base_n"],
                    "TB%": stats["tb_pct"],
                    "TB2%": stats["t2b_pct"],
                    "TB3%": stats["t3b_pct"],
                    "Mean Score": stats["mean_score"],
                }
            )

    return pd.DataFrame(rows, columns=NORM_COLUMNS)


def get_summary_stats():
    """Fetch all dashboard summary counts in one database round-trip."""
    engine = get_engine()
    stmt = select(
        select(func.count(Project.project_id)).scalar_subquery().label("projects"),
        select(func.count(func.distinct(Response.respondent_id)))
        .scalar_subquery()
        .label("respondents"),
        select(func.count(Response.id)).scalar_subquery().label("responses"),
        select(func.count(func.distinct(Response.variable_name)))
        .scalar_subquery()
        .label("variables"),
    )

    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().one()

    return dict(row)


def get_norm_by_percentile(
    variable_name: str,
    scale_max: int,
    category: str | None = None,
    sub_category: str | None = None,
    detail_product: str | None = None,
    occupation: str | None = None,
    test_type: str | None = None,
    methodology: str | None = None,
    sub_method: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    year: int | None = None,
    gender: str | None = None,
    ses: str | None = None,
) -> dict:
    """Calculate percentile norm statistics for one variable and scale."""
    engine = get_engine()
    stmt = _score_query(
        variable_names=[variable_name],
        scale_max=scale_max,
        gender=gender,
        ses=ses,
        category=category,
        sub_category=sub_category,
        detail_product=detail_product,
        occupation=occupation,
        test_type=test_type,
        methodology=methodology,
        sub_method=sub_method,
        age_min=age_min,
        age_max=age_max,
        year=year,
    )

    with engine.connect() as conn:
        df = pd.read_sql(stmt, conn)

    if df.empty:
        return {}

    return _norm_result(variable_name, scale_max, df["score"])


def get_available_filters(engine=None) -> dict:
    """Fetch unique values used by dashboard filter controls."""
    if engine is None:
        engine = get_engine()

    with engine.connect() as conn:
        categories = pd.read_sql(
            select(Project.category).distinct().order_by(Project.category), conn
        )
        sub_cats = pd.read_sql(
            select(Project.sub_category).distinct().order_by(Project.sub_category), conn
        )
        detail_products = pd.read_sql(
            select(Project.detail_product).distinct().order_by(Project.detail_product), conn
        )
        test_types = pd.read_sql(
            select(Project.test_type).distinct().order_by(Project.test_type), conn
        )
        methodologies = pd.read_sql(
            select(Project.methodology).distinct().order_by(Project.methodology), conn
        )
        sub_methods = pd.read_sql(
            select(Project.sub_method).distinct().order_by(Project.sub_method), conn
        )
        years = pd.read_sql(select(Project.year).distinct().order_by(Project.year), conn)
        variables = pd.read_sql(
            select(Response.variable_name, Response.scale_max)
            .distinct()
            .order_by(Response.variable_name, Response.scale_max),
            conn,
        )
        genders = pd.read_sql(
            select(Response.gender)
            .where(Response.gender.is_not(None))
            .distinct()
            .order_by(Response.gender),
            conn,
        )
        ses_list = pd.read_sql(
            select(Response.ses)
            .where(Response.ses.is_not(None))
            .distinct()
            .order_by(Response.ses),
            conn,
        )
        occupations = pd.read_sql(
            select(Response.occupation)
            .where(Response.occupation.is_not(None))
            .distinct()
            .order_by(Response.occupation),
            conn,
        )
        age_bounds = conn.execute(
            select(
                func.min(Response.actual_age).label("min_age"),
                func.max(Response.actual_age).label("max_age"),
            ).where(Response.actual_age.is_not(None))
        ).mappings().one()

    return {
        "categories": categories["category"].dropna().tolist(),
        "sub_categories": sub_cats["sub_category"].dropna().tolist(),
        "detail_products": detail_products["detail_product"].dropna().tolist(),
        "test_types": test_types["test_type"].dropna().tolist(),
        "methodologies": methodologies["methodology"].dropna().tolist(),
        "sub_methods": sub_methods["sub_method"].dropna().tolist(),
        "years": years["year"].dropna().tolist(),
        "variables": variables.to_dict("records"),
        "variable_names": sorted(variables["variable_name"].dropna().unique().tolist()),
        "genders": genders["gender"].dropna().tolist(),
        "ses": ses_list["ses"].dropna().tolist(),
        "occupations": occupations["occupation"].dropna().tolist(),
        "age_min": age_bounds["min_age"],
        "age_max": age_bounds["max_age"],
    }
