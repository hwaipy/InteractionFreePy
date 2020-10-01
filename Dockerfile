FROM python:3.8.5-slim-buster

RUN mkdir /ifs
COPY . /ifs
COPY .dockerConfig/start.py /ifs
WORKDIR /ifs
RUN python3.8 setup.py install

EXPOSE 224

CMD ["python3.8", "start.py"]