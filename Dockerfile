FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command to run the interactive REPL
# Can be overridden to run tests (e.g. `CMD ["python", "main.py", "--test"]`)
CMD ["python", "main.py"]
