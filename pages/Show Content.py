import streamlit as st
from db_connection import get_mongo_client
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from botocore.exceptions import NoCredentialsError
import os
import boto3
import numpy as np
import cv2
# Access AWS credentials from environment variables
s3_access_key = os.getenv("ACCESS_KEY")
s3_secret_key = os.getenv("SECRET_KEY")
bucket_name = "pythonteam"
folder_name = "new folder/"

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key,
)
def list_images_in_s3(bucket, folder):
    """
    Lists image files in the specified S3 bucket and folder.

    Args:
        bucket (str): S3 bucket name.
        folder (str): Folder path within the bucket.

    Returns:
        list: List of image file keys.
    """
    image_keys = []
    try:
        # List all files in the specified S3 bucket folder
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        if "Contents" not in response:
            print("No files found in the specified folder.")
            return image_keys

        for item in response["Contents"]:
            file_key = item["Key"]
            # Check if the file is an image by extension
            if file_key.endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_keys.append(file_key)

    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error listing images: {e}")

    return image_keys

def show_image_from_s3(bucket, file_key):
    """
    Fetches and decodes an image from S3 and returns it in RGB format.

    Args:
        bucket (str): S3 bucket name.
        file_key (str): File key of the image in the S3 bucket.

    Returns:
        np.ndarray: Decoded image in RGB format or None if an error occurs.
    """
    try:
        # Get the image file from S3
        file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        # Read the file content into a bytes array
        file_content = file_obj["Body"].read()
        # Convert bytes data to a NumPy array for OpenCV
        np_arr = np.frombuffer(file_content, np.uint8)
        # Decode the image using OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # Convert BGR to RGB for correct color display
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return rgb_image

    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error fetching image {file_key}: {e}")
        return None
    
def show_image_from_s3(bucket, file_key):
    """
    Fetches and decodes an image from S3 and returns it in RGB format.

    Args:
        bucket (str): S3 bucket name.
        file_key (str): File key of the image in the S3 bucket.

    Returns:
        np.ndarray: Decoded image in RGB format or None if an error occurs.
    """
    try:
        # Get the image file from S3
        print(file_key)
        file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        # Read the file content into a bytes array
        file_content = file_obj["Body"].read()
        # Convert bytes data to a NumPy array for OpenCV
        np_arr = np.frombuffer(file_content, np.uint8)
        # Decode the image using OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # Convert BGR to RGB for correct color display
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return rgb_image

    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error fetching image {file_key}: {e}")
        return None

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
        mongo_date= record['Date']
        # print(type(mongo_date),"&&&&&", mongo_date)
        st.json(record)  # Display JSON data
        images=list_images_in_s3(bucket_name, folder_name)
        for dates in images:
            dates=str(dates)
            x=dates.split("/")[1]
            y=x.split(".")[0]
            # print(mongo_date, 'fasfuhdilvn;zsin',y)   
            if mongo_date==y:
                # print(mongo_date, 'fasfuhdilvn;zsin',y)
                image=show_image_from_s3(bucket_name, dates)
                cv2.imshow(image)
                st.image(image)
else:
    st.write("No data found in the specified collection.")
