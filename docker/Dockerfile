FROM python:3.8

COPY docker/requirements.txt /

RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR "/code"
