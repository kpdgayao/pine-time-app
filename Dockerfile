FROM python:3.9-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY admin_dashboard/requirements.txt admin_dashboard_requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r admin_dashboard_requirements.txt

# Copy the application code
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Create a script to run both services
RUN echo '#!/bin/bash\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 & \n\
cd admin_dashboard && streamlit run user_app.py --server.port 8501 --server.address 0.0.0.0\n\
wait\n' > /app/start.sh

RUN chmod +x /app/start.sh

# Command to run the services
CMD ["/app/start.sh"]
