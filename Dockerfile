# Use Python 3.9
FROM python:3.9

# Set working directory
WORKDIR /code

# Copy requirements and install them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all your files
COPY . .

# Create the templates directory if it doesn't exist (safety check)
RUN mkdir -p templates

# Fix permissions (Hugging Face specific)
RUN chmod -R 777 /code

# Command to run the app on port 7860 (Required by Hugging Face)
CMD ["python", "app.py"]