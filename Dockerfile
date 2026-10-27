# Reproducible runtime for the Male Infertility Burden analysis & dashboard.
# Build:  docker build -t mi-burden .
# Run:    docker run -p 8501:8501 mi-burden
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit listens on 8501; --server.headless avoids the browser popup.
EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
