FROM ubuntu:latest
MAINTAINER Thomas Spycher
EXPOSE 80
EXPOSE 443

ENV PYTHONPATH /app
ENV LETSENCRYPT_KEY="No key Provided"
ENV TZ=Europe/Zurich

# update and install basics
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential vim
RUN apt-get install -y ghostscript
RUN pip install --upgrade pip
RUN apt-get install -y supervisor nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# install the application
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install uwsgi

# install letsencrypt client
RUN apt-get install -y wget
RUN wget https://dl.eff.org/certbot-auto -O /usr/local/bin/certbot-auto
RUN chmod a+x /usr/local/bin/certbot-auto
#RUN /usr/local/bin/certbot-auto --non-interactive --os-packages-only
RUN /usr/local/bin/certbot-auto register --agree-tos --email flugbetrieb@aecs-fricktal.ch --non-interactive || true
RUN sh -c "[ -f /app/certs/letsencrypt.tar ] && tar -xvf certs/letsencrypt.tar -C /"
#RUN /usr/local/bin/certbot-auto certonly --manual -d dashboard.aecs-fricktal.ch --agree-tos --email flugbetrieb@aecs-fricktal.ch

# fucking timezones
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crontabs
RUN apt-get install -y cron
ADD crontab /etc/cron.d/letsencrypt-cron
RUN chmod 0644 /etc/cron.d/letsencrypt-cron
RUN touch /var/log/cron.log
RUN service cron start

# Configure Supervisord,Nginx and UWSGI
ADD supervisor.conf /etc/supervisor/conf.d/
ADD default.conf /etc/nginx/sites-enabled/default
#ADD init-wsgi.sh /var/local/
#RUN chmod +x /var/local/init-wsgi.sh

# Start
CMD supervisord -n