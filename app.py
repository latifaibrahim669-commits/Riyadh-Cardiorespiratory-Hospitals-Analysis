import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Set working directory safely
try:
    os.chdir(r"C:\Users\Latif\Desktop\Epsilon Data Analysis With Python Project")
except Exception:
    pass

# 1. Page Configuration
st.set_page_config(
    page_title="Riyadh Cardiorespiratory Dashboard", page_icon="🏥", layout="wide"
)

# 2. Custom CSS to style the Sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #038C4C;
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] span {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

PRIMARY_GREEN = "#038C4C"
GOLD_ACCENT = "#A69563"
LIGHT_GREEN = "#49A684"


# 3. Load and preprocess data
@st.cache_data
def load_data():
    file_path = r"Cleaned Riyadh Cardiorespiratory Hospital Admissions.csv"
    df = pd.read_csv(file_path)
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["daily_medication_dosage"] = df["daily_medication_dosage"].round(2)
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset file or incorrect path. Details: {e}")
    st.stop()

df["hour"] = df["admission_date"].dt.hour
df["month"] = df["admission_date"].dt.month
df["year"] = df["admission_date"].dt.year

# 4. Sidebar Navigation and Global Filters (الترتيب المطلوب تماماً)
st.sidebar.image("MOH-1.png", use_container_width=True)
st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Page:",
    (
        "1. Facility & Operational Performance Analysis",
        "2. Temporal & Seasonal Trend Analysis",
        "3. Patient Demographics & Epidemiological Insights",
        "4. Clinical Severity, Comorbidities, & Medication Analysis",
        "5. Readmission & Emergency Utilization (Risk Drivers)",
    ),
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Global Data Filters")

all_hospitals = df["hospital_name"].unique()
selected_hospital = st.sidebar.multiselect(
    "Select Hospital:", options=all_hospitals, default=all_hospitals
)

all_conditions = df["condition_type"].unique()
selected_condition = st.sidebar.multiselect(
    "Select Condition Type:", options=all_conditions, default=all_conditions
)

# --- فلتر التاريخ (Date Range Filter) في الشريط الجانبي ---
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Range Filter")
min_date = df["admission_date"].min().date()
max_date = df["admission_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = df[
        (df["hospital_name"].isin(selected_hospital))
        & (df["condition_type"].isin(selected_condition))
        & (df["admission_date"].dt.date >= start_date)
        & (df["admission_date"].dt.date <= end_date)
    ]
else:
    filtered_df = df[
        (df["hospital_name"].isin(selected_hospital))
        & (df["condition_type"].isin(selected_condition))
    ]

if filtered_df.empty:
    st.warning(
        "⚠️ No data matches the current filter selection. Please adjust the filters in the sidebar."
    )
    st.stop()


# ==========================================
# العنوان الرئيسي في منتصف الصفحة والصورة تحته مباشرة
# ==========================================
st.markdown(
    f"<h1 style='text-align: center; color: {PRIMARY_GREEN};'>Riyadh Cardio-respiratory Hospital Admissions Analysis</h1>",
    unsafe_allow_html=True,
)

col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
with col_img2:
    st.image("heart.jpeg", use_container_width=True)

st.markdown("---")


# ==============================================================================
# عرض المحتوى والرسوم البيانية مرتبة حسب الترتيب الجديد للـ if / elif
# ==============================================================================

if page == "1. Facility & Operational Performance Analysis":
    st.markdown(
        f"<h2 style='color: {PRIMARY_GREEN};'>🏥 Facility & Operational Performance Analysis</h2>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Admissions", f"{filtered_df['admission_count'].sum():,}")
    col2.metric(
        "Avg Length of Stay (Days)",
        f"{filtered_df['length_of_stay_avg'].mean():.1f}",
    )
    col3.metric(
        "Total Emergency Visits",
        f"{filtered_df['emergency_visit_count'].sum():,}",
    )
    col4.metric("Active Hospitals", len(filtered_df["hospital_name"].unique()))

    st.markdown("---")
    hospital_summary = (
        filtered_df.groupby("hospital_name")
        .agg(
            {
                "admission_count": "sum",
                "length_of_stay_avg": "mean",
                "emergency_visit_count": "sum",
            }
        )
        .reset_index()
    )

    fig_hosp = px.bar(
        hospital_summary,
        x="hospital_name",
        y=["admission_count", "emergency_visit_count"],
        barmode="group",
        color_discrete_sequence=["#49A684", "#A69563"],
        title="Total Admissions and Emergency Visits by Hospital",
        text_auto=True,
        height=500,
    )
    fig_hosp.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_hosp, use_container_width=True)

    fig_hosp_len = px.bar(
        hospital_summary,
        x="hospital_name",
        y=["length_of_stay_avg"],
        barmode="group",
        color_discrete_sequence=["#038C4C"],
        title="Average of length of admission days by Hospital",
        text_auto=True,
        height=400,
    )
    fig_hosp_len.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_hosp_len, use_container_width=True)


elif page == "2. Temporal & Seasonal Trend Analysis":
    st.markdown(
        f"<h2 style='color: {PRIMARY_GREEN};'>📈 Temporal & Seasonal Trend Analysis</h2>",
        unsafe_allow_html=True,
    )

    yearly_trend = (
        filtered_df.groupby("year")[
            ["admission_count", "emergency_visit_count"]
        ]
        .sum()
        .reset_index()
    )
    yearly_trend.rename(columns={"year": "Year"}, inplace=True)

    fig_pattern = px.line(
        yearly_trend,
        x="Year",
        y=["admission_count", "emergency_visit_count"],
        color_discrete_sequence=["#49A684", "#A69563"],
        markers=True,
    )
    fig_pattern.update_layout(xaxis=dict(tickmode="linear", dtick=1))
    fig_pattern.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_pattern, use_container_width=True)

    monthly_pattern = (
        filtered_df.groupby("month")["admission_count"].mean().reset_index()
    )
    monthly_pattern.rename(columns={"month": "Month"}, inplace=True)

    fig_mon = px.line(
        monthly_pattern,
        x="Month",
        y="admission_count",
        title="(Admission Monthly Pattern)",
        color_discrete_sequence=["#A69563"],
        labels={"admission_count": "Average admission per month"},
        markers=True,
    )
    fig_mon.update_xaxes(tickmode="linear", tick0=1, dtick=1)
    fig_mon.update_layout(plot_bgcolor="white", paper_bgcolor="white")

    Hour_pattern = (
        filtered_df.groupby("hour")["admission_count"].mean().reset_index()
    )
    Hour_pattern.rename(columns={"hour": "Hour"}, inplace=True)

    fig_hour = px.line(
        Hour_pattern,
        x="Hour",
        y="admission_count",
        title="(Admission Hourly Pattern)",
        color_discrete_sequence=["#A69563"],
        labels={"admission_count": "Average admission per hour"},
        markers=True,
    )
    fig_hour.update_xaxes(
        range=[-0.5, 23.5], tickmode="linear", tick0=1, dtick=1
    )
    fig_hour.update_layout(plot_bgcolor="white", paper_bgcolor="white")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_mon, use_container_width=True)
    with c2:
        st.plotly_chart(fig_hour, use_container_width=True)

    if "seasonal_indicator" in filtered_df.columns:
        monthly_seasonal_df = (
            filtered_df.groupby(
                ["month", "seasonal_indicator", "condition_type"]
            )["admission_count"]
            .mean()
            .reset_index()
        )
        monthly_seasonal_df.rename(columns={"month": "Month"}, inplace=True)

        fig_env = px.line(
            monthly_seasonal_df,
            x="Month",
            y="admission_count",
            color="condition_type",
            facet_row="seasonal_indicator",
            title="Respiratory & Cardiovascular Admissions Across Seasons",
            template="plotly_white",
            height=1100,
        )
        fig_env.update_xaxes(matches=None)
        fig_env.update_yaxes(matches=None)
        fig_env.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_env, use_container_width=True)


elif page == "3. Patient Demographics & Epidemiological Insights":
    st.markdown(
        f"<h2 style='color: {PRIMARY_GREEN};'>👥 Patient Demographics & Epidemiological Insights</h2>",
        unsafe_allow_html=True,
    )

    if (
        "patient_age_group" in filtered_df.columns
        and "patient_gender" in filtered_df.columns
    ):
        age_df = (
            filtered_df.groupby(
                ["patient_age_group", "condition_type", "patient_gender"]
            )["admission_count"]
            .sum()
            .reset_index()
        )
        age_con_fig = px.bar(
            age_df,
            x="patient_age_group",
            y="admission_count",
            color="condition_type",
            barmode="group",
            facet_row="patient_gender",
            template="plotly_white",
            height=1000,
            title="Admissions by Age Group and Condition Type across Genders",
        )
        age_con_fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(age_con_fig, use_container_width=True)


elif page == "4. Clinical Severity, Comorbidities, & Medication Analysis":
    st.markdown(
        f"<h2 style='color: {PRIMARY_GREEN};'>🩺 Clinical Severity, Comorbidities, & Medication Analysis</h2>",
        unsafe_allow_html=True,
    )

    if (
        "patient_age_group" in filtered_df.columns
        and "severity_level" in filtered_df.columns
    ):
        severe_df = (
            filtered_df.groupby(
                [
                    "patient_age_group",
                    "severity_level",
                    "condition_type",
                    "patient_gender",
                ]
            )["admission_count"]
            .sum()
            .reset_index()
        )
        gender_con_fig = px.bar(
            severe_df,
            x="patient_age_group",
            y="admission_count",
            color="severity_level",
            facet_col="condition_type",
            facet_row="patient_gender",
            barmode="group",
            template="plotly_white",
            height=700,
            width=1500,
            text_auto=True,
            title="Admissions by Age Group, Severity Level, Condition Type and Gender",
        )
        gender_con_fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(gender_con_fig, use_container_width=True)

    corr_cols = [
        "admission_count",
        "readmission_count",
        "length_of_stay_avg",
        "comorbid_conditions_count",
        "daily_medication_dosage",
        "emergency_visit_count",
    ]
    available_corr_cols = [col for col in corr_cols if col in filtered_df.columns]
    if len(available_corr_cols) > 1:
        new_corr_matrix = filtered_df[available_corr_cols].corr()
        new_fig_corr = px.imshow(
            new_corr_matrix,
            text_auto=".4f",
            color_continuous_scale="darkmint",
            aspect="auto",
            width=1000,
            height=850,
            title="Correlation Heatmap of Numerical Features",
        )
        new_fig_corr.update_layout(
            margin=dict(l=150), plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(new_fig_corr, use_container_width=True)


elif page == "5. Readmission & Emergency Utilization (Risk Drivers)":
    st.markdown(
        f"<h2 style='color: {PRIMARY_GREEN};'>🔄 Readmission & Emergency Utilization (Risk Drivers)</h2>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Total Readmissions",
            f"{filtered_df['readmission_count'].sum():,}",
        )
    with col2:
        st.metric(
            "Total Emergency Visits",
            f"{filtered_df['emergency_visit_count'].sum():,}",
        )

    st.markdown("---")

    readmission_summary = (
        filtered_df.groupby(["hospital_name", "condition_type"])[
            ["readmission_count", "admission_count"]
        ]
        .sum()
        .reset_index()
    )

    fig_readmit = px.bar(
        readmission_summary,
        x="hospital_name",
        y=["readmission_count", "admission_count"],
        facet_col="condition_type",
        template="plotly_white",
        text_auto=True,
        title="Total Readmission Counts by Hospital and Condition Type",
        color_discrete_sequence=["#49A684", "#A69563"],
        labels={
            "readmission_count": "Total Readmissions",
            "hospital_name": "Hospital Name",
            "condition_type": "Condition Type",
        },
        width=1500,
        height=500,
    )
    fig_readmit.update_xaxes(matches=None, showticklabels=True)
    fig_readmit.update_yaxes(matches=None)
    fig_readmit.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_readmit, use_container_width=True)

    fig_ad_con = px.bar(
        readmission_summary,
        x="hospital_name",
        y=["admission_count"],
        facet_col="condition_type",
        template="plotly_white",
        text_auto=True,
        title="Total Admissions by Hospital and Condition Type",
        color_discrete_sequence=["#A69563"],
        labels={
            "admission_count": "Total Admissions",
            "hospital_name": "Hospital Name",
            "condition_type": "Condition Type",
        },
        width=1500,
        height=400,
    )
    fig_ad_con.update_xaxes(matches=None, showticklabels=True)
    fig_ad_con.update_yaxes(matches=None)
    fig_ad_con.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_ad_con, use_container_width=True)