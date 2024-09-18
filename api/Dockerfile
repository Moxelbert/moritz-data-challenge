# Use a lightweight version of Python 3.9
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file first to leverage Docker's cache for dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY main.py database.py models.py ./

# Expose the port the application will run on
EXPOSE 8080

# Use Uvicorn (or Gunicorn) for running the application in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]