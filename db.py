import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient, errors
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📚",
    layout="wide"
)

# Helper Function to Load and Preprocess Data
def load_and_preprocess_data():
    # Path to the CSV file
    csv_file_path = "Student_performance_data.csv"

    if os.path.exists(csv_file_path):
        # Load CSV
        df = pd.read_csv(csv_file_path)

        # Subset & Clean Data
        df_info = df[["StudentID", "Age", "Gender", "GPA", "GradeClass"]].dropna()

        # Transform Age & GPA for Charting
        df_info_for_chart = df_info.copy()
        df_info_for_chart["Age"] = df_info_for_chart["Age"].round(0).astype(int)

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

        return df, df_info_for_chart
    else:
        st.error("CSV file not found. Please ensure 'Student_performance_data.csv' is in the same directory as app.py.")
        return None, None

# Load and preprocess data
df, df_info_for_chart = load_and_preprocess_data()

if df is None or df_info_for_chart is None:
    st.stop()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Intro", "Analysis", "Insert Data"])

# Main Logic Using Big if-else Statement
if page == "Intro":
    st.title("Student Performance Dashboard")
    st.write("""
    This dashboard provides tools for analyzing student performance data and inserting it into MongoDB Atlas.
    - Use the sidebar to navigate between pages.
    - Explore the **Analysis** page to visualize insights.
    - Add new data using the **Insert Data** page.
    """)
    st.image("student.jpg", use_container_width=True)

    st.subheader("Original Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    st.subheader("Overall Data Preview (first 10 rows)")
    st.dataframe(df_info_for_chart.head(10))

    with st.expander(f"ℹ️ **Dataset Information**"):
        st.write(f"**Dataset Features and Their Description:**")
        # Define descriptions for each column
  
        column_descriptions = {
            'Student ID': 'The unique identifier for each student.',
            'Age': 'The age of the student, from 15-18 years old.',
            'Gender': {
                'desciption': 'The gender of the students:',
                'values': {
                    0: 'Male',
                    1: 'Female'
                }
            },

            'Ethnicity': {
                'description': 'The ethnicity of student, coded as follows:',
                'values': {
                    0: 'Caucasion',
                    1: 'African American',
                    2: 'Asian',
                    3: 'Other'
                }
            },

            'Parental Education': {
                'description': 'The education level of the parents, coded as follows:',
                'values': {
                    0: 'None',
                    1: 'High School',
                    2: 'Some College',
                    3: "Bachelor's",
                    4: 'Higher'
                }
            },

            'Weekly Study Time': 'The number of hours the student studies per week.',
            'Absences': 'Number of absences during the school year, ranging from 0 to 30.',
            'Tutoring': {
                'description': 'Whether the student received tutoring, coded as follows:',
                'values': {0: 'No', 1: 'Yes'}
            },

            'Parental Support': {
                'description': 'The level of parental support, coded as follows:',
                'values': {
                  0: 'None',
                    1: 'Low',
                    2: 'Moderate',
                    3: 'High',
                    4: 'Very High'
                }
            },
            'Extracurricular Activities': {
                'description': 'Participation in extracurricular activities:',
                'values': {
                    0: 'No',
                    1: 'Yes'
                }
            },

            'Sports': {
                'description': 'Participation in sports:',
                'values': {
                    0: 'No',
                    1: 'Yes'
                }
            },

            'Music': { 
                'description': 'Participation in music activities:',
                'values': {
                    0: 'No',
                    1: 'Yes'
                }
            },

            'Volunteering': {
                'description': 'Participation in volunteering activities:',
                'values': {
                    0: 'No',
                    1: 'Yes'
                }
            }, 

            'GPA': 'The student\'s grade point average (GPA), ranging from 0 to 4.',

            'GradeClass': {
                'description': 'Classification of students\' grades based on GPA:',
                'values': {
                    0: 'A (GPA >= 3.5)',
                    1: 'B (3.0 <= GPA < 3.5)',
                    2: 'C (2.5 <= GPA < 3.0)',
                    3: 'D (2.0 <= GPA < 2.5)',
                    4: 'F (GPA < 2.0)'
                }
            }
        }

        # Display the column descriptions
        st.subheader("Column Descriptions")

        for column, description in column_descriptions.items():
            st.subheader(f"**{column}**")
    
            # Check if the description is a dictionary (nested structure)
            if isinstance(description, dict):
                # Handle nested structures
                if 'description' in description:
                    st.write(description['description'])
        
                if 'values' in description:
                    markdown_list = ""
            
                    # Handle single-level or multi-level nested values
                    for key, value in description['values'].items():
                        if isinstance(value, dict):
                            markdown_list += f"* **{key}**: \n"
                            markdown_list += "\n".join([f"  - {k}: {v}" for k, v in value.items()]) + "\n"
                        else:
                            markdown_list += f"* {key}: {value}\n"
            
                    st.markdown(markdown_list)
            else:
                # Handle simple string descriptions
                st.write(description)

    with st.expander("**✍️ Made By:**"):
        st.write("""
        **Name: Sara Fuah Jin-Yin**                                                      
        - **Student ID:** 0136704                                         
        - **Email:** 0136704@student.uow.edu.my
                 
        **Name: Jung Jun Won**
        - **Student ID:** 0136488
        - **Email:** 0136488@student.uow.edu.my
                 
        **Name: Tan Jo Shen**
        - **Student ID:** 0136733
        - **Email:** 0136733@student.uow.edu.my
         
        """)

elif page == "Analysis":
    st.title("Student Performance Data")

    # Pie Charts in 2×2 Layout
    st.subheader("General Distribution of Data")

    def build_pie_chart(series, label):
        counts = series.value_counts().reset_index()
        counts.columns = [label, "Count"]

        chart = (
            alt.Chart(counts)
            .mark_arc(innerRadius=50)  # Donut
            .encode(
                theta="Count:Q",
                color=f"{label}:N",
                tooltip=[f"{label}:N", "Count:Q"]
            )
        )
        return chart

    col1, col2 = st.columns(2)
    with col1:
        st.write("Age Distribution")
        chart_age = build_pie_chart(df_info_for_chart["Age"], "Age")
        st.altair_chart(chart_age, use_container_width=True)

    with col2:
        st.write("Gender Distribution")
        chart_gender = build_pie_chart(df_info_for_chart["Gender"], "Gender")
        st.altair_chart(chart_gender, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("GPA Distribution")
        chart_gpa = build_pie_chart(df_info_for_chart["GPA_Cat"], "GPA")
        st.altair_chart(chart_gpa, use_container_width=True)

    with col4:
        st.write("GradeClass Distribution")
        chart_grade = build_pie_chart(df_info_for_chart["GradeClass"], "GradeClass")
        st.altair_chart(chart_grade, use_container_width=True)
    
    with st.expander("ℹ️ **Pie Chart Overview:**"):
        st.markdown("""
        The pie charts above provide a general overview of the distribution of student data based on the following categories:
    
        - **Age Distribution:** Approximately equal distribution among ages 15-18, with the mean of 598.
        - **Gender Distribution:** Approximately equal distribution between males and females, with the mean of 1197.
        - **GPA Distribution:** Majority of students have a GPA of 2.0 and lower, while less than 1/3 of students have a GPA of 3.0 and higher.
        - **GradeClass Distribution:** Approximately half of the students fall into the 'F' class, with fewer students in the higher grade classes.
        """)

    # Countplots for Categorical Columns
    st.subheader("Countplots for Categorical Columns")

    # Identify numerical columns: columns with more than 5 unique values are considered numerical
    numerical_columns = [col for col in df.columns if df[col].nunique() > 5]

    # Identify categorical columns: columns that are not numerical and not 'GradeClass'
    categorical_columns = df.columns.difference(numerical_columns).difference(['GradeClass']).to_list()

    # Custom labels for the categorical columns
    custom_labels = {
        'Ethnicity': ['Caucasian', 'African American', 'Asian', 'Other'],
        'Age': [15, 16, 17, 18],
        'ParentalEducation': ['None', 'High School', 'Some College', 'Bachelor\'s', 'Higher'],
        'Tutoring': ['No', 'Yes'],
        'ParentalSupport': ['No', 'Low', 'Moderate', 'High', 'Very High'],
        'Extracurricular': ['No', 'Yes'],
        'Sports': ['No', 'Yes'],
        'Music': ['No', 'Yes'],
        'Volunteering': ['No', 'Yes'],
        'Gender': ['Male', 'Female']
    }

    # Add a selection box to choose a categorical column
    selected_column = st.selectbox("Select a categorical column to visualize", categorical_columns)

    # Plot countplot for the selected column
    if selected_column in custom_labels:
        plt.figure(figsize=(8, 5))
        sns.countplot(data=df, x=selected_column)
        plt.title(f'Countplot of {selected_column}')

        # Directly set custom labels
        labels = custom_labels[selected_column]
        ticks = range(len(labels))
        plt.xticks(ticks=ticks, labels=labels)

        plt.tight_layout()
        st.pyplot(plt)  # Render the plot in Streamlit
    else:
        st.warning(f"No custom labels defined for column: {selected_column}")

    st.markdown("""
    ### Bar Chart Analysis
    - **Purpose**: 
        - Visualize student information distribution across the dataset.
     - **Visualization**: 
        - Each bar represents the count of students in a specific category.
    - **Insights**: 
        - Identify the distribution of students across different categories.
        - Highlight any imbalances or trends in the data.
    - **Actionable Use**: 
        - Optimize resources and study plans based on the distribution of students.
    """)

elif page == "Insert Data":
    st.title("Insert Data into MongoDB Atlas")

    # Hard-coded MongoDB Atlas connection settings
    CLOUD_CONN = "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/"
    CLOUD_DB_NAME = "Student"
    CLOUD_COLL_NAME = "student_info"

    record_data = df_info_for_chart.to_dict(orient="records")

    if st.button("Insert Data into MongoDB Atlas"):
        try:
            cloud_client = MongoClient(CLOUD_CONN)
            st.success("Connection to MongoDB Atlas succeeded!")
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.stop()

        clouddb = cloud_client[CLOUD_DB_NAME]
        cloudrecordcol = clouddb[CLOUD_COLL_NAME]

        # Delete existing data
        cloudrecordcol.delete_many({})
        st.info("Deleted all existing records in the cloud collection.")

        # Create unique index on StudentID
        cloudrecordcol.create_index("StudentID", unique=True)

        # Insert data
        try:
            cloudrecordcol.insert_many(record_data)
            st.success("Data inserted into cloud collection successfully.")
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