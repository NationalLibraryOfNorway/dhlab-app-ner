FROM python:3.11-slim
EXPOSE 8501
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
        