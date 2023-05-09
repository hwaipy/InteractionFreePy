FROM python:3.10.8-slim-buster

RUN mkdir /ifs
COPY . /ifs
COPY .dockerConfig/start.py /ifs
WORKDIR /ifs
RUN python3.10 -m pip install -r requirements.txt

EXPOSE 1061
# EXPOSE 1062
# EXPOSE 1063

CMD ["python3.10", "-u", "start.py"]