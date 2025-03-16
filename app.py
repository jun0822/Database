# -*- coding: utf-8 -*-
"""
Streamlit app to ingest a pre-loaded student CSV -> subset columns ->
display a CSV preview table, then a subset & cleaned data preview with pie charts 
for Age, Gender, GPA, and GradeClass -> insert data into MongoDB Atlas -> check duplicates.
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

if os.path.exists(csv_file_path):
    # 1) Load the CSV and show its preview (table only)
    df = pd.read_csv(csv_file_path)
    st.subheader("CSV Preview (first 10 rows)")
    st.dataframe(df.head(10))
    
    # 2) Subset & Clean Data (keep selected columns and drop missing values)
    df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]].dropna()
    st.subheader("Subset & Cleaned Data Preview (first 10 rows)")
    st.dataframe(df_info.head(10))
    
    # 3) Pie Charts for Subset & Cleaned Data:
    st.subheader("Pie Charts for Age, Gender, GPA, and GradeClass")
    
    columns_to_plot = ["Age", "Gender", "GPA", "GradeClass"]
    
    for col in columns_to_plot:
        st.write(f"**{col} Distribution**")
        
        # Calculate the count for each unique value in the column
        df_counts = df_info[col].value_counts().reset_index()
        df_counts.columns = [col, "Count"]
        
        # Create a donut (pie) chart using Altair
        chart = (
            alt.Chart(df_counts)
            .mark_arc(innerRadius=50)  # Use innerRadius=50 for donut style; remove for standard pie
            .encode(
                theta="Count:Q",
                color=f"{col}:N",
                tooltip=[f"{col}:N", "Count:Q"]
            )
        )
        st.altair_chart(chart, use_container_width=True)

    # Convert the cleaned DataFrame to a list of dictionaries for MongoDB insertion
    record_data = df_info.to_dict(orient="records")
    
    # 4) Insert into MongoDB Atlas (on button click)
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
        
        # 5) Verify data insertion by counting documents
        try:
            cloud_count = cloudrecordcol.count_documents({})
            st.write(f"Cloud collection count: {cloud_count}")
        except errors.PyMongoError as e:
            st.error(f"An error occurred while counting documents: {e}")
        
        # 6) Check for duplicates using an aggregation pipeline
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
