import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Oil & Gas Production Intelligence",
    page_icon="🛢️",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🛢️ Oil & Gas Production Intelligence Dashboard")

st.write(
    "Dashboard untuk monitoring produksi minyak dan gas "
    "berdasarkan data Volve Field."
)

# =========================================================
# LOAD DATA
# =========================================================

production = pd.read_csv(
    "data/volve_production_clean.csv"
)

well_kpi = pd.read_csv(
    "data/volve_well_kpi.csv"
)

anomaly = pd.read_csv(
    "data/volve_anomaly_report.csv"
)

# =========================================================
# DATA PREPARATION
# =========================================================

production["DATEPRD"] = pd.to_datetime(
    production["DATEPRD"],
    errors="coerce"
)

production["BORE_OIL_VOL"] = pd.to_numeric(
    production["BORE_OIL_VOL"],
    errors="coerce"
)

production["BORE_GAS_VOL"] = pd.to_numeric(
    production["BORE_GAS_VOL"],
    errors="coerce"
)

production["BORE_WAT_VOL"] = pd.to_numeric(
    production["BORE_WAT_VOL"],
    errors="coerce"
)
# Konversi tanggal anomaly
anomaly["DATEPRD"] = pd.to_datetime(
    anomaly["DATEPRD"], errors="coerce"
)
# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.header("🎛️ Dashboard Filter")

# -------------------------
# Well Filter
# -------------------------

well_list = sorted(
    production["NPD_WELL_BORE_NAME"]
    .dropna()
    .unique()
)

selected_well = st.sidebar.selectbox(
    "Select Well",
    ["All Wells"] + well_list
)

# -------------------------
# Date Filter
# -------------------------

min_date = production["DATEPRD"].min().date()
max_date = production["DATEPRD"].max().date()

date_range = st.sidebar.date_input(
    "Production Period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
# =========================================================
# APPLY GLOBAL FILTER
# =========================================================

filtered_production = production.copy()

# -------------------------
# Filter Well
# -------------------------

if selected_well != "All Wells":

    filtered_production = filtered_production[
        filtered_production["NPD_WELL_BORE_NAME"]
        == selected_well
    ].copy()


# -------------------------
# Filter Date
# -------------------------

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_production = filtered_production[
        (filtered_production["DATEPRD"] >= start_date)
        &
        (filtered_production["DATEPRD"] <= end_date)
    ].copy()


# =========================================================
# APPLY ANOMALY FILTER
# =========================================================

filtered_anomaly = anomaly.copy()

# -------------------------
# Filter Well
# -------------------------

if selected_well != "All Wells":

    filtered_anomaly = filtered_anomaly[
        filtered_anomaly["NPD_WELL_BORE_NAME"]
        == selected_well
    ].copy()


# -------------------------
# Filter Date
# -------------------------

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_anomaly = filtered_anomaly[
        (filtered_anomaly["DATEPRD"] >= start_date)
        &
        (filtered_anomaly["DATEPRD"] <= end_date)
    ].copy()

# =========================================================
# SIDEBAR SUMMARY
# =========================================================

st.sidebar.divider()

st.sidebar.markdown("### 📌 Current Filter")

st.sidebar.write(
    f"Well: **{selected_well}**"
)

if len(date_range) == 2:

    st.sidebar.write(
        f"Period: **{date_range[0]} → {date_range[1]}**"
    )

st.sidebar.write(
    f"Records: **{len(filtered_production):,}**"
)

# =========================================================
# DATASET INFORMATION
# =========================================================

st.subheader("Dataset")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Production Records",
        f"{len(production):,}"
    )

with col2:
    st.metric(
        "Wells",
        f"{production['NPD_WELL_BORE_NAME'].nunique():,}"
    )

with col3:
    st.metric(
        "Anomaly Records",
        f"{len(anomaly):,}"
    )

# =========================================================
# PRODUCTION KPI
# =========================================================

st.subheader("Production KPI")

total_oil = filtered_production["BORE_OIL_VOL"].sum()
total_gas = filtered_production["BORE_GAS_VOL"].sum()
total_water = filtered_production["BORE_WAT_VOL"].sum()

avg_oil = filtered_production["BORE_OIL_VOL"].mean()
avg_gas = filtered_production["BORE_GAS_VOL"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Oil",
        f"{total_oil:,.2f}"
    )

with col2:
    st.metric(
        "Total Gas",
        f"{total_gas:,.2f}"
    )

with col3:
    st.metric(
        "Total Water",
        f"{total_water:,.2f}"
    )

with col4:
    st.metric(
        "Average Daily Oil",
        f"{avg_oil:,.2f}"
    )

with col5:
    st.metric(
        "Average Daily Gas",
        f"{avg_gas:,.2f}"
    )
# =========================================================
# PRODUCTION DATA
# =========================================================

st.subheader("Production Data")

st.dataframe(
    filtered_production.head(10),
    use_container_width=True
)

# =========================================================
# PRODUCTION TREND
# =========================================================

st.subheader("📈 Production Trend")

daily_production = (
    filtered_production
    .groupby("DATEPRD")[
        [
            "BORE_OIL_VOL",
            "BORE_GAS_VOL",
            "BORE_WAT_VOL"
        ]
    ]
    .sum()
    .reset_index()
)

st.markdown("### 🛢️ Oil Production")

st.line_chart(
    daily_production.set_index("DATEPRD")["BORE_OIL_VOL"],
    use_container_width=True
)

st.markdown("### 🔥 Daily Gas Production")

st.line_chart(
    daily_production.set_index("DATEPRD")["BORE_GAS_VOL"],
    use_container_width=True
)

st.markdown("### 💧 Daily Water Production")

st.line_chart(
    daily_production.set_index("DATEPRD")["BORE_WAT_VOL"],
    use_container_width=True
)

# =========================================================
# WELL PERFORMANCE
# =========================================================

st.subheader("🏭 Well Performance")

well_performance = (
    filtered_production
    .groupby("NPD_WELL_BORE_NAME")[
        [
            "BORE_OIL_VOL",
            "BORE_GAS_VOL",
            "BORE_WAT_VOL"
        ]
    ]
    .sum()
    .reset_index()
)

# -------------------------
# Table
# -------------------------

st.markdown("### Production by Well")

st.dataframe(
    well_performance.sort_values(
        "BORE_OIL_VOL",
        ascending=False
    ),
    use_container_width=True
)

# -------------------------
# Oil by Well
# -------------------------

st.markdown("### 🛢️ Total Oil Production by Well")

oil_by_well = (
    well_performance
    .set_index("NPD_WELL_BORE_NAME")["BORE_OIL_VOL"]
    .sort_values(ascending=False)
)

st.bar_chart(
    oil_by_well,
    use_container_width=True
)

# -------------------------
# Gas by Well
# -------------------------

st.markdown("### 🔥 Total Gas Production by Well")

gas_by_well = (
    well_performance
    .set_index("NPD_WELL_BORE_NAME")["BORE_GAS_VOL"]
    .sort_values(ascending=False)
)

st.bar_chart(
    gas_by_well,
    use_container_width=True
)

# -------------------------
# Water by Well
# -------------------------

st.markdown("### 💧 Total Water Production by Well")

water_by_well = (
    well_performance
    .set_index("NPD_WELL_BORE_NAME")["BORE_WAT_VOL"]
    .sort_values(ascending=False)
)

st.bar_chart(
    water_by_well,
    use_container_width=True
)

# =========================================================
# FILTERED PRODUCTION KPI
# =========================================================

st.subheader("🔎 Selected Production Analysis")

filtered_oil = filtered_production["BORE_OIL_VOL"].sum()
filtered_gas = filtered_production["BORE_GAS_VOL"].sum()
filtered_water = filtered_production["BORE_WAT_VOL"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Selected Oil",
        f"{filtered_oil:,.2f}"
    )

with col2:
    st.metric(
        "Selected Gas",
        f"{filtered_gas:,.2f}"
    )

with col3:
    st.metric(
        "Selected Water",
        f"{filtered_water:,.2f}"
    )

# =========================================================
# ANOMALY MONITORING
# =========================================================

st.subheader("🚨 Anomaly Monitoring")


# =========================================================
# ANOMALY KPI
# =========================================================

total_anomaly = len(filtered_anomaly)

affected_wells = (
    filtered_anomaly["NPD_WELL_BORE_NAME"]
    .nunique()
)


col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Anomaly",
        f"{total_anomaly:,}"
    )

with col2:

    st.metric(
        "Affected Wells",
        f"{affected_wells:,}"
    )

with col3:

    anomaly_rate = (
        total_anomaly / len(filtered_production) * 100
        if len(filtered_production) > 0
        else 0
    )

    st.metric(
        "Anomaly Rate",
        f"{anomaly_rate:.2f}%"
    )


# =========================================================
# ANOMALY BY WELL
# =========================================================

st.markdown("### 🚨 Anomaly by Well")


if not filtered_anomaly.empty:

    anomaly_by_well = (
        filtered_anomaly
        .groupby("NPD_WELL_BORE_NAME")
        .size()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        anomaly_by_well,
        use_container_width=True
    )

else:

    st.info(
        "Tidak ditemukan anomaly pada "
        "well dan periode yang dipilih."
    )


# =========================================================
# ANOMALY DETAILS
# =========================================================

st.markdown("### 🔎 Anomaly Details")


if not filtered_anomaly.empty:

    st.dataframe(
        filtered_anomaly.sort_values(
            "DATEPRD",
            ascending=False
        ),
        use_container_width=True
    )

else:

    st.info(
        "Tidak ada data anomaly untuk "
        "filter yang dipilih."
    )

# =========================================================
# PRODUCTION VS ANOMALY
# =========================================================

st.subheader("📊 Production vs Anomaly Monitoring")


# =========================================================
# FILTER WELL SESUAI SIDEBAR
# =========================================================

if selected_well == "All Wells":

    well_production = filtered_production.copy()

    well_anomaly = anomaly.copy()

else:

    well_production = filtered_production[
        filtered_production["NPD_WELL_BORE_NAME"]
        == selected_well
    ].copy()

    well_anomaly = anomaly[
        anomaly["NPD_WELL_BORE_NAME"]
        == selected_well
    ].copy()


# =========================================================
# DAILY PRODUCTION
# =========================================================

well_daily = (
    well_production
    .groupby("DATEPRD")[
        [
            "BORE_OIL_VOL",
            "BORE_GAS_VOL",
            "BORE_WAT_VOL"
        ]
    ]
    .sum()
    .reset_index()
)


# =========================================================
# WELL KPI
# =========================================================

total_well_oil = well_daily["BORE_OIL_VOL"].sum()
total_well_gas = well_daily["BORE_GAS_VOL"].sum()
total_well_water = well_daily["BORE_WAT_VOL"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Oil",
        f"{total_well_oil:,.2f}"
    )

with col2:
    st.metric(
        "Total Gas",
        f"{total_well_gas:,.2f}"
    )

with col3:
    st.metric(
        "Total Water",
        f"{total_well_water:,.2f}"
    )


# =========================================================
# WELL ANOMALY
# =========================================================

well_anomaly["DATEPRD"] = pd.to_datetime(
    well_anomaly["DATEPRD"],
    errors="coerce"
)

st.markdown("### 🚨 Selected Well Anomaly")

st.metric(
    "Anomaly Records",
    f"{len(well_anomaly):,}"
)


# =========================================================
# ANOMALY DATE MATCHING
# =========================================================

well_daily["DATEPRD"] = pd.to_datetime(
    well_daily["DATEPRD"],
    errors="coerce"
)

anomaly_dates = (
    well_anomaly["DATEPRD"]
    .dropna()
    .dt.normalize()
    .drop_duplicates()
)

well_daily["ANOMALY"] = (
    well_daily["DATEPRD"]
    .dt.normalize()
    .isin(anomaly_dates)
)


# =========================================================
# OIL PRODUCTION VS ANOMALY
# =========================================================

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=well_daily["DATEPRD"],
        y=well_daily["BORE_OIL_VOL"],
        mode="lines",
        name="Oil Production"
    )
)

anomaly_production = well_daily[
    well_daily["ANOMALY"]
].copy()

if not anomaly_production.empty:

    fig.add_trace(
        go.Scatter(
            x=anomaly_production["DATEPRD"],
            y=anomaly_production["BORE_OIL_VOL"],
            mode="markers",
            name="Anomaly",
            marker=dict(
                size=11,
                color="red",
                symbol="circle",
                line=dict(
                    width=2,
                    color="white"
                )
            )
        )
    )

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# ANOMALY DATES
# =========================================================

if not anomaly_production.empty:

    st.markdown("### ⚠️ Dates with Anomaly")

    anomaly_period = well_daily[
        well_daily["ANOMALY"]
    ][
        [
            "DATEPRD",
            "BORE_OIL_VOL",
            "BORE_GAS_VOL",
            "BORE_WAT_VOL"
        ]
    ].copy()

    st.dataframe(
        anomaly_period,
        use_container_width=True
    )

else:

    st.info(
        "Tidak ditemukan anomaly pada "
        "well dan periode yang dipilih."
    )