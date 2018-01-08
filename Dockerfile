FROM ubuntu:latest
MAINTAINER Thomas Spycher

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y ghostscript
RUN pip install --upgrade pip

RUN apt-get install -y supervisor nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# INSTALL THE BROWSER
#RUN apt-get install -y chromium-browser xvfb x11vnc
#RUN Xvfb :99 > /dev/null 2>&1 &
#RUN x11vnc -display :99 -bg -nopw -xkb

#COPY . /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install uwsgi

# install letsencrypt client
RUN apt-get install -y wget
RUN wget https://dl.eff.org/certbot-auto -O /usr/local/bin/certbot-auto
RUN chmod a+x /usr/local/bin/certbot-auto
RUN mkdir -p /app/certs
#RUN /usr/local/bin/certbot-auto certonly --non-interactive --webroot -w /app/certs -d dashboard.aecs-fricktal.ch --agree-tos --email flugbetrieb@aecs-fricktal.ch
#RUN /usr/local/bin/certbot-auto certonly --manual -d dashboard.aecs-fricktal.ch --agree-tos --email flugbetrieb@aecs-fricktal.ch
ENV LETSENCRYPT_KEY="No key Provided"


EXPOSE 443
ENV PYTHONPATH /app

# fucking timezones
ENV TZ=Europe/Zurich
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#ENTRYPOINT ["python"]
#CMD ["dashaggregator/server.py"]

#ENTRYPOINT ["uwsgi"]
#CMD ["--ini", "uwsgi.ini"]
#CMD ["--socket", "0.0.0.0:9000", "--protocol=http", "-w", "wsgi"]


#chromium-browser --app=http://example.com --start-fullscreen


ADD supervisor.conf /etc/supervisor/conf.d/
ADD default.conf /etc/nginx/sites-enabled/default
ADD init-wsgi.sh /var/local/
RUN chmod +x /var/local/init-wsgi.sh

EXPOSE 80
EXPOSE 443
CMD supervisord -n