FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY LICENSE ./LICENSE

# TODO: mount or bake in Swiss Ephemeris .se1 data files and set SE_EPHE_PATH
# ENV SE_EPHE_PATH=/app/ephe

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
