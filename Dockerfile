# Use the official Python image as base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the command to start the app. this will execute only if docker run is
# executed without other command line arguments
CMD ["flask", "run", "--host", "0.0.0.0", "-p", "5000"]
