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
page = st.sidebar.radio("Go to", ["📖Intro", "📈Analysis", "🔖Insert Data"])

# Main Logic Using Big if-else Statement
if page == "📖Intro":
    st.title("Student Performance Dashboard📚")
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
        - **Student ID:** 0136468
        - **Email:** 0136468@student.uow.edu.my
                 
        **Name: Tan Jo Shen**
        - **Student ID:** 0136733
        - **Email:** 0136733@student.uow.edu.my
         
        """)

elif page == "📈Analysis":
    st.title("Student Performance Data📈")

    # Add a select box to choose visualization type
    visualization_option = st.selectbox(
        "Select Visualization Type",
        ["🥧Pie Chart", "📊Bar Chart", "📈Histogram", "⭐Correlations", "❌Absences"]
    )

    if visualization_option == "🥧Pie Chart":
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

        st.markdown("""
            The pie charts above provide a general overview of the distribution of student data based on the following categories:
    
            - **Age Distribution:** Approximately equal distribution among ages 15-18, with the mean of 598.
            - **Gender Distribution:** Approximately equal distribution between males and females, with the mean of 1197.
            - **GPA Distribution:** Majority of students have a GPA of 2.0 and lower, while less than 1/3 of students have a GPA of 3.0 and higher.
            - **GradeClass Distribution:** Approximately half of the students fall into the 'F' class, with fewer students in the higher grade classes.
            """)
        
        with st.expander("ℹ️ **Why Pie Charts**"):
            st.markdown("""
            ### Pie Chart Analysis
            - **Purpose**: 
                - Visualize the proportional distribution of categorical data across different categories.
            - **Visualization**: 
                - Each slice of the pie chart represents the proportion of data points belonging to a specific category.
                - The size of each slice is proportional to the frequency or percentage of the category it represents.
            - **Insights**: 
                - Quickly identify dominant categories and their relative sizes within the dataset.
                - Highlight imbalances or trends in categorical distributions (e.g., gender, age groups, GPA categories).
             - **Actionable Use**: 
                - Tailor interventions or resource allocation based on the observed proportions (e.g., focusing on underrepresented groups or addressing imbalances in grade distributions).
            """)
    


    elif visualization_option == "📊Bar Chart":
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

        # Custom descriptions for each categorical column
        descriptions = {
            'Ethnicity': [
                "- Shows the distribution of students by ethnicity.",
                "- Helps analyze diversity in the dataset.",
                "- Caucasian students are the majority.",
                "- Approximately equal distribution of both African American and Asian students.",
                "- Other ethnicity students are the minority."
            ],
            'Age': [
                "- Displays the number of students in each age group.",
                "- Useful for understanding the age demographics.",
                "- Majority of students are 15 years old.",
                "- Approximately equal distribution of 16 to 18 years old students."
            ],
            'ParentalEducation': [
                "- Represents the highest education level of parents.",
                "- Can indicate the impact of parental education on student performance.",
                "- Countplot of students' parental education forms a rough bell curve.",
                "- Majority of students' parents has educational backgroud in college.",
                "- Followed by high school education.",
                "- While the minority of students' parents has a higher than bachelor's education background."

            ],
            'Tutoring': [
                "- Compares students who receive tutoring vs. those who don't.",
                "- Useful for analyzing the effect of tutoring on grades.",
                "- Majority of students do not receive tutoring.",
                "- While the minority of students receive tutoring."
            ],
            'ParentalSupport': [
                "- Shows the level of parental support students receive.",
                "- Helps understand the role of family involvement in education.",
                "- Countplot of students' parental support forms a rough bell curve.",
                "- Majority of students receive moderate parental support.",
                "- Closely folowed by high parental support.",
                "- While the minority of students receive no parental support."
            ],
            'Extracurricular': [
                "- Displays the number of students involved in extracurricular activities.",
                "- Can be used to examine the impact on academic performance.",
                "- Majority of students are not involved in any extracurricular activities.",
                "- While the minority of students are involved in some type of extracurricular activities."

            ],
            'Sports': [
                "- Represents students' participation in sports.",
                "- Useful for analyzing the balance between academics and athletics.",
                "- Majority of students are not involved in any sports.",
                "- While the minority of students are involved in some type of sports."
            ],
            'Music': [
                "- Shows the number of students involved in music-related activities.",
                "- Can indicate the relationship between music and academic success.",
                "- Majority of students are not involved in any music-related activities.",
                "- While the minority of students are involved in some type of music-related activities."
            ],
            'Volunteering': [
                "- Displays the proportion of students engaged in volunteering.",
                "- Helps assess students’ involvement in community service.",
                "- Majority of students are not involved in any volunteering activities.",
                "- While the minority of students are involved in some type of volunteering activities."
            ],
            'Gender': [
                "- Compares the number of male and female students.",
                "- Useful for gender-based performance analysis.",
                "- Approximately equal distribution of both genders in the dataset.",
                "- Females lead slightly in numbers."
            ]
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
            st.pyplot(plt)  

            st.write("### 📊 Insights & Interpretation")
            st.markdown("\n".join(descriptions.get(selected_column, [f"- Distribution of {selected_column}."])))
        else:
            st.warning(f"No custom labels defined for column: {selected_column}")

        with st.expander("ℹ️ **Why Bar Charts?**"):
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

    elif visualization_option == "📈Histogram":
        st.subheader("Histogram of Numerical Columns")
        numerical_columns = [col for col in df.columns if df[col].nunique() > 5 and col != 'StudentID']
        selected_column = st.selectbox("Select a numerical column to visualize", numerical_columns)

        plt.figure(figsize=(8, 5))
        sns.histplot(df[selected_column], kde=True, bins=20)
        plt.title(f'Histogram of {selected_column}')
        plt.xlabel(selected_column)
        plt.ylabel('Frequency')
        plt.tight_layout()
        st.pyplot(plt)

        # ✅ Individual descriptions based on the selected column
        column_descriptions = {
            "GPA": [
                "- Represents the distribution of student GPAs.",
                "- Helps identify the most common GPA range.",
                "- Can highlight performance gaps or outliers.",
                "- GPA of students range between 0.0 to 4.0.",
                "- Histogram shows a rough bell curve, indicating a normal distribution of GPA.",
                "- Mean GPA of students are approximately 2.0."
            ],
            "StudyTimeWeekly": [
                "- Shows the distribution of hours spent studying per week.",
                "- Helps determine if most students study enough or too little.",
               "- Useful for analyzing study habits in relation to performance.",
                "- Study time of students range between 0 to 20 hours.",
                "- Histogram shows a right skewed distribution, indicating that most students study less than 10 hours weekly."
            ],
            "Absences": [
                "- Displays the number of absences per student.",
                "- Can indicate patterns of absenteeism affecting performance.",
                "- Helps in identifying students who may need intervention.",
                "- Absences of students range between 0 to 30.",
                "- Histogram shows an uneven distribution, indicating that there is no clear pattern of absences."
            ],
        }

        # Display the selected column’s specific description
        st.write("### 📊 Insights & Interpretation")
        description = column_descriptions.get(selected_column, ["- No specific insights available for this column."])
        st.markdown("\n".join(description))

        with st.expander("ℹ️ **Why Histograms?**"):
            st.markdown("""
            ### Histogram Analysis
            - **Purpose**: 
                - Understand the distribution and frequency of numerical data across the dataset.
            - **Visualization**: 
                - The histogram displays the frequency of values within specified bins, providing a clear view of how the data is spread.
            - **Insights**: 
                - Identify patterns such as skewness, central tendency, and outliers in numerical variables like GPA, absences, or study time.
                - Highlight any unusual trends or concentrations in the data.
            - **Actionable Use**: 
            - Tailor interventions or resources based on observed patterns (e.g., addressing high absence rates or improving study habits for low GPA students).
            """)

    elif visualization_option == "⭐Correlations":
        st.subheader("Correlation Heatmap")
        corr_matrix = df.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Matrix")
        plt.tight_layout()
        st.pyplot(plt)
        st.markdown("""
        ### Correlation Matrix Analysis
        - **Purpose**: 
            - Understand the relationships and dependencies between numerical variables in the dataset.
        - **Visualization**: 
            - The correlation heatmap displays the strength and direction of correlations (ranging from -1 to 1) between pairs of numerical variables.
            - The color intensity indicates the strength of the correlation.
            - Positive correlations are shown in red, while negative correlations are shown in blue.
            - Positive values indicate a direct relationship, while negative values indicate an inverse relationship.
        - **Insights**: 
            - Identify strongly correlated variables that may influence each other.
            - Highlight weak or no correlations to determine independent variables.
            - Absences and GPA have a strong negative correlation of -0.80, indicating that as absences increase, GPA tends to decrease.
            - GPA and Grade Class have a strong negative correlation of -0.75, indicating that higher GPAs are associated with lower grade classes.
        - **Actionable Use**: 
            - Focus on highly correlated variables when designing interventions (e.g., improving study habits if it strongly correlates with GPA).
            - Exclude redundant features in machine learning models to improve performance and interpretability.
        """)

    elif visualization_option == "❌Absences":
        plt.figure(figsize=(8, 5))
        
        # Scatter plot with trend line
        sns.regplot(x=df["Absences"], y=df["GPA"], scatter_kws={'alpha':0.6}, line_kws={"color": "red"})
        
        plt.title("Relationship Between Absences and GPA")
        plt.xlabel("Number of Absences")
        plt.ylabel("GPA")
        plt.grid(True)
        st.pyplot(plt) 

        st.write("### 📊Insights & Interpretation")
        st.markdown("""
        - **Negative Correlation**: More absences may lead to lower GPA.
        - **Outliers**: Very few students with higher GPA despite many absences.
        - **Trend Line**: The red regression line shows the general relationship between absences and GPA.
        - **Actionable Insights**:
          - Identify students with excessive absences for intervention.
          - Compare this trend with other factors like study time or parental support.
        """)

        with st.expander("ℹ️ **Why absences?**"):
            st.markdown("""
            ### Absence Analysis
            - **Reason**: Number of absences is the **strongest correlated** variable with GPA.
            - **Purpose**: Understand the distribution of student absences based on GPA.
            - **Insights**: Identify trends in absences correlated with GPA.
            - **Actionable Use**: Develop strategies to reduce absences for students with high absence rates.
            """)

elif page == "🔖Insert Data":
    st.title("Manage Student Records")

    # Hard-coded MongoDB Atlas connection settings
    CLOUD_CONN = "mongodb+srv://jun:jungjunwon0822@cluster0.6utno.mongodb.net/"
    CLOUD_DB_NAME = "Student"
    CLOUD_COLL_NAME = "student_info"

    # --- CONNECT TO MONGODB (runs automatically on page load) ---
    try:
        cloud_client = MongoClient(CLOUD_CONN)
        st.success("Connection to MongoDB Atlas succeeded!")
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

    clouddb = cloud_client[CLOUD_DB_NAME]
    cloudrecordcol = clouddb[CLOUD_COLL_NAME]

    # Ensure StudentID is unique
    cloudrecordcol.create_index("StudentID", unique=True)

    # --- BUTTON: Check & Remove Duplicates ---
    st.subheader("Check and Remove Duplicates")
    if st.button("Check for duplicates"):
        pipeline = [
            {"$group": {"_id": "$StudentID", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        try:
            cloud_duplicates = list(cloudrecordcol.aggregate(pipeline))
            if cloud_duplicates:
                st.warning(f"Duplicates found in cloud collection: {cloud_duplicates}")

                # OPTIONAL: Remove duplicates, leaving one record per StudentID
                # (Below is a simple approach—adapt as needed)
                for doc in cloud_duplicates:
                    student_id = doc["_id"]
                    duplicates_cursor = cloudrecordcol.find({"StudentID": student_id})
                    first_doc = True
                    for duplicate in duplicates_cursor:
                        if first_doc:
                            first_doc = False  # keep the first doc
                            continue
                        # remove subsequent duplicates
                        cloudrecordcol.delete_one({"_id": duplicate["_id"]})

                st.success("Duplicates removed (one record kept for each StudentID).")
            else:
                st.write("No duplicates found in cloud collection.")
        except errors.PyMongoError as e:
            st.error(f"Error checking or removing duplicates: {e}")

    st.subheader("➕ Add a New Student Record")
    # Now define the form for adding a single new student
    with st.form("new_student_form"):
        new_student_id = st.text_input("StudentID")
        new_age = st.number_input("Age", min_value=15, max_value=18)
        new_gender = st.selectbox("Gender", options=["", "Male", "Female", "Other"], index=0)
        new_ethnicity = st.selectbox("Ethnicity", options=["", "0", "1", "2", "3"], index=0)
        new_parentaleducation = st.selectbox("Parental Education", options=["", "0", "1", "3", "4"], index=0)
        new_weeklystudytime = st.number_input("Weekly Study Time", min_value=0, max_value=168)
        new_absences = st.number_input("Absences", min_value=0, max_value=30)
        new_tutoring = st.selectbox("Tutoring", options=["", "0", "1"], index=0)
        new_parentalsupport = st.selectbox("Parental Support", options=["", "0", "1", "3", "4"], index=0)
        new_extracurricularactivities = st.selectbox("Extracurricular Activities", options=["", "0", "1"], index=0)
        new_sports = st.selectbox("Sports", options=["", "0", "1"], index=0)
        new_music = st.selectbox("Music", options=["", "0", "1"], index=0)
        new_volunteering = st.selectbox("Volunteering", options=["", "0", "1"], index=0)
        new_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, value=0.0, step=0.1)
        new_gradeclass = st.number_input("GradeClass", min_value=0, max_value=4)
        new_submitted = st.form_submit_button("Add Student")

        if new_submitted:
            # Create the new record dictionary
            new_record = {
                "StudentID": new_student_id,
                "Age": new_age,
                "Gender": new_gender,
                "Ethnicity": new_ethnicity,
                "Parental Education": new_parentaleducation,
                "Weekly Study Time": new_weeklystudytime,
                "Absences": new_absences,
                "Tutoring": new_tutoring,
                "Parental Support": new_parentalsupport,
                "Extracurricular Activities": new_extracurricularactivities,
                "Sports": new_sports,
                "Music": new_music,
                "Volunteering": new_volunteering,
                "GPA": new_gpa,
                "GradeClass": new_gradeclass
            }
            st.write("New Record:", new_record)

    #Check if StudentID exists, then insert
    try:
        existing_doc = cloudrecordcol.find_one({"StudentID": new_student_id})
        if existing_doc:
            st.error(f"Student with ID {new_student_id} already exists. "
                     "Please use a different ID or update the existing record.")
        else:
            insert_result = cloudrecordcol.insert_one(new_record)
            st.success(f"Student {new_student_id} added! Inserted ID: {insert_result.inserted_id}")
    except Exception as e:
        st.error(f"Insertion failed: {e}")
