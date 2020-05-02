FROM python:3.8
LABEL maintainer="a.s.pridachin@gmail.com"

RUN apt-get update && apt-get -y upgrade

WORKDIR /code
COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/common.txt

CMD ["python", "./run.py"]

