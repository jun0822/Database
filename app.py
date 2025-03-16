# -*- coding: utf-8 -*-
"""
Streamlit app to ingest a pre-loaded student CSV -> subset columns -> convert to BSON -> 
insert into local & cloud MongoDB -> check duplicates.
"""

import streamlit as st
import pandas as pd
import json
from bson.json_util import dumps, loads
from pymongo import MongoClient, errors
import os

st.title("Student Data Pipeline (CSV -> MongoDB)")

# Option 1: Load CSV from local repository (recommended if the file is packaged with your code)
csv_file_path = "Student_performance_data.csv"

# Option 2: Alternatively, load CSV from a public GitHub raw URL
# csv_file_path = "https://raw.githubusercontent.com/YourUsername/YourRepo/main/Student_performance_data.csv"

if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
    st.subheader("CSV Preview")
    st.dataframe(df.head(10))
    
    # Subset columns
    df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]]
    # Drop rows with missing values
    df_info = df_info.dropna()
    
    st.subheader("Subset & Cleaned Data Preview")
    st.dataframe(df_info.head(10))
    
    # Convert to BSON and store in a file (optional)
    bson_filename = "student_record.bson"
    with open(bson_filename, "wb") as file:
        file.write(dumps(df_info.to_dict(orient="records")).encode("utf-8"))
    st.success(f"BSON file '{bson_filename}' created successfully!")
    
    # MongoDB Connection Settings
    st.subheader("MongoDB Connection")
    local_conn = st.text_input("Local Mongo URI", "mongodb://localhost:27017/")
    cloud_conn = st.text_input("Cloud Mongo URI", "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/")
    local_db_name = st.text_input("Local DB Name", "Student")
    cloud_db_name = st.text_input("Cloud DB Name", "Student")
    local_coll_name = st.text_input("Local Collection Name", "student_info")
    cloud_coll_name = st.text_input("Cloud Collection Name", "student_info")
    
    if st.button("Insert Data into MongoDB"):
        # Connect to MongoDB
        try:
            local_client = MongoClient(local_conn)
            cloud_client = MongoClient(cloud_conn)
            st.success("Connection to MongoDB succeeded!")
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.stop()
    
        localdb = local_client[local_db_name]
        clouddb = cloud_client[cloud_db_name]
    
        localrecordcol = localdb[local_coll_name]
        cloudrecordcol = clouddb[cloud_coll_name]
    
        # Delete existing data (optional)
        localrecordcol.delete_many({})
        cloudrecordcol.delete_many({})
        st.info("Deleted all existing records in both collections.")
    
        # Create unique index on StudentID
        localrecordcol.create_index("StudentID", unique=True)
        cloudrecordcol.create_index("StudentID", unique=True)
    
        # Step 2: Load data from the BSON file
        try:
            with open(bson_filename, "rb") as file:
                record_data = loads(file.read())
        except Exception as e:
            st.error(f"Failed to load BSON file: {e}")
            st.stop()
    
        # Insert data into local collection
        try:
            if isinstance(record_data, list):
                localrecordcol.insert_many(record_data)
            else:
                localrecordcol.insert_one(record_data)
            st.success("Data inserted into local collection successfully.")
        except errors.PyMongoError as e:
            st.error(f"An error occurred in local collection: {e}")
    
        # Insert data into cloud collection
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
            local_count = localrecordcol.count_documents({})
            cloud_count = cloudrecordcol.count_documents({})
            st.write(f"Local collection count: {local_count}")
            st.write(f"Cloud collection count: {cloud_count}")
        except errors.PyMongoError as e:
            st.error(f"An error occurred while counting documents: {e}")
    
        # Check for duplicates
        pipeline = [
            {"$group": {"_id": "$StudentID", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
    
        # Local duplicates
        try:
            local_duplicates = list(localrecordcol.aggregate(pipeline))
            if local_duplicates:
                st.warning(f"Duplicates found in local collection: {local_duplicates}")
            else:
                st.write("No duplicates found in local collection.")
        except errors.PyMongoError as e:
            st.error(f"Error checking duplicates in local: {e}")
    
        # Cloud duplicates
        try:
            cloud_duplicates = list(cloudrecordcol.aggregate(pipeline))
            if cloud_duplicates:
                st.warning(f"Duplicates found in cloud collection: {cloud_duplicates}")
            else:
                st.write("No duplicates found in cloud collection.")
        except errors.PyMongoError as e:
            st.error(f"Error checking duplicates in cloud: {e}")
    
        # Clean up the BSON file if desired
        if os.path.exists(bson_filename):
            os.remove(bson_filename)
else:
    st.error("CSV file not found. Please ensure 'Student_performance_data.csv' is in the same directory as app.py.")
