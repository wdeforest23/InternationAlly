FROM python:3.12.2-bullseye

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Expose port
EXPOSE 8080

# Set working directory
WORKDIR /app

# Copy all project files
ADD . ./

# Copy the requirements file into the container
# COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# RUN python -m pip install --no-cache-dir -r requirements.txt

# Install dependencies, including vertexai and transformers
RUN python -m pip install --no-cache-dir \
        streamlit==1.33.0 \
        google-generativeai==0.5.0 \
        python-dotenv==1.0.1 \
        vertexai \
        transformers \
        geopandas
        

# Start Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080"]