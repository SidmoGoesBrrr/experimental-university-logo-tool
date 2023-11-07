import streamlit as st
import pandas as pd
import os
import zipfile
import logging
from bing_image_downloader import downloader
import shutil

# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to search for university logos
def search_university_logos(university, output_dir):
    try:
        downloader.download(f"{university} logo", limit=6, output_dir=output_dir, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
    except Exception as e:
        logging.error(f"Error searching for logos for {university}: {str(e)}")

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

            zip_filename = "university_logos.zip"

            # Clear the "uni_logos" directory before starting
            if os.path.exists("uni_logos"):
                shutil.rmtree("uni_logos")

            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                exceptions = {}
                for university in df["University"]:
                    university_dir = os.path.join("uni_logos", university)
                    os.makedirs(university_dir, exist_ok=True)

                    search_university_logos(university, output_dir=university_dir)

                    for i in range(1, 7):
                        image_filename = f"{university}/{i}.png"  # Updated path to the downloaded image
                        if os.path.exists(os.path.join("uni_logos", image_filename)):
                            zipf.write(os.path.join("uni_logos", image_filename), image_filename)
                            logging.info(f"Fetched image {i} for {university}")
                        else:
                            exceptions[university] = f"Image {i} not found"

            # Display exceptions
            for university, error_message in exceptions.items():
                st.write(f"Errors for {university}: {error_message}")

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
