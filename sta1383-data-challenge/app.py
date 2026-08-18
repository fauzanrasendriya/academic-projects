import numpy as np
import streamlit as st

from src.queries import get_available_filters, get_norm_table, get_summary_stats


@st.cache_data
def load_norms(
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
    """Load the norm table with optional database-side filters."""
    return get_norm_table(
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


@st.cache_data
def load_filters():
    """Load semua nilai unik untuk filter dropdown."""
    return get_available_filters()


@st.cache_data
def load_stats():
    """Load summary statistics (project/respondent/response/variable count)."""
    return get_summary_stats()


stats = load_stats()
filters = load_filters()

NORM_GRADES = [
    "Top 25%",
    "Average 50%",
    "Bottom 25%",
]

variable_names = filters["variable_names"]
scales = sorted(set(v["scale_max"] for v in filters["variables"]))
age_min = int(filters["age_min"]) if filters["age_min"] is not None else 0
age_max = int(filters["age_max"]) if filters["age_max"] is not None else 100

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Norm Database",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# COLOR TOKENS
# =========================================================
NAVY = "#1B2A57"
ORANGE = "#F5A623"
BG = "#EEF2F8"
CARD_BG = "#FFFFFF"
TEXT_MUTED = "#9098AC"
TEXT_DARK = "#111827"
BORDER = "#E3E8F1"

# =========================================================
# SESSION STATE / FILTER DEFAULTS
# =========================================================
FILTER_DEFAULTS = {
    "f_parameter": [],
    "f_skala": "Semua",
    "f_norm_grade": "Semua",
    "f_category": "Semua",
    "f_sub_category": "Semua",
    "f_detail_product": "Semua",
    "f_gender": "Semua",
    "f_ses": "Semua",
    "f_occupation": "Semua",
    "f_test_type": "Semua",
    "f_methodology": "Semua",
    "f_sub_method": "Semua",
    "f_actual_age": (age_min, age_max),
}

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
for k, v in FILTER_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_filters():
    for k, v in FILTER_DEFAULTS.items():
        st.session_state[k] = v


# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown(
    f"""
<style>
.block-container {{ padding-top: 1.6rem; padding-bottom: 2rem; padding-left: 2.4rem; padding-right: 2.4rem; }}
[data-testid="stAppViewContainer"] {{ background-color: {BG}; }}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {{
    background-color: {NAVY};
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 0rem; }}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
    color: #D7DDEE;
}}
.brand {{
    padding: 0 20px 18px;
    margin-bottom: 50px;
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 0.2px;
    text-align: center;
}}

/* nav + reset buttons share stButton, base style = nav look */
[data-testid="stSidebar"] [data-testid="stButton"] button {{
    width: calc(100% - 8px);
    margin: 0 4px -4px;
    padding: 9px 18px;
    background-color: transparent;
    color: #C7CEE3;
    border: none;
    border-radius: 8px;
    box-shadow: none;
    justify-content: flex-start !important;
    text-align: left !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] button > div {{
    justify-content: flex-start !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] button p {{
    font-weight: 800 !important;
    font-size: 17px !important;
    text-align: left !important;
    width: 100% !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {{
    background-color: rgba(255,255,255,0.08);
    color: #FFFFFF;
}}
.st-key-reset_btn {{
    margin-top: -50px !important;
}}
.st-key-reset_btn button {{
    background-color: transparent !important;
    color: {ORANGE} !important;
    border: 1.5px solid {ORANGE} !important;
    border-radius: 8px !important;
    padding: 9px 18px !important;
    height: 42px !important;
    justify-content: center !important;
    text-align: center !important;
    margin-top: 0px !important;
}}
[data-testid="stSidebar"] .st-key-reset_btn button > div {{
    justify-content: center !important;
    width: 100% !important;
}}
.st-key-reset_btn button:hover {{
    background-color: rgba(245,166,35,0.12) !important;
}}
.side-divider {{
    margin: 0 14px 10px;
    border: none !important;
    border-top: 1px solid {ORANGE} !important;
    transform: translateY(-45px);
}}

/* sidebar filter expander */
[data-testid="stSidebar"] [data-testid="stExpander"] {{
    background-color: transparent;
    border: 1px solid {ORANGE};
    border-radius: 8px;
    margin: 0 4px -4px 4px;
    width: calc(100% - 8px);
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    color: {ORANGE} !important;
    font-weight: 700;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary:focus,
[data-testid="stSidebar"] [data-testid="stExpander"] summary:active,
[data-testid="stSidebar"] [data-testid="stExpander"] summary:focus-visible {{
    background-color: {NAVY} !important;
    color: {ORANGE} !important;
    outline: none !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{
    background-color: rgba(245, 166, 35, 0.12) !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {{
    font-weight: 800 !important; font-size: 17px !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] svg {{ fill: {ORANGE}; }}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    color: #C7CEE3 !important; font-size: 12.5px; font-weight: 700;
    margin-bottom: 2px;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    border: 1px solid #FFFFFF !important;
    min-height: 34px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span {{ color: {TEXT_DARK} !important; font-size: 13px; }}

/* ---------- MAIN AREA ---------- */
.breadcrumb {{ font-size: 14px; margin-bottom: 8px; }}
.bc-muted {{ color: #A7AEC0; }}
.bc-sep {{ color: #A7AEC0; margin: 0 4px; }}
.bc-active {{ color: {TEXT_DARK}; font-weight: 700; }}

.page-title {{ color: {TEXT_DARK}; font-weight: 800; font-size: 28px; margin: 2px 0 2px 0; }}
.page-subtitle {{ color: {TEXT_MUTED}; font-size: 14.5px; margin-bottom: 22px; }}

[data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p {{
    color: {NAVY} !important; font-weight: 700 !important; font-size: 14px;
}}
[data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    min-height: 42px !important;
}}
[data-testid="stMultiSelect"] input::placeholder {{
    color: inherit !important;
    opacity: 1 !important;
}}
/* Parameter multiselect selected tags */
[data-testid="stMultiSelect"] [data-tag] {{
    background-color: {ORANGE} !important;
    color: {NAVY} !important;
}}
/* text di dalam tag */
[data-testid="stMultiSelect"] [data-tag] span {{
    color: {NAVY} !important;
}}
/* tombol X */
[data-testid="stMultiSelect"] [data-tag] button {{
    color: {NAVY} !important;
}}
/* Filter border: normal */
[data-testid="stMultiSelect"] div[role="group"][data-rac],
[data-testid="stSelectbox"] div[role="group"][data-rac] {{
    border-color: {BORDER} !important;
}}
/* Filter border: focus */
[data-testid="stMultiSelect"] div[role="group"][data-rac]:focus-within,
[data-testid="stSelectbox"] div[role="group"][data-rac]:focus-within {{
    border-color: {ORANGE} !important;
    outline-color: {ORANGE} !important;
}}

/* ---------- KPI CARDS ---------- */
.kpi-card {{
    background-color: {CARD_BG};
    border-radius: 14px;
    padding: 16px 20px 18px 20px;
    box-shadow: 0 2px 12px rgba(20,30,60,0.07);
    border: 1px solid #F1F3F9;
    min-height: 92px;
}}
.kpi-label {{ font-size: 13px; font-weight: 700; color: #A8AFC1; margin-bottom: 8px; }}
.kpi-value {{ font-size: 26px; font-weight: 800; color: {NAVY}; }}

/* ---------- DATA TABLE ---------- */
.norm-table-wrap {{
    background-color: {CARD_BG};
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(20,30,60,0.07);
    border: 1px solid #F1F3F9;
    overflow: hidden;
}}
.norm-table-scroll {{ max-height: 480px; overflow-y: auto; }}
table.norm-table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
table.norm-table thead th {{
    position: sticky; top: 0;
    background-color: {CARD_BG};
    color: {NAVY}; font-weight: 800;
    text-align: left; padding: 14px 16px;
    border-bottom: 1px solid #F4D9A6;
    z-index: 1;
}}
table.norm-table tbody td {{
    padding: 11px 16px; color: #6B7280;
    border-bottom: 1px solid #F4D9A6;
    white-space: nowrap;
}}
table.norm-table tbody tr:hover td {{ background-color: #FFFBF2; }}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR CONTENT
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand">Norm Database</div>', unsafe_allow_html=True)

    for item in ["Dashboard", "Data", "About"]:
        if st.button(item, key=f"nav_{item.lower()}", use_container_width=True):
            st.session_state.page = item
            st.rerun()

    active_key = f"nav_{st.session_state.page.lower()}"
    st.markdown(
        f"""
    <style>
    .st-key-{active_key} button,
    .st-key-{active_key} button:hover {{
        background-color: {ORANGE} !important;
        color: {NAVY} !important;
        font-weight: 800 !important;
    }}

    .st-key-{active_key} button p {{
        color: {NAVY} !important;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="side-divider">', unsafe_allow_html=True)

    if st.session_state.page == "Dashboard":
        st.button(
            "Reset filter",
            key="reset_btn",
            use_container_width=True,
            on_click=reset_filters,
        )

        with st.expander("Filter Data", expanded=False):
            st.selectbox(
                "Category",
                ["Semua"] + filters["categories"],
                key="f_category",
            )

            st.selectbox(
                "Sub-Category",
                ["Semua"] + filters["sub_categories"],
                key="f_sub_category",
            )

            st.selectbox(
                "Detail Product",
                ["Semua"] + filters["detail_products"],
                key="f_detail_product",
            )

            st.selectbox(
                "Gender",
                ["Semua"] + filters["genders"],
                key="f_gender",
            )

            st.selectbox(
                "SES",
                ["Semua"] + filters["ses"],
                key="f_ses",
            )

            st.selectbox(
                "Occupation",
                ["Semua"] + filters["occupations"],
                key="f_occupation",
            )

            st.selectbox(
                "Test Type",
                ["Semua"] + filters["test_types"],
                key="f_test_type",
            )

            st.selectbox(
                "Methodology",
                ["Semua"] + filters["methodologies"],
                key="f_methodology",
            )

            st.selectbox(
                "Sub-Method",
                ["Semua"] + filters["sub_methods"],
                key="f_sub_method",
            )

            if age_min < age_max:
                st.slider(
                    "Actual Age",
                    min_value=age_min,
                    max_value=age_max,
                    key="f_actual_age",
                )


# =========================================================
# HELPERS
# =========================================================
def fmt_int(n):
    return f"{n:,.0f}".replace(",", ".")


def fmt_pct(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "None"
    return f"{v:.1f}%"


def fmt_score(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "-"
    return f"{v:.2f}"


def render_table(table_df):
    cols = [
        "Parameter",
        "Skala",
        "Norm Grade",
        "Base (N)",
        "TB%",
        "TB2%",
        "TB3%",
        "Mean Score",
    ]
    html = [
        '<div class="norm-table-wrap"><div class="norm-table-scroll"><table class="norm-table"><thead><tr>'
    ]
    for c in cols:
        html.append(f"<th>{c}</th>")
    html.append("</tr></thead><tbody>")
    for _, r in table_df.iterrows():
        html.append("<tr>")
        html.append(f"<td>{r['Parameter']}</td>")
        html.append(f"<td>{r['Skala']}</td>")
        html.append(f"<td>{r['Norm Grade']}</td>")
        html.append(f"<td>{fmt_int(r['Base (N)'])}</td>")
        html.append(f"<td>{fmt_pct(r['TB%'])}</td>")
        html.append(f"<td>{fmt_pct(r['TB2%'])}</td>")
        html.append(f"<td>{fmt_pct(r['TB3%'])}</td>")
        html.append(f"<td>{fmt_score(r['Mean Score'])}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def kpi_card(col, label, value):
    col.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def breadcrumb(page_name):
    st.markdown(
        f"""
    <div class="breadcrumb">
        <span class="bc-muted">Pages</span><span class="bc-sep">/</span><span class="bc-active">{page_name}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def weighted_avg(sub, col):
    valid = sub.dropna(subset=[col])
    if valid.empty or valid["Base (N)"].sum() == 0:
        return None
    return float((valid[col] * valid["Base (N)"]).sum() / valid["Base (N)"].sum())


# =========================================================
# PAGE: DASHBOARD
# =========================================================
if st.session_state.page == "Dashboard":
    breadcrumb("Dashboard")
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Top Box / Top 2 Boxes / Top 3 Boxes / Mean Score</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.multiselect(
            "Parameter",
            options=variable_names,
            key="f_parameter",
            placeholder="Semua",
        )
    with c2:
        st.selectbox("Skala", ["Semua"] + [f"{s}pts" for s in scales], key="f_skala")
    with c3:
        st.selectbox("Norm Grade", ["Semua"] + NORM_GRADES, key="f_norm_grade")

    # Sidebar filters are applied in PostgreSQL before norm calculation.
    def selected_value(key):
        value = st.session_state[key]
        return value if value != "Semua" else None

    selected_age_min, selected_age_max = st.session_state.f_actual_age
    age_min_val = selected_age_min if selected_age_min > age_min else None
    age_max_val = selected_age_max if selected_age_max < age_max else None

    df = load_norms(
        gender=selected_value("f_gender"),
        ses=selected_value("f_ses"),
        category=selected_value("f_category"),
        sub_category=selected_value("f_sub_category"),
        detail_product=selected_value("f_detail_product"),
        occupation=selected_value("f_occupation"),
        test_type=selected_value("f_test_type"),
        methodology=selected_value("f_methodology"),
        sub_method=selected_value("f_sub_method"),
        age_min=age_min_val,
        age_max=age_max_val,
    )

    # Filter in-memory: parameter, skala, norm_grade (kolom-kolom ini ada di DataFrame)
    fdf = df.copy()
    if st.session_state.f_parameter:
        fdf = fdf[fdf["Parameter"].isin(st.session_state.f_parameter)]
    if st.session_state.f_skala != "Semua":
        fdf = fdf[fdf["Skala"] == st.session_state.f_skala]
    if st.session_state.f_norm_grade != "Semua":
        fdf = fdf[fdf["Norm Grade"] == st.session_state.f_norm_grade]

    base_n = int(fdf["Base (N)"].sum()) if not fdf.empty else 0
    tb = weighted_avg(fdf, "TB%")
    tb2 = weighted_avg(fdf, "TB2%")
    tb3 = weighted_avg(fdf, "TB3%")
    mean_score = weighted_avg(fdf, "Mean Score")

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_card(k1, "Base (N)", fmt_int(base_n))
    kpi_card(k2, "Top Box %", fmt_pct(tb))
    kpi_card(k3, "Top 2 Box %", fmt_pct(tb2))
    kpi_card(k4, "Top 3 Box %", fmt_pct(tb3))
    kpi_card(k5, "Mean Score", fmt_score(mean_score))

    st.write("")
    if fdf.empty:
        st.info("Tidak ada data untuk kombinasi filter ini.")
    else:
        render_table(fdf)

# =========================================================
# PAGE: DATA
# =========================================================
elif st.session_state.page == "Data":
    breadcrumb("Data")
    st.markdown('<div class="page-title">Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Data respons survei</div>', unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Total Project", fmt_int(stats["projects"]))
    kpi_card(k2, "Total Responden", fmt_int(stats["respondents"]))
    kpi_card(k3, "Total Response", fmt_int(stats["responses"]))
    kpi_card(k4, "Total Parameter", fmt_int(stats["variables"]))

    st.write("")
    # Halaman Data selalu tampilkan data global (tanpa filter sidebar)
    render_table(load_norms())

# =========================================================
# PAGE: ABOUT
# =========================================================
else:
    breadcrumb("About")
    st.markdown('<div class="page-title">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Informasi Dashboard</div>', unsafe_allow_html=True
    )

    st.markdown(
        f"""
    <div class="kpi-card" style="min-height:auto;">
        <div style="color:{TEXT_DARK}; font-size:14.5px; line-height:1.7;">
            <b>Norm Database</b> adalah dashboard internal untuk menelusuri data norma hasil survei
            sensori &amp; konsumen lintas proyek. Gunakan menu <b>Dashboard</b> untuk melihat ringkasan
            Top Box / Top 2 Box / Top 3 Box / Mean Score per parameter, dan menu <b>Data</b> untuk
            melihat keseluruhan respons survei.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
