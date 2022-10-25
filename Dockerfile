FROM python:3.10.8-slim-buster

RUN mkdir /ifs
COPY . /ifs
COPY .dockerConfig/start.py /ifs
WORKDIR /ifs
RUN python3.10 -m pip install -r requirements.txt

EXPOSE 1081
EXPOSE 1082
EXPOSE 1083

CMD ["python3.10", "-u", "start.py"]