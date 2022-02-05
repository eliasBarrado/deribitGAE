FROM python:3.8
COPY . /project
WORKDIR /project
ENV GOOGLE_APPLICATION_CREDENTIALS="key.json"
RUN pip install -r requirements.txt
CMD ["python","main.py"]