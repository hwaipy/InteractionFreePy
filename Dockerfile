FROM python:3.10.8-slim-buster

RUN mkdir /ifs
COPY . /ifs
COPY .dockerConfig/start.py /ifs
WORKDIR /ifs
RUN python3.10 -m pip install -r requirements.txt

EXPOSE 224
EXPOSE 81
EXPOSE 1082

CMD ["python3.10", "start.py"]