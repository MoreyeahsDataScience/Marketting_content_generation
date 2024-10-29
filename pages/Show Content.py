import streamlit as st
from db_connection import get_mongo_client
import pandas as pd
from PIL import Image
from io import BytesIO
from botocore.exceptions import NoCredentialsError
import os
import boto3

# Access AWS credentials from environment variables
s3_access_key = os.getenv("ACCESS_KEY")
s3_secret_key = os.getenv("SECRET_KEY")
bucket_name = "pythonteam"
folder_name = "new folder/"

# Step 1: Check for missing AWS credentials
if not s3_access_key or not s3_secret_key:
    st.error("AWS credentials are missing. Check environment variables.")
else:
    st.write("AWS credentials loaded successfully.")

# Initialize S3 client
try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
    )
    st.write("Successfully connected to S3.")
except Exception as e:
    st.error(f"Error initializing S3 client: {e}")

def list_images_in_s3(bucket, folder):
    """
    Lists image files in the specified S3 bucket and folder.
    """
    image_keys = []
    try:
        # Attempt to list all files in the specified S3 bucket folder
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        
        # Step 2: Check if the folder is empty
        if "Contents" not in response:
            st.warning("No files found in the specified folder.")
            return image_keys

        for item in response["Contents"]:
            file_key = item["Key"]
            if file_key.endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_keys.append(file_key)
        
        st.write(f"Found {len(image_keys)} image(s) in folder '{folder}'.")
        
    except NoCredentialsError:
        st.error("AWS credentials not available.")
    except Exception as e:
        st.error(f"Error listing images in S3: {e}")
    return image_keys

def show_image_from_s3(bucket, file_key):
    """
    Fetches and decodes an image from S3 and returns it in RGB format using Pillow.
    """
    try:
        # Attempt to retrieve the image from S3
        file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        file_content = file_obj["Body"].read()
        image = Image.open(BytesIO(file_content)).convert("RGB")
        st.write(f"Successfully fetched image: {file_key}")
        return image

    except NoCredentialsError:
        st.error("AWS credentials not available.")
    except Exception as e:
        st.error(f"Error fetching image {file_key} from S3: {e}")
        return None

def fetch_data_from_mongo():
    """
    Connects to MongoDB and retrieves data from the specified collection.
    """
    try:
        client = get_mongo_client()
        if not client:
            st.error("Failed to connect to MongoDB.")
            return []  # Return an empty list if connection fails
        
        # Attempt to fetch data from MongoDB
        db = client["Marketing_data"]
        collection = db["content_collection"]
        data = list(collection.find())
        
        # Step 3: Log the number of records retrieved
        st.write(f"Retrieved {len(data)} records from MongoDB.")
        
        # Convert to JSON-friendly format if necessary
        for record in data:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string
        
        return data

    except Exception as e:
        st.error(f"Error fetching data from MongoDB: {e}")
        return []

# Streamlit page layout
st.title("MongoDB Data Viewer - JSON with Images")

# Fetch and display data automatically on page load
data = fetch_data_from_mongo()

if data:
    images = list_images_in_s3(bucket_name, folder_name)
    
    for record in data:
        mongo_date = record.get('Date')
        if not mongo_date:
            st.warning("Record is missing 'Date' field.")
            continue

        st.json(record)  # Display JSON data
        
        # Check for matching images by date
        matched = False
        for dates in images:
            date_str = dates.split("/")[1].split(".")[0]
            if mongo_date == date_str:
                image = show_image_from_s3(bucket_name, dates)
                if image:
                    st.image(image)
                    matched = True
                break
        
        if not matched:
            st.info(f"No matching image found for date: {mongo_date}")
else:
    st.write("No data found in the specified collection.")
