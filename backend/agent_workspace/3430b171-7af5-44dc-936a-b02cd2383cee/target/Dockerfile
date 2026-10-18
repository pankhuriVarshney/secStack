FROM python:3.11-slim
RUN pip install --no-cache-dir flask==3.0.3
WORKDIR /app
ARG FLAG
RUN echo -n "$FLAG" > /flag.txt && chmod 400 /flag.txt
COPY app.py .
EXPOSE 80
CMD ["python", "app.py"]
