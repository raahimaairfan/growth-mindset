import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Set up Streamlit page
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Advanced Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning, visualization, and enhanced data analysis.")

# File uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")
        st.write("🔍 Preview of the Uploaded File:")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values in Numeric Columns Filled with Column Means!")
            
        # Advanced Data Analysis
        st.subheader("📊 Advanced Data Analysis")
        if st.checkbox(f"Show Data Summary for {file.name}"):
            st.write("**Summary Statistics:**")
            st.write(df.describe())
            
            if df.select_dtypes(include=['object']).shape[1] > 0:
                st.write("**Categorical Data Overview:**")
                cat_summary = df.select_dtypes(include=['object']).describe(include='all')
                st.write(cat_summary)
        
        # Outlier Detection & Removal
        st.subheader("🚨 Outlier Detection & Removal")
        if st.checkbox(f"Detect & Remove Outliers for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            st.write("Outliers removed based on IQR method!")
            st.dataframe(df.head())
        
        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                selected_cols = st.multiselect(f"Choose columns for {file.name} visualization:", numeric_cols, default=numeric_cols[:2])
                chart_type = st.selectbox("Select chart type:", ["Histogram", "Bar Chart", "Scatter Plot", "Line Plot", "Pie Chart"])
                
                fig, ax = plt.subplots(figsize=(8, 4))
                if chart_type == "Histogram":
                    for col in selected_cols:
                        sns.histplot(df[col], kde=True, ax=ax, bins=30, label=col)
                    ax.legend()
                    ax.set_title(f"Distribution of Selected Columns")
                elif chart_type == "Bar Chart":
                    df[selected_cols].plot(kind='bar', ax=ax)
                    ax.set_title(f"Bar Chart of Selected Columns")
                elif chart_type == "Scatter Plot" and len(selected_cols) >= 2:
                    sns.scatterplot(x=df[selected_cols[0]], y=df[selected_cols[1]], ax=ax)
                    ax.set_title(f"Scatter Plot: {selected_cols[0]} vs {selected_cols[1]}")
                elif chart_type == "Line Plot":
                    df[selected_cols].plot(kind='line', ax=ax)
                    ax.set_title(f"Line Plot of Selected Columns")
                elif chart_type == "Pie Chart" and len(selected_cols) == 1:
                    pie_data = df[selected_cols[0]].value_counts()
                    pie_data.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                    ax.set_ylabel('')
                    ax.set_title(f"Pie Chart of {selected_cols[0]}")
                st.pyplot(fig)
            else:
                st.write("No numeric columns available for visualization.")
        
       # Automated Reports (PDF Export)
            st.subheader("📑 Automated Reports (PDF/Markdown Export)")
            if st.button(f"Generate Report for {file.name}"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Data Summary Report for {file.name}", ln=True, align='C')
                pdf.ln(10)
                pdf.multi_cell(0, 10, txt=str(df.describe()))

                pdf_file = BytesIO()
                pdf_bytes = pdf.output(dest='S').encode('latin1')  # Generate PDF as bytes
                pdf_file.write(pdf_bytes)
                pdf_file.seek(0)

                st.download_button(
                    label="Download PDF Report",
                    data=pdf_file,
                    file_name=f"{file.name}_report.pdf",
                    mime="application/pdf"
                )

if uploaded_files:
    st.success("🎉 All files processed successfully!")