FROM ubuntu:latest
MAINTAINER Thomas Spycher

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip


# INSTALL THE BROWSER
#RUN apt-get install -y chromium-browser xvfb x11vnc
#RUN Xvfb :99 > /dev/null 2>&1 &
#RUN x11vnc -display :99 -bg -nopw -xkb

#COPY . /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install uwsgi

EXPOSE 80
ENV PYTHONPATH /app

#ENTRYPOINT ["python"]
#CMD ["dashaggregator/server.py"]

ENTRYPOINT ["uwsgi"]
CMD ["--ini", "uwsgi.ini"]
#CMD ["--socket", "0.0.0.0:9000", "--protocol=http", "-w", "wsgi"]


#chromium-browser --app=http://example.com --start-fullscreen
