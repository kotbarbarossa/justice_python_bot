FROM python:3.10-slim
RUN mkdir /app
COPY requirements.txt /app
COPY .env /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY justice_python_bot/ /app
WORKDIR /app
CMD ["python3", "justice_bot_main.py"]