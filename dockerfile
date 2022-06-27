FROM python:3.6.2-jessie

RUN echo deb http://ftp.ru.debian.org/debian/ jessie main non-free contrib >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y install sudo \
    libreoffice --no-install-recommends \
    openjdk-7-jre-headless \
    ttf-mscorefonts-installer \
    && pip install --no-cache-dir --upgrade pip \
    && pip install aiohttp \
    && rm -rf /var/lib/apt/lists/*

ADD main.py /proxy/main.py

ENV PORT 6000

CMD ["python", "-u", "/proxy/main.py"]