import streamlit as st
import google.generativeai as genai
import json
import requests
from db_connection import get_mongo_client
import logging
from PIL import Image
import io
from io import BytesIO
import numpy as np

from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv


load_dotenv()
headers = {"Authorization": "Bearer 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"}
mongo_client = get_mongo_client()
# Assuming DALLE module for text-to-image conversion

# Hugging Face API settings
API_URL_FLUX = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
API_URL_Midjourney = "https://api-inference.huggingface.co/models/Jovie/Midjourney"
headers = {"Authorization": "Bearer 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"}
genai.configure(api_key='AIzaSyDJwy0_cazhBdIn9I673-W7nOmxeDZXBVo')

st.set_page_config(
    page_title="Marketing Content Generator",
    page_icon="📅",
)

def query(payload,API_URL):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response




def upload_image_to_s3(file_path,date, bucket_name="pythonteam" ):
    object_name="new folder/"+date+".png"
    # Initialize the S3 client with your credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY")
    )

    try:
        # Upload the file to the specified S3 bucket and object path
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ContentType': 'image/png'})
        print(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_name}")

        # Generate the public URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        print("Image uploaded successfully:", file_url)
        return file_url

    except NoCredentialsError:
        print("Credentials not available.")
        return None

st.write("# 7-Day Marketing Content Generator 📅")

# Input fields
business_domain = st.text_input("Business Domain")
Specific_Focus = st.text_area("Specific Focus")
Target_Audience = st.text_area("Target Audience")
# business_detail = st.text_area("Business Details")
# product_description = st.text_area("Product Description")
Key_Features = st.text_area("Key Features")
Unique_Selling_Points = st.text_area("Unique Selling Points")
Pricing_and_Packages = st.text_area("Pricing & Packages")
target_platform = st.selectbox("Target Social Media Platform", ["Facebook", "Instagram", "Twitter", "LinkedIn"])

if st.button("Generate 7-Day Marketing Content"):
    # Initialize the generative model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Input prompt for generative model
    input_prompt = """
        You are an expert in understanding business and generating content for marketing purposes.
        You will receive a Business Domain, Product Description, and Target Social Media Platform.

        Your task is:
        1. Create a punchline that grabs attention.
        2. Generate 125-word content focused on the provided business information and product description.
        3. Provide 5 relevant hashtags that align with the marketing strategy and target audience.
        4. 5 Keywords that can help me generate an Iconic image.
        # provide this information in json format only and it should contain Title, Punchline, Content, hashtags, Keywords .
        # Be sure of the Json Syntax and formate
    """

    # Prepare input text
    input_text = f"""
        Business Domain = {business_domain},
        Specific Focus = {Specific_Focus},
        Target Audience = {Target_Audience},
        Key Features = {Key_Features},
        Unique Selling Points = {Unique_Selling_Points},
        Pricing & Packages = {Pricing_and_Packages},
        Target Platform = {target_platform}
    """

    # Store results for 7 days
    seven_day_content = []
    
    for day in range(1, 8):
        st.write(f"### Day {day} Marketing Content")
        
        # Modify the prompt slightly for each day to ensure uniqueness
        day_specific_prompt = input_prompt + f"\nGenerate content for Day {day}. Make sure it's different from previous days."
        
        # Generate content for the day
        completion = model.generate_content([input_text, day_specific_prompt])
        response_text = completion.text
        
        # Display the content for the day
        st.write(f"**Generated Content for Day {day}:**")
        st.write(response_text)
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').strip()
            if response_text.endswith('```'):
                response_text = response_text[:-3].strip()

        json_data = json.loads(response_text)
        # Save the response for later use (optional)
        seven_day_content.append({
            "day": day,
            "generated_text": json_data
        })
        # seven_day_content.append(response_text)

    # Display all 7-day content as JSON
    st.json(seven_day_content)
   

    filename= datetime.now().date()
    image_model="FLUX"
    
    for text in seven_day_content:
        content= text['generated_text']
        print(content)
        if json_data:
            title = content["Title"]
            Punchline = content["Punchline"]
            Keywords = content["Keywords"]
            # Choose model API URL based on the selection
            # model_url = API_URL_FLUX if image_model == "FLUX" else API_URL_Midjourney
            model_url=API_URL_Midjourney
            input_text1 = f""" create a attractive image for social media for Marketing of product with {Punchline} and {title} and some of the Keywords to consider {Keywords} """
            # Generate the image from the generated marketing text
            response = query({"inputs": input_text1}, model_url)
            print(response)
            if response.status_code == 200:
                try:
                    # Attempt to open the image from the response content
                    image = Image.open(io.BytesIO(response.content))

                    # Display the generated image
                    st.image(image, caption=f"Generated Image ({image_model})", use_column_width=True)
                    date=filename.strftime("%x")
                    date=date.replace('/','-')
                    image.save(date+".png")
                    content["Date"]= date
                    file_url= upload_image_to_s3(date+".png", date)
                    content["Image_URL"]= file_url
                    filename=filename + timedelta(days=1)
                    if os.path.exists(date+".png"):
                        os.remove(date+".png")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
                    st.write("Response content:", response.content)  # Debugging info to check response content
            else:
                # Display an error message if the request failed
                st.error(f"Image generation failed with status code: {response.status_code}. Response: {response.text}")
        else:
            st.warning("No marketing content to generate an image from. Please generate marketing content first.")

        if mongo_client:
            db = mongo_client["Marketing_data"]
            content_collection = db["content_collection"]
            inserted_id = content_collection.insert_one(content).inserted_id
            content["_id"] = str(inserted_id)
            logging.info(f"Inserted content collection with ID: {inserted_id}")
