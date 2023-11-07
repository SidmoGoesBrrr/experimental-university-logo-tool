import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import os
import zipfile

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
        return str(e)

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

            # Create a temporary directory to store downloaded logos
            os.makedirs("temp")

            logo_urls = {}
            for university in df["University"]:
                logo_url = search_university_logo(university)
                if logo_url:
                    logo_urls[university] = logo_url

            # Zip the logos
            zip_filename = "university_logos.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                exceptions = {}
                for university, logo_url in logo_urls.items():
                    try:
                        logo = requests.get(logo_url)
                        if logo.status_code == 200:
                            with open(os.path.join("temp", f"{university}.png"), "wb") as f:
                                f.write(logo.content)
                            zipf.write(os.path.join("temp", f"{university}.png"), f"{university}.png")
                        else:
                            exceptions[university] = f"Failed to fetch logo (Status code {logo.status_code})"
                    except Exception as e:
                        exceptions[university] = str(e)

            # Display logos and exceptions
            for university, logo_url in logo_urls.items():
                st.write(f"Logo for {university}:")
                try:
                    st.image(logo_url, use_column_width=True)
                except:
                    pass

            if exceptions:
                st.write("Exceptions in fetching logos:")
                st.write(exceptions)

            # Provide download link for the zip file
            st.write("### Download Logos")
            st.markdown(f"[Download {zip_filename}](temp/{zip_filename})")

        else:
            st.write("CSV file must contain a column named 'University'.")

    except pd.errors.EmptyDataError:
        st.write("Uploaded file is empty or not in CSV format.")

# Cleanup temporary directory
os.rmdir("temp")

