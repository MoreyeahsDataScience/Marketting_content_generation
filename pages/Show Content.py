import streamlit as st
from db_connection import get_mongo_client
import pandas as pd
from PIL import Image
import requests
from io import BytesIO


def show_image(image_url):
    response = requests.get(str(image_url))
    img = Image.open(BytesIO(response.content))
   
    # Streamlit app
    st.title("Image from Google Drive")
    st.image(img, caption='Fetched from Google Drive', use_column_width=True)
# Enhanced function to convert Google Drive link to direct image link
def get_direct_gdrive_link(gdrive_url):
    if "drive.google.com" in gdrive_url:
        # Extract file ID using a more robust method
        try:
            file_id = gdrive_url.split("/d/")[1].split("/")[0]
            # Convert to direct download link format
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        except IndexError:
            st.error("Invalid Google Drive URL format. Could not extract file ID.")
            return None
    return gdrive_url  # Return the original URL if it's not from Google Drive

# Function to fetch data from MongoDB
def fetch_data_from_mongo():
    client = get_mongo_client()
    if not client:
        st.error("Failed to connect to MongoDB.")
        return []  # Return an empty list if connection fails

    # Connect to the specific database and collection
    db = client["Marketing_data"]
    collection = db["content_collection"]
    
    # Fetch data from MongoDB collection
    data = list(collection.find())
    
    # Convert to JSON-friendly format if necessary
    for record in data:
        record["_id"] = str(record["_id"])  # Convert ObjectId to string
    
    return data

# Streamlit page layout
st.title("MongoDB Data Viewer - JSON with Images")

# Fetch and display data automatically on page load
data = fetch_data_from_mongo()

if data:
    for record in data:
        st.json(record)  # Display JSON data

        # Check for an image URL in the JSON record and display the image
        image_url = record["Image_URL"]
        image_url=get_direct_gdrive_link(image_url)
        # image_url = "https://drive.google.com/uc?export=view&id=1rW2o3tvvsypXVvTDPVOL1r1N_W8_LHOu"
        print(image_url)
        if image_url:
            show_image(image_url)
        else:
            st.write("Invalid or inaccessible image URL.")
else:
    st.write("No data found in the specified collection.")
