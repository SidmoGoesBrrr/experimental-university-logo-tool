import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# Function to search for university logo
def search_university_logo(university):
    try:
        query = f"{university} logo site:.edu"  # Search for university logo on .edu domains
        for j in search(query, num=1, stop=1, pause=2):
            page = requests.get(j)
            soup = BeautifulSoup(page.content, 'html.parser')
            logo = soup.find("img", {"alt": f"{university} logo"})
            if logo:
                return logo['src']

        # If not found on .edu domain, try searching on Google Images
        query = f"{university} logo"
        for j in search(query, num=1, stop=1, pause=2, tbs='isz:l'):
            return j

    except Exception as e:
        return None

# Streamlit app
st.title("University Logo Scraper")

# Upload CSV file
st.write("Upload a CSV file with a column named 'University'")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if "University" in df.columns:
            st.write("Universities to fetch logos for:")
            st.write(df)

            for university in df["University"]:
                logo_url = search_university_logo(university)
                if logo_url:
                    st.write(f"Logo for {university}:")
                    st.image(logo_url, use_column_width=True)
                else:
                    st.write(f"Logo for {university} not found.")
        else:
            st.write("CSV file must contain a column named 'University'.")

    except pd.errors.EmptyDataError:
        st.write("Uploaded file is empty or not in CSV format.")

# Requirements.txt
st.write("### Requirements.txt")
with open("requirements.txt", "r") as file:
    st.code(file.read())

