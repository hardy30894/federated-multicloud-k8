# Start with a Linux micro-container to keep the image tiny
FROM ubuntu

# Document who is responsible for this image
MAINTAINER Harsh Dubey "hd2225@nyu.edu"

# Install just the Python runtime (no dev)
RUN apt-get update && apt-get install -y \
    python3 python3-dev gcc gfortran musl-dev \
    python3-pip ca-certificates

# Expose any ports the app is expecting in the environment


# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install --upgrade pip setuptools 
RUN pip3 install -r requirements.txt


# Add the code as the last Docker layer because it changes the most
ADD templates  /app/templates
ADD Upload  /app/Upload
ADD main.py  /app/main.py
EXPOSE 9002
ENV PORT 9002
#ENV COUNTING_SERVICE_URL http://172.17.0.7:9001
ENV COUNTING_SERVICE_URL http://counting.service.consul:9001

# Run the service
CMD [ "python3", "main.py"]