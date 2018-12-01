
FROM debian:stretch
RUN apt-get update \
    && apt-get install -yq python-pip git python-setuptools python-dev
RUN apt-get -yq install sox pulseaudio-utils

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY pulse-client.conf /etc/pulse/client.conf

CMD ["python", "./main.py"]
