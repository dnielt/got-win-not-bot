# syntax=docker/dockerfile:1

FROM python:3.8

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y \
	git unzip xclip vim && \
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	apt install ./google-chrome-stable_current_amd64.deb -y && \
	wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip 
	#&& \ unzip chromedriver.zip chromedriver -d /usr/local/bin/


#  curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-343.0.0-linux-x86_64.tar.gz 
# tar -zxvf google-cloud-sdk-343.0.0-linux-x86_64.tar.gz
# export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/users/daniel/desktop/2021-05-22 telegram bot - GWN/google-api-key/google-key.json"
# ./google-cloud-sdk/bin/gcloud init
#pip install --upgrade google-cloud-vision