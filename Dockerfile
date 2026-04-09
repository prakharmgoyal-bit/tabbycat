# Docker file lists all the commands needed to setup a fresh linux instance to
# run the application specified. docker-compose does not use this.

# Grab a python image
FROM python:3.11
SHELL ["/bin/bash", "--login", "-c"]

# Just needed for all things python (note this is setting an env variable)
ENV PYTHONUNBUFFERED 1
# Needed for correct settings input
ENV IN_DOCKER 1
ENV NODE_OPTIONS=--max-old-space-size=1536

# Setup Node/NPM
RUN apt-get update
RUN apt-get install -y curl nginx
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Copy all our files into the baseimage and cd to that directory
WORKDIR /tcd
COPY . /tcd/

RUN nvm install && nvm use

# Set git to use HTTPS (SSH is often blocked by firewalls)
RUN git config --global url."https://".insteadOf git://

# Install our node/python requirements
RUN pip install pipenv
RUN pipenv install --system --skip-lock
RUN pip install autobahn networkx async_timeout dj-database-url daphne resend sib-api-v3-sdk
RUN npm ci --only=production

# Compile all the static files
RUN npm run build

ENV PYTHONPATH=/tcd:/tcd/tabbycat

EXPOSE 10000

CMD python tabbycat/manage.py collectstatic --noinput -v 0 && python tabbycat/manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-10000} tabbycat.asgi:application