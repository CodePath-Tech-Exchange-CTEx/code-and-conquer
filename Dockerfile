# Python image to use.
FROM python:3.10

# Expose 8080 as the port
EXPOSE 8080

# Set the working directory to /app
WORKDIR /app

# Copy the directory contents into the container
COPY ./src ./

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# The main command to run when the container starts.
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
