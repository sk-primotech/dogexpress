# # Use Python as the base image
# FROM python:3.9-slim as builder

# # Set the working directory
# WORKDIR /app

# # Copy the requirements file and install dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Install Allure for reporting
# RUN apt-get update && apt-get install -y openjdk-17-jdk wget curl && \
#     LATEST_URL=$(curl -s https://api.github.com/repos/allure-framework/allure2/releases/latest | grep "tarball_url" | cut -d '"' -f 4) && \
#     wget -O allure-latest.tgz "$LATEST_URL" && \
#     mkdir -p /opt/allure && \
#     tar -xvzf allure-latest.tgz --strip-components=1 -C /opt/allure && \
#     ln -s /opt/allure/bin/allure /usr/bin/allure

# # Final stage
# FROM python:3.9-slim

# # Set the working directory
# WORKDIR /app

# # Copy installed dependencies from the builder stage
# COPY --from=builder /app /app

# # Copy the rest of the project files
# COPY . .

# # Run pytest with Allure
# CMD ["pytest", "--alluredir=allure-results"]



# Use Python as the base image
# Builder stage
FROM python:3.9-slim as builder

# Set the working directory
WORKDIR /app

# Copy only the requirements file first for better caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container
COPY . .

# Install Allure for reporting
RUN apt-get update && apt-get install -y openjdk-17-jdk wget curl && \
    LATEST_URL=$(curl -s https://api.github.com/repos/allure-framework/allure2/releases/latest | grep "tarball_url" | cut -d '"' -f 4) && \
    wget -O allure-latest.tgz "$LATEST_URL" && \
    mkdir -p /opt/allure && \
    tar -xvzf allure-latest.tgz --strip-components=1 -C /opt/allure && \
    ln -s /opt/allure/bin/allure /usr/bin/allure

# Final stage
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy installed dependencies and project files from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Ensure pytest is installed explicitly
RUN pip install --upgrade pip && pip install pytest

# Command to run pytest and generate Allure reports
CMD ["python", "-m", "pytest", "--alluredir=allure-results"]

