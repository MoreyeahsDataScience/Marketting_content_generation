import boto3
import os
import cv2
import numpy as np
from botocore.exceptions import NoCredentialsError
import streamlit as st

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

def list_and_show_images(bucket, folder):
    try:
        # List all files in the specified S3 bucket folder
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        if "Contents" not in response:
            print("No files found in the specified folder.")
            return

        for item in response["Contents"]:
            file_key = item["Key"]
            # Check if the file is an image by extension
            if file_key.endswith((".png", ".jpg", ".jpeg", ".gif")):
                # Get the image file from S3
                file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
                # Read the file content into a bytes array
                file_content = file_obj["Body"].read()
                # Convert bytes data to a NumPy array for OpenCV
                np_arr = np.frombuffer(file_content, np.uint8)
                # Decode the image using OpenCV
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   
                # Display the image
                 # Press any key to close each image window
         # Close all windows after displaying images

    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error fetching images: {e}")

# Call the function to list and show images
list_and_show_images(bucket_name, folder_name)
