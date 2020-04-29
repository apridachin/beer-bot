FROM python:3.8

RUN apt-get update && apt-get -y upgrade

COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/common.txt

CMD ["python", "./run.py"]

