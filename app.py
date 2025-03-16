# -*- coding: utf-8 -*-
"""
Streamlit app to ingest a pre-loaded student CSV -> subset columns ->
insert data into MongoDB Atlas (hard-coded) and check for duplicates.
"""

import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
import os

st.title("Student Data Pipeline (CSV -> MongoDB Atlas)")

# Hard-coded MongoDB Atlas connection settings
CLOUD_CONN = "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/"
CLOUD_DB_NAME = "Student"
CLOUD_COLL_NAME = "student_info"

# Path to the CSV file (ensure it's in your repo alongside app.py)
csv_file_path = "Student_performance_data.csv"

if os.path.exists(csv_file_path):
    # Read CSV using pandas
    df = pd.read_csv(csv_file_path)
    st.subheader("CSV Preview")
    st.dataframe(df.head(10))
    
    # Subset the relevant columns and drop rows with missing values
    df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]]
    df_info = df_info.dropna()
    
    st.subheader("Subset & Cleaned Data Preview")
    st.dataframe(df_info.head(10))
    
    # Convert DataFrame to list of dictionaries
    record_data = df_info.to_dict(orient="records")
    
    # Button to insert data into MongoDB Atlas
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
            if isinstance(record_data, list):
                cloudrecordcol.insert_many(record_data)
            else:
                cloudrecordcol.insert_one(record_data)
            st.success("Data inserted into cloud collection successfully.")
        except errors.PyMongoError as e:
            st.error(f"An error occurred in cloud collection: {e}")
        
        # Verify data insertion
        try:
            cloud_count = cloudrecordcol.count_documents({})
            st.write(f"Cloud collection count: {cloud_count}")
        except errors.PyMongoError as e:
            st.error(f"An error occurred while counting documents: {e}")
        
        # Check for duplicates using aggregation pipeline
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
