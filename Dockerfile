FROM python:3.10-slim-bookworm
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.baseUrlPath", "/ner"]        
