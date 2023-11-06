# dockerfile
FROM python:3.10.12

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN apt-get update

RUN pip install --upgrade pip setuptools_rust wheel \
 && pip install --no-cache-dir -r requirements.txt


COPY main.py /code
COPY feedback_classes.py /code
COPY speeches_and_feedback.json /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
