# Base Image Python3.7 Stretch
FROM python:3.7-slim

# Maintainer Information:
MAINTAINER Yutao Tang

# Install lower dependencies:
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 xvfb \
    wget unzip libnss3 gnupg2 curl bzip2

# Set the Working Directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt ./

# Install Dependencies
RUN pip3 install -r ./requirements.txt

# install geckodriver and firefox

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

#COPY . /app

# Healthcheck
HEALTHCHECK CMD pidof python3 || exit 1
