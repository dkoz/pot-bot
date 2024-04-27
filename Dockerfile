FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 7600

CMD ["bash", "-c", "python main.py & python app.py && wait"]
