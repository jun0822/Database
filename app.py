# -*- coding: utf-8 -*-
"""
Streamlit app to ingest a pre-loaded student CSV -> subset columns ->
display two tables and a pie chart under each table -> insert data into MongoDB Atlas -> check duplicates.
"""

import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient, errors
import os

st.title("Student Data Pipeline (CSV -> MongoDB Atlas) with Pie Charts")

# Hard-coded MongoDB Atlas connection settings
CLOUD_CONN = "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/"
CLOUD_DB_NAME = "Student"
CLOUD_COLL_NAME = "student_info"

# Path to the CSV file (ensure it's in your repo alongside app.py)
csv_file_path = "Student_performance_data.csv"

# 1) Load CSV
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
    
    # --- Original CSV Preview ---
    st.subheader("CSV Preview (first 10 rows)")
    st.dataframe(df.head(10))

    # Pie chart for the original data's Gender distribution
    # If "Gender" is numeric in your dataset, you can still visualize it, 
    # but typically for a pie chart, it's best if Gender is categorical.
    st.subheader("Pie Chart: Gender Distribution (Original Data)")
    df_gender_orig = df["Gender"].value_counts().reset_index()
    df_gender_orig.columns = ["Gender", "Count"]
    
    chart_orig = (
        alt.Chart(df_gender_orig)
        .mark_arc(innerRadius=50)  # Donut style
        .encode(
            theta="Count:Q",
            color="Gender:N",
            tooltip=["Gender:N", "Count:Q"]
        )
    )
    st.altair_chart(chart_orig, use_container_width=True)

    # 2) Subset & Clean Data
    df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]].dropna()
    
    st.subheader("Subset & Cleaned Data Preview (first 10 rows)")
    st.dataframe(df_info.head(10))

    # Pie chart for the cleaned data's Gender distribution
    st.subheader("Pie Chart: Gender Distribution (Cleaned Data)")
    df_gender_clean = df_info["Gender"].value_counts().reset_index()
    df_gender_clean.columns = ["Gender", "Count"]
    
    chart_clean = (
        alt.Chart(df_gender_clean)
        .mark_arc(innerRadius=50)
        .encode(
            theta="Count:Q",
            color="Gender:N",
            tooltip=["Gender:N", "Count:Q"]
        )
    )
    st.altair_chart(chart_clean, use_container_width=True)

    # Convert DataFrame to list of dictionaries for MongoDB
    record_data = df_info.to_dict(orient="records")

    # 3) Insert into MongoDB Atlas
    if st.button("Insert Data into MongoDB Atlas"):
        # Connect to MongoDB Atlas
        try:
            cloud_client = MongoClient(CLOUD_CONN)
            st.success("Connection to MongoDB Atlas succeeded!")
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.stop()
        
        clouddb = cloud_client[CLOUD_DB_NAME]
        cloudrecordcol = clouddb[CLOUD_COLL_NAME]
        
        # Delete existing data (optional)
        cloudrecordcol.delete_many({})
        st.info("Deleted all existing records in the cloud collection.")
        
        # Create unique index on StudentID
        cloudrecordcol.create_index("StudentID", unique=True)
        
        # Insert data into the cloud collection
        try:
            cloudrecordcol.insert_many(record_data)
            st.success("Data inserted into cloud collection successfully.")
        except errors.PyMongoError as e:
            st.error(f"An error occurred in cloud collection: {e}")
        
        # 4) Verify data insertion
        try:
            cloud_count = cloudrecordcol.count_documents({})
            st.write(f"Cloud collection count: {cloud_count}")
        except errors.PyMongoError as e:
            st.error(f"An error occurred while counting documents: {e}")
        
        # 5) Check for duplicates using aggregation pipeline
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

else:
    st.error("CSV file not found. Please ensure 'Student_performance_data.csv' is in the same directory as app.py.")
