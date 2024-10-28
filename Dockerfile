# # Use the official Python image from the Docker Hub
# FROM python:3.10

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements.txt file to the working directory
# COPY requirements.txt .

# # Install the dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of your application code to the working directory
# COPY . .

# # Expose the port that Streamlit will run on
# EXPOSE 8501

# # Command to run your Streamlit app
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.host=0.0.0.0"]


# FROM ubuntu:latest
# WORKDIR /us/app/src
# ARG LANG-'en_us.UTF-8'
# # Download and Install Dependencies
# RUN apt-get update \
# && apt-get install -y --no-install-recommends \
# apt-utils \
# # build-essentials \
# locales python3-pip \ python3-yaml
# rsyslog system systemd-cron sudo \ && apt-get clean
# RUN pip3 install --upgrade pip
# RUN pip3 install streamlit
# COPY / -/
# #Tell the image what to do when it starts as a container
# CMD ["streamlit" , "run", "app.py"]

# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the working directory
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run your Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.host=0.0.0.0"]
