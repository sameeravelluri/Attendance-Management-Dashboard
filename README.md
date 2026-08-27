# Attendance Management Dashboard

A descriptive analytics project that converts raw student attendance
records into attendance percentages, KPIs, and dashboard visualizations.

## Project Rounds
- **Round 1:** Algorithm & process flow (data collection → cleaning →
  transformation → attendance calculation → KPI generation → visualization)
- **Round 2:** Dataset structure (Student_ID, Student_Name, Class_Section,
  Subject, Attendance_Date, Attendance_Status, Faculty)
- **Round 3:** Full working source code (this repository)

## Files
| File | Description |
|---|---|
| `Attendance_Management_Dashboard_Source_Code.ipynb` | Main Jupyter notebook — full pipeline with explanations and executed outputs |
| `attendance_dashboard.py` | Same logic as a plain Python script |
| `attendance_raw.csv` | Sample/demo attendance dataset used by the notebook |
| `dashboard.png` | Generated dashboard screenshot (KPIs + charts) |

## How to Run
1. Install Python 3 with `pandas`, `numpy`, and `matplotlib`.
2. Open `Attendance_Management_Dashboard_Source_Code.ipynb` in Jupyter
   Notebook, JupyterLab, VS Code, or Google Colab.
3. Run all cells (`Kernel > Restart & Run All`).

## Pipeline Overview
Attendance Data Collection → Data Import → Data Cleaning → Data
Transformation → Attendance Calculation → KPI Generation → Data
Aggregation → Visualization → Interactive Dashboard → Attendance Insights

## Key Formula
```
Attendance Percentage = (Number of Classes Attended / Total Number of Classes) × 100
```
