import streamlit as st
import pandas as pd
import os
import zipfile
import logging
from bing_image_downloader import downloader

# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to search for university logo
def search_university_logo(university):
    try:
        downloader.download(f"{university} logo", limit=1,  output_dir='uni_logos', adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
    except Exception as e:
        logging.error(f"Error searching for logo for {university}: {str(e)}")

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
            os.makedirs("uni_logos", exist_ok=True)  # Use exist_ok=True to avoid errors if the directory already exists

            logo_urls = {}
            for university in df["University"]:
                search_university_logo(university)
                logo_filename = f"uni_logos/{university} logo/image.jpg"  # Updated path to the downloaded image
                if os.path.exists(logo_filename):
                    logo_urls[university] = logo_filename

            # Zip the logos
            zip_filename = "university_logos.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                exceptions = {}
                for university, logo_filename in logo_urls.items():
                    try:
                        zipf.write(logo_filename, f"{university}.jpg")
                        logging.info(f"Fetched logo for {university}")
                    except Exception as e:
                        exceptions[university] = str(e)
                        logging.error(f"Error fetching logo for {university}: {str(e)}")

            # Display logos and exceptions
            for university, logo_filename in logo_urls.items():
                st.write(f"Logo for {university}:")
                try:
                    st.image(logo_filename, use_column_width=True)
                except:
                    pass

            if exceptions:
                st.write("Exceptions in fetching logos:")
                st.write(exceptions)

            # Provide download link for the zip file
            st.write("### Download Logos")

            # Generate a download button for the zip file
            with open(zip_filename, "rb") as fp:
                st.download_button(
                    label="Download ZIP",
                    data=fp,
                    file_name=zip_filename,
                    key='download-zip-button',  # Add a key to the button to avoid duplicate buttons
                    mime="application/octet-stream"
                )

        else:
            st.write("CSV file must contain a column named 'University'.")

    except pd.errors.EmptyDataError:
        st.write("Uploaded file is empty or not in CSV format")

# Log when the app finishes
logging.info("University Logo Scraper finished")
