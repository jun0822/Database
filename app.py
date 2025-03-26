# -*- coding: utf-8 -*-
"""
Streamlit app to categorize GPA into 1.0, 2.0, 3.0, 4.0 bins,
then display a 2×2 layout of pie charts (Age, Gender, *Categorized* GPA, GradeClass),
insert bulk data into MongoDB Atlas, and allow users to add new student records.
"""

import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient, errors
import os

st.title("Student Performance Data")

# Hard-coded MongoDB Atlas connection settings
CLOUD_CONN = "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/"
CLOUD_DB_NAME = "Student"
CLOUD_COLL_NAME = "student_info"

# Path to the CSV file
csv_file_path = "Student_performance_data.csv"

if os.path.exists(csv_file_path):
    # 1) Load CSV
    df = pd.read_csv(csv_file_path)
    st.subheader("Original Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    # 2) Subset & Clean Data
    df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]].dropna()
    st.subheader("Overall Data Preview (first 10 rows)")
    st.dataframe(df_info.head(10))

    # 3) Transform Age & GPA for Charting
    # Round Age to integer
    df_info_for_chart = df_info.copy()
    df_info_for_chart["Age"] = df_info_for_chart["Age"].round(0).astype(int)

    # Categorize GPA 
    def categorize_gpa(g):
        if g < 1.5:
            return "1.0"
        elif g < 2.5:
            return "2.0"
        elif g < 3.5:
            return "3.0"
        else:
            return "4.0"
    
    df_info_for_chart["GPA_Cat"] = df_info_for_chart["GPA"].apply(categorize_gpa)

    # 4) Pie Charts in 2×2 Layout
    st.subheader("Pie Charts (Age, Gender, GPA, GradeClass)")

    def build_pie_chart(series, label):
        """Helper function to build a donut chart for any column."""
        counts = series.value_counts().reset_index()
        counts.columns = [label, "Count"]
        
        chart = (
            alt.Chart(counts)
            .mark_arc(innerRadius=50)  # Donut style
            .encode(
                theta="Count:Q",
                color=f"{label}:N",
                tooltip=[f"{label}:N", "Count:Q"]
            )
        )
        return chart

    # First row: Age (left), Gender (right)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Age Distribution")
        chart_age = build_pie_chart(df_info_for_chart["Age"], "Age")
        st.altair_chart(chart_age, use_container_width=True)

    with col2:
        st.write("Gender Distribution")
        chart_gender = build_pie_chart(df_info_for_chart["Gender"], "Gender")
        st.altair_chart(chart_gender, use_container_width=True)

    # Second row: GPA (left), GradeClass (right)
    col3, col4 = st.columns(2)
    with col3:
        st.write("GPA Distribution")
        chart_gpa = build_pie_chart(df_info_for_chart["GPA_Cat"], "GPA")
        st.altair_chart(chart_gpa, use_container_width=True)

    with col4:
        st.write("GradeClass Distribution")
        chart_grade = build_pie_chart(df_info_for_chart["GradeClass"], "GradeClass")
        st.altair_chart(chart_grade, use_container_width=True)

        # Delete existing data (optional)
        cloudrecordcol.delete_many({})
        st.info("Deleted all existing records in the cloud collection.")

        # Create unique index on StudentID
        cloudrecordcol.create_index("StudentID", unique=True)

        # Insert data
        try:
            cloudrecordcol.insert_many(record_data)
            st.success("Bulk data inserted into cloud collection successfully.")
        except errors.PyMongoError as e:
            st.error(f"An error occurred in cloud collection: {e}")

        # Verify insertion
        try:
            cloud_count = cloudrecordcol.count_documents({})
            st.write(f"Cloud collection count: {cloud_count}")
        except errors.PyMongoError as e:
            st.error(f"An error occurred while counting documents: {e}")

        # Check for duplicates
        pipeline = [
            {"$group": {"_id": "$StudentID", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        try:
            cloud_duplicates = list(cloudrecordcol.aggregate(pipeline))
            if cloud_duplicates:
                st.warning(f"Duplicates found in cloud collection: {cloud_duplicates}")
            else:
                st.write("No duplicates found in cloud collection.")
        except errors.PyMongoError as e:
            st.error(f"Error checking duplicates in cloud: {e}")

    # 6) Form to Add a New Student Record (Single Insert)
st.subheader("➕ Add a New Student Record")
with st.form("new_student_form"):
    new_student_id = st.text_input("StudentID")
    new_age = st.number_input("Age", min_value=1, max_value=100, value=18)
    new_gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
    new_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, value=0.0, step=0.1)
    new_gradeclass = st.text_input("GradeClass")
    new_submitted = st.form_submit_button("Add Student")

    if new_submitted:
        # Create the new record dictionary
        new_record = {
            "StudentID": new_student_id,
            "Age": new_age,
            "Gender": new_gender,
            "GPA": new_gpa,
            "GradeClass": new_gradeclass
        }
        # Debug: Output the new record so you can see what was entered
        st.write("New Record:", new_record)
        try:
            cloud_client = MongoClient(CLOUD_CONN)
            clouddb = cloud_client[CLOUD_DB_NAME]
            cloudrecordcol = clouddb[CLOUD_COLL_NAME]
            # Insert the new record
            insert_result = cloudrecordcol.insert_one(new_record)
            st.success(f"Student {new_student_id} has been added! Inserted ID: {insert_result.inserted_id}")
            st.experimental_rerun()  # Refresh the app to update the data view if needed
        except Exception as e:
            st.error(f"Insertion failed: {e}")
            
    st.error("CSV file not found. Please ensure 'Student_performance_data.csv' is in the same directory as app.py.")
