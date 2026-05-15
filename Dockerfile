# Use Python 3.11 slim image
FROM python:3.11-slim

# Set up a new user with UID 1000 (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# Copy the requirements file and install dependencies
COPY --chown=user requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY --chown=user . $HOME/app

# Ensure the data directory exists and is writable
RUN mkdir -p $HOME/app/data

# Expose the port Gradio runs on
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]
