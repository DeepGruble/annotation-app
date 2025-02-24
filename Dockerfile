# Use an official Python runtime as base image
FROM python:3.11

# Copy the project files into the container
COPY requirements.txt requirements.txt
COPY src/ src/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false", "--server.address=0.0.0.0"]


