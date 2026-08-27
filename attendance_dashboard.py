"""
ATTENDANCE MANAGEMENT DASHBOARD - SOURCE CODE
Round 3 Deliverable

This implements, end-to-end, the algorithm described in Round 1
(Algorithm & Process Flow) and the dataset structure described in
Round 2 (Dataset), using the exact process flow:

Attendance Data Collection -> Data Import -> Data Cleaning ->
Data Transformation -> Attendance Calculation -> KPI Generation ->
Data Aggregation -> Visualization -> Interactive Dashboard ->
Attendance Insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# STEP 1 & 2: DATA COLLECTION + DATA IMPORT
# ---------------------------------------------------------------------------
# Since no live attendance system is connected yet, a demonstration dataset
# is generated here in the exact schema defined in Round 2 (Dataset doc),
# saved as CSV, and then imported back - simulating the real
# "collect -> import from Excel/CSV" step of the pipeline.

def generate_demo_dataset(n_students=40, n_days=30, out_path="attendance_raw.csv"):
    students = [f"S{i:03d}" for i in range(1, n_students + 1)]
    names = [f"Student_{i}" for i in range(1, n_students + 1)]
    sections = ["A", "B", "C"]
    subjects = ["Maths", "Physics", "Chemistry", "English", "Computer Science"]
    faculty_map = {
        "Maths": "Mr. Rao",
        "Physics": "Mrs. Iyer",
        "Chemistry": "Mr. Khan",
        "English": "Ms. Fernandes",
        "Computer Science": "Mr. Sharma",
    }

    student_section = {sid: random.choice(sections) for sid in students}

    start_date = datetime(2026, 1, 1)
    rows = []
    for day in range(n_days):
        date = start_date + timedelta(days=day)
        if date.weekday() >= 5:          # skip weekends
            continue
        for sid, name in zip(students, names):
            for subject in subjects:
                status = np.random.choice(
                    ["Present", "Absent"], p=[0.85, 0.15]
                )
                rows.append({
                    "Student_ID": sid,
                    "Student_Name": name,
                    "Class_Section": student_section[sid],
                    "Subject": subject,
                    "Attendance_Date": date.strftime("%Y-%m-%d"),
                    "Attendance_Status": status,
                    "Faculty": faculty_map[subject],
                })

    df = pd.DataFrame(rows)

    # Deliberately inject some messy/inconsistent records so that the
    # cleaning step (Step 3-5) has real work to do, matching the
    # Round 1 description ("identify missing, duplicate, or inconsistent
    # records").
    dirty_idx = df.sample(frac=0.02, random_state=1).index
    df.loc[dirty_idx[:len(dirty_idx)//3], "Attendance_Status"] = None
    df.loc[dirty_idx[len(dirty_idx)//3: 2*len(dirty_idx)//3], "Attendance_Status"] = "present "  # inconsistent case/spacing
    df = pd.concat([df, df.sample(5, random_state=2)], ignore_index=True)  # duplicates

    df.to_csv(out_path, index=False)
    return out_path


def import_attendance_data(path):
    """STEP 2: Import the attendance data from a structured CSV file."""
    df = pd.read_csv(path)
    return df


# ---------------------------------------------------------------------------
# STEP 3: INSPECT THE DATASET
# ---------------------------------------------------------------------------

def inspect_dataset(df):
    report = {
        "total_records": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_records": int(df.duplicated().sum()),
        "unique_status_values": df["Attendance_Status"].dropna().unique().tolist(),
    }
    return report


# ---------------------------------------------------------------------------
# STEP 4 & 5: DATA CLEANING + STANDARDIZATION
# ---------------------------------------------------------------------------

def clean_and_standardize(df):
    df = df.copy()

    # Drop exact duplicate records
    df = df.drop_duplicates()

    # Standardize text fields (strip whitespace, consistent casing)
    df["Attendance_Status"] = (
        df["Attendance_Status"].astype(str).str.strip().str.capitalize()
    )
    df.loc[~df["Attendance_Status"].isin(["Present", "Absent"]), "Attendance_Status"] = np.nan

    # Handle missing/invalid attendance status -> drop, since attendance
    # status is the core field the whole calculation depends on
    df = df.dropna(subset=["Attendance_Status"])

    # Standardize IDs, names, sections, subject fields
    df["Student_ID"] = df["Student_ID"].astype(str).str.strip().str.upper()
    df["Student_Name"] = df["Student_Name"].astype(str).str.strip()
    df["Class_Section"] = df["Class_Section"].astype(str).str.strip().str.upper()
    df["Subject"] = df["Subject"].astype(str).str.strip()

    # Standardize date field to a proper datetime type
    df["Attendance_Date"] = pd.to_datetime(df["Attendance_Date"], errors="coerce")
    df = df.dropna(subset=["Attendance_Date"])

    df = df.reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# STEP 6: DATA TRANSFORMATION (analysis-ready structure)
# ---------------------------------------------------------------------------

def transform_data(df):
    df = df.copy()
    df["Is_Present"] = (df["Attendance_Status"] == "Present").astype(int)
    df["Month"] = df["Attendance_Date"].dt.to_period("M").astype(str)
    return df


# ---------------------------------------------------------------------------
# STEP 7: ATTENDANCE CALCULATION
# ---------------------------------------------------------------------------

def calculate_attendance(df, group_cols):
    """
    Generic attendance-percentage calculator.
    Attendance % = (Classes Attended / Total Classes) * 100
    """
    summary = (
        df.groupby(group_cols)
        .agg(
            Present_Count=("Is_Present", "sum"),
            Total_Classes=("Is_Present", "count"),
        )
        .reset_index()
    )
    summary["Absent_Count"] = summary["Total_Classes"] - summary["Present_Count"]
    summary["Attendance_Percentage"] = (
        summary["Present_Count"] / summary["Total_Classes"] * 100
    ).round(2)
    return summary


# ---------------------------------------------------------------------------
# STEP 8: KPI GENERATION
# ---------------------------------------------------------------------------

def generate_kpis(df, student_summary, low_attendance_threshold=75.0):
    kpis = {
        "Total_Students": df["Student_ID"].nunique(),
        "Total_Classes_Recorded": len(df),
        "Average_Attendance_Percentage": round(
            student_summary["Attendance_Percentage"].mean(), 2
        ),
        "Total_Present_Count": int(df["Is_Present"].sum()),
        "Total_Absent_Count": int((1 - df["Is_Present"]).sum()),
        "Low_Attendance_Student_Count": int(
            (student_summary["Attendance_Percentage"] < low_attendance_threshold).sum()
        ),
    }
    return kpis


# ---------------------------------------------------------------------------
# STEP 9: SUMMARIZATION (by student, subject, class/section, time period)
# ---------------------------------------------------------------------------

def build_summaries(df):
    by_student = calculate_attendance(df, ["Student_ID", "Student_Name"])
    by_subject = calculate_attendance(df, ["Subject"])
    by_section = calculate_attendance(df, ["Class_Section"])
    by_month = calculate_attendance(df, ["Month"])
    return {
        "by_student": by_student,
        "by_subject": by_subject,
        "by_section": by_section,
        "by_month": by_month,
    }


# ---------------------------------------------------------------------------
# STEP 10: CHARTS, TABLES, KPI CARDS
# ---------------------------------------------------------------------------

def render_dashboard(summaries, kpis, low_attendance_threshold=75.0, save_path="dashboard.png"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Attendance Management Dashboard", fontsize=16, fontweight="bold")

    # KPI card panel (rendered as text, top-left)
    ax = axes[0, 0]
    ax.axis("off")
    kpi_text = "\n".join([f"{k.replace('_', ' ')}: {v}" for k, v in kpis.items()])
    ax.text(0.05, 0.95, "KPI SUMMARY", fontsize=13, fontweight="bold", va="top")
    ax.text(0.05, 0.80, kpi_text, fontsize=11, va="top")

    # Attendance % by subject
    ax = axes[0, 1]
    data = summaries["by_subject"].sort_values("Attendance_Percentage")
    ax.barh(data["Subject"], data["Attendance_Percentage"], color="#4C72B0")
    ax.set_title("Attendance % by Subject")
    ax.set_xlabel("Attendance %")

    # Attendance % by class/section
    ax = axes[1, 0]
    data = summaries["by_section"].sort_values("Class_Section")
    ax.bar(data["Class_Section"], data["Attendance_Percentage"], color="#55A868")
    ax.set_title("Attendance % by Class/Section")
    ax.set_ylabel("Attendance %")

    # Attendance trend by month
    ax = axes[1, 1]
    data = summaries["by_month"].sort_values("Month")
    ax.plot(data["Month"], data["Attendance_Percentage"], marker="o", color="#C44E52")
    ax.set_title("Attendance % Trend by Month")
    ax.set_ylabel("Attendance %")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path


# ---------------------------------------------------------------------------
# STEP 11: INTERACTIVE FILTERS
# ---------------------------------------------------------------------------

def filter_attendance(df, student_id=None, subject=None, class_section=None,
                       start_date=None, end_date=None):
    """
    Applies interactive-style filters for student, subject, class/section,
    and time period (mirrors the filter controls a BI tool like Power BI
    would expose on the dashboard).
    """
    result = df.copy()
    if student_id:
        result = result[result["Student_ID"] == student_id]
    if subject:
        result = result[result["Subject"] == subject]
    if class_section:
        result = result[result["Class_Section"] == class_section]
    if start_date:
        result = result[result["Attendance_Date"] >= pd.to_datetime(start_date)]
    if end_date:
        result = result[result["Attendance_Date"] <= pd.to_datetime(end_date)]
    return result


# ---------------------------------------------------------------------------
# STEP 12: PRESENT THE DASHBOARD / STEP 13: VALIDATION
# ---------------------------------------------------------------------------

def validate_dashboard(df, student_summary):
    """
    Cross-checks dashboard-level totals against the raw cleaned data to
    make sure the KPI numbers are internally consistent.
    """
    checks = {}
    checks["present_count_matches"] = (
        df["Is_Present"].sum() == student_summary["Present_Count"].sum()
    )
    checks["total_classes_match"] = (
        len(df) == student_summary["Total_Classes"].sum()
    )
    checks["percentage_range_valid"] = bool(
        student_summary["Attendance_Percentage"].between(0, 100).all()
    )
    return checks


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def run_pipeline():
    raw_path = generate_demo_dataset()
    df_raw = import_attendance_data(raw_path)

    inspection_report = inspect_dataset(df_raw)
    df_clean = clean_and_standardize(df_raw)
    df_final = transform_data(df_clean)

    summaries = build_summaries(df_final)
    kpis = generate_kpis(df_final, summaries["by_student"])
    chart_path = render_dashboard(summaries, kpis)
    validation = validate_dashboard(df_final, summaries["by_student"])

    return {
        "inspection_report": inspection_report,
        "kpis": kpis,
        "summaries": summaries,
        "chart_path": chart_path,
        "validation": validation,
    }


if __name__ == "__main__":
    results = run_pipeline()
    print("INSPECTION REPORT:", results["inspection_report"])
    print("KPIS:", results["kpis"])
    print("VALIDATION:", results["validation"])
    print("Dashboard chart saved at:", results["chart_path"])
