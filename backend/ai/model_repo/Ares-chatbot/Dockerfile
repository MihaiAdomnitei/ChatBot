# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the app using uvicorn
# Note: "application.app:app" means:
# - "application" folder
# - "app.py" file
# - "app" FastAPI instance
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
