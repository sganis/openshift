FROM python:3.9-slim
WORKDIR /service
COPY app.py requirements.txt ./
RUN pip install -r requirements.txt
EXPOSE 5001
CMD ["python", "app.py"]
