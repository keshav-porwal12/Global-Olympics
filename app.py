import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Global Olympic Performance Analysis", page_icon="🏅", layout="wide")

MEDAL_URL = "https://raw.githubusercontent.com/ismayc/olympic-moderndive-data/main/data/medal_table_summary.csv"
EDITION_URL = "https://raw.githubusercontent.com/ismayc/olympic-moderndive-data/main/data/edition_metadata.csv"

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f4f7fb; padding: 14px 16px; border-radius: 12px; border: 1px solid #e2e8f0;}
h1, h2, h3 {color: #173b65;}
</style>
""", unsafe_allow_html=True)

st.title("🏅 Global Olympic Sports Performance Analysis")
st.caption("Interactive Tableau-style analytics dashboard • Olympic editions 1992–2026 • Summer and Winter Games")
st.info("Medal totals use an edition-country medal table (one medal per event result, rather than one medal per team roster member). Investment figures are not included because a comparable, sourced investment dataset is not bundled.")

@st.cache_data(show_spinner=False)
def load_from_url(url):
    return pd.read_csv(url)

def normalize_medals(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    aliases = {"year":"year", "season":"season", "country":"country", "noc":"noc",
               "gold":"gold", "silver":"silver", "bronze":"bronze", "total":"total",
               "games":"games", "notes":"notes"}
    missing = [c for c in ["year","season","country","gold","silver","bronze"] if c not in df.columns]
    if missing:
        raise ValueError("The medal table must include these columns: " + ", ".join(missing))
    for c in ["year","gold","silver","bronze"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["year","country"])
    df["year"] = df["year"].astype(int)
    for c in ["gold","silver","bronze"]:
        df[c] = df[c].fillna(0).astype(int)
    if "total" not in df.columns:
        df["total"] = df["gold"] + df["silver"] + df["bronze"]
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(df["gold"]+df["silver"]+df["bronze"])
    if "games" not in df.columns:
        df["games"] = df["year"].astype(str) + " " + df["season"].astype(str)
    if "noc" not in df.columns:
        df["noc"] = ""
    if "notes" not in df.columns:
        df["notes"] = ""
    return df

def normalize_editions(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "year" not in df.columns:
        return pd.DataFrame()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data(show_spinner=False)
def get_remote_data():
    medals = normalize_medals(load_from_url(MEDAL_URL))
    editions = normalize_editions(load_from_url(EDITION_URL))
    return medals, editions

with st.sidebar:
    st.header("Data & filters")
    st.write("Default: load the documented public medal-table dataset.")
    uploaded_medals = st.file_uploader("Optional: upload medal table CSV", type=["csv"])
    uploaded_editions = st.file_uploader("Optional: upload edition metadata CSV", type=["csv"])
    use_demo = st.checkbox("Use built-in demo data if online source is unavailable", value=True)
    st.divider()
    st.caption("Expected medal CSV columns: year, season, country, gold, silver, bronze; total is optional.")

demo_rows = [
    [1992,"Summer","United States",37,34,37,108,"1992 Summer"],
    [1992,"Summer","Unified Team",45,38,29,112,"1992 Summer"],
    [1992,"Summer","China",16,22,16,54,"1992 Summer"],
    [1992,"Summer","Germany",33,21,28,82,"1992 Summer"],
    [1992,"Summer","Cuba",14,6,11,31,"1992 Summer"],
    [1996,"Summer","United States",44,32,25,101,"1996 Summer"],
    [1996,"Summer","Russia",26,21,16,63,"1996 Summer"],
    [1996,"Summer","Germany",20,18,27,65,"1996 Summer"],
    [2000,"Summer","United States",37,24,32,93,"2000 Summer"],
    [2000,"Summer","Russia",32,28,29,89,"2000 Summer"],
    [2000,"Summer","China",28,16,15,59,"2000 Summer"],
    [2004,"Summer","United States",36,39,26,101,"2004 Summer"],
    [2004,"Summer","China",32,17,14,63,"2004 Summer"],
    [2008,"Summer","China",48,22,30,100,"2008 Summer"],
    [2008,"Summer","United States",36,39,37,112,"2008 Summer"],
    [2012,"Summer","United States",46,28,30,104,"2012 Summer"],
    [2012,"Summer","China",38,31,22,91,"2012 Summer"],
    [2016,"Summer","United States",46,37,38,121,"2016 Summer"],
    [2016,"Summer","Great Britain",27,23,17,67,"2016 Summer"],
    [2020,"Summer","United States",39,41,33,113,"2020 Summer"],
    [2020,"Summer","China",38,32,19,89,"2020 Summer"],
    [2024,"Summer","United States",40,44,42,126,"2024 Summer"],
    [2024,"Summer","China",40,27,24,91,"2024 Summer"],
    [2024,"Summer","Japan",20,12,13,45,"2024 Summer"],
    [1992,"Winter","Unified Team",9,6,8,23,"1992 Winter"],
    [1992,"Winter","Germany",10,10,6,26,"1992 Winter"],
    [1994,"Winter","Norway",10,11,5,26,"1994 Winter"],
    [1998,"Winter","Germany",12,9,8,29,"1998 Winter"],
    [2002,"Winter","Norway",13,5,7,25,"2002 Winter"],
    [2006,"Winter","Germany",11,12,6,29,"2006 Winter"],
    [2010,"Winter","United States",9,15,13,37,"2010 Winter"],
    [2014,"Winter","Russia",11,9,9,29,"2014 Winter"],
    [2018,"Winter","Norway",14,14,11,39,"2018 Winter"],
    [2022,"Winter","Norway",16,8,13,37,"2022 Winter"],
    [2026,"Winter","Norway",18,12,11,41,"2026 Winter"]
]
demo = pd.DataFrame(demo_rows, columns=["year","season","country","gold","silver","bronze","total","games"])
demo["noc"] = ""
demo["notes"] = "DEMO FALLBACK — replace with complete sourced medal table"

try:
    if uploaded_medals is not None:
        medal_raw = pd.read_csv(uploaded_medals)
        medals = normalize_medals(medal_raw)
        data_status = "Uploaded CSV"
    else:
        medals, editions = get_remote_data()
        data_status = "Live public source"
except Exception as e:
    if not use_demo:
        st.error("Could not load the online source. Upload a medal table CSV or enable the demo fallback.")
        st.stop()
    medals = demo.copy()
    editions = pd.DataFrame()
    data_status = "Built-in demo subset (not full dataset)"
    st.warning("The online dataset could not be reached. Showing a small built-in demo subset. Upload a full sourced CSV for final results.")

if uploaded_medals is not None:
    try:
        medals = normalize_medals(pd.read_csv(uploaded_medals))
    except Exception as e:
        st.error(f"Could not read the uploaded medal CSV: {e}")
        st.stop()

if uploaded_editions is not None:
    try:
        editions = normalize_editions(pd.read_csv(uploaded_editions))
    except Exception as e:
        st.warning(f"Could not read edition metadata: {e}")
        editions = pd.DataFrame()

medals = medals[(medals["year"] >= 1992) & (medals["year"] <= 2026)].copy()
if medals.empty:
    st.error("No rows remain for 1992–2026. Check the year column in your CSV.")
    st.stop()

with st.sidebar:
    season_options = ["All"] + sorted(medals["season"].dropna().astype(str).unique().tolist())
    season = st.selectbox("Season", season_options)
    countries = sorted(medals["country"].dropna().astype(str).unique().tolist())
    selected_countries = st.multiselect("Countries (optional)", countries, default=[])
    min_year, max_year = int(medals["year"].min()), int(medals["year"].max())
    year_range = st.slider("Year range", min_value=min_year, max_value=max_year, value=(max(1992,min_year), min(2026,max_year)))
    top_n = st.slider("Top countries", min_value=5, max_value=20, value=10)

f = medals[(medals["year"] >= year_range[0]) & (medals["year"] <= year_range[1])].copy()
if season != "All":
    f = f[f["season"].astype(str) == season]
if selected_countries:
    f = f[f["country"].isin(selected_countries)]
if f.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Country edition medal records: each row is a country at an edition.
k1, k2, k3, k4 = st.columns(4)
k1.metric("Medals in selected data", f"{int(f['total'].sum()):,}")
k2.metric("Countries / NOCs", f"{f['country'].nunique():,}")
k3.metric("Olympic editions", f"{f['games'].nunique():,}")
k4.metric("Years covered", f"{f['year'].min()}–{f['year'].max()}")

tabs = st.tabs(["Global Overview", "Country Comparison", "Sport / Athlete Extension", "Investment & Regional Analysis", "Data Notes"])

with tabs[0]:
    left, right = st.columns([1.15, 1])
    with left:
        top = f.groupby("country", as_index=False)["total"].sum().sort_values("total", ascending=False).head(top_n)
        fig = px.bar(top.sort_values("total"), x="total", y="country", orientation="h",
                     title=f"Top {top_n} Countries by Total Medals",
                     labels={"total":"Total medals","country":"Country"}, text="total")
        fig.update_layout(height=460, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        trend = f.groupby(["year","season"], as_index=False)["total"].sum()
        fig = px.line(trend, x="year", y="total", color="season", markers=True,
                      title="Medal totals across Olympic editions",
                      labels={"year":"Year","total":"Medal-table total","season":"Season"})
        fig.update_layout(height=460, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)
    medals_long = f.melt(id_vars=["year","season","games","country"], value_vars=["gold","silver","bronze"],
                         var_name="medal_type", value_name="count")
    medals_long["medal_type"] = medals_long["medal_type"].str.title()
    medal_mix = medals_long.groupby("medal_type", as_index=False)["count"].sum()
    fig = px.pie(medal_mix, names="medal_type", values="count", hole=0.55, title="Gold / Silver / Bronze composition")
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    country_summary = f.groupby("country", as_index=False)[["gold","silver","bronze","total"]].sum()
    country_summary = country_summary.sort_values(["gold","total"], ascending=False)
    fig = px.bar(country_summary.head(top_n).sort_values("gold"), x="gold", y="country", orientation="h",
                 title="Gold Medal Comparison", text="gold", labels={"gold":"Gold medals","country":"Country"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(country_summary, use_container_width=True, hide_index=True)
    st.download_button("Download filtered country summary CSV",
                       country_summary.to_csv(index=False).encode("utf-8"),
                       file_name="olympic_country_summary.csv", mime="text/csv")

with tabs[2]:
    st.subheader("Sport and athlete-level analysis")
    st.write("The medal-table file is country-by-edition data, so it does not contain sport or athlete detail. Upload an athlete-event CSV in a future extension to activate sport-level analysis.")
    st.markdown("**Recommended athlete dataset fields:** `year`, `season`, `noc`, `country`, `athlete_id`, `sport`, `event`, `medal`.")
    st.markdown("**Suggested charts once athlete data is connected:** medals by sport, unique athletes by edition, country × sport heatmap, and medal-winning athlete share.")
    st.link_button("Open documented athlete-event dataset", "https://github.com/moderndive/olympicAthletes")

with tabs[3]:
    st.subheader("Investment vs. medal outcomes")
    st.warning("No investment data is bundled. This project deliberately avoids inventing country spending values or regional efficiency percentages.")
    st.write("To enable this analysis, prepare a CSV with: `country`, `year`, `investment_amount`, `currency`, `investment_definition`, and `source_url`. Ideally normalize currency and inflation, and align spending years with the Olympic cycle.")
    st.subheader("Regional analysis")
    st.write("A country-to-region mapping is also required. Define regions consistently and document how transcontinental countries and historical NOCs are assigned.")
    st.markdown("A valid future scatter plot can use investment amount on the x-axis, total medals on the y-axis, and country as the label. Treat the relationship as correlation, not proof of causation.")

with tabs[4]:
    st.subheader("Dataset status")
    st.write(f"**Source mode:** {data_status}")
    st.write(f"**Rows in selected year window before filters:** {len(medals):,}")
    st.write("**Counting rule:** The intended source is an edition-country medal table, so team medals are counted by medal-table convention rather than by the number of athletes on a roster.")
    st.write("**Time range:** 1992–2026. The year 2026 is a Winter Olympic edition; there is no 2026 Summer Olympic Games edition.")
    st.write("**Caveats:** Historical NOCs and country names change. Olympic medal totals alone cannot explain training systems, investment, participation access, or causation.")
    st.dataframe(f.head(100), use_container_width=True, hide_index=True)

st.divider()
st.caption("Project source: olympicAthletes / olympic-moderndive-data by Chester Ismay and contributors; see source links and license before redistribution.")
st.caption("This dashboard is a student project starter. Verify all conclusions against the selected dataset and cite the data source in your submission.")
