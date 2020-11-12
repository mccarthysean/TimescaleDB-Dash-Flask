
FROM python:3.8-slim

COPY requirements.txt /
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY wsgi.py gunicorn-cfg.py config.py .env entrypoint.sh /
COPY app app 
COPY migrations migrations
# COPY instance instance
# COPY cron cron

# RUN apt-get update && \
#     apt-get install -y cron && \
#     echo "0 2 "

ENV FLASK_APP wsgi.py
EXPOSE 5005

CMD ["/bin/bash", "/entrypoint.sh"]
