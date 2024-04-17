FROM python:3.10-alpine3.17

WORKDIR /app
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

ADD ./src .

CMD [ "python3", "consumer.py" ]
