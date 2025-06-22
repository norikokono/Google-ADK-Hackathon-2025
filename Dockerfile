# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Start the FastAPI server with uvicorn
CMD ["uvicorn", "multi_tool_agent.api.server:app", "--host", "0.0.0.0", "--port", "8080"]



