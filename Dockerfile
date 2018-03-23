FROM python:3.6
RUN mkdir -p /opt/binverter

COPY ./app.py /opt/binverter/
COPY ./requirements.txt /opt/binverter/
COPY ./templates /opt/binverter/templates
COPY ./uploads /opt/binverter/uploads
COPY ./static /opt/binverter/static
COPY ./fix-permissions /usr/bin/fix-permissions

RUN pip install -r /opt/binverter/requirements.txt
RUN /usr/bin/fix-permissions /opt/binverter/uploads

USER nobody
WORKDIR /opt/binverter

EXPOSE 6699

ENTRYPOINT ["python3", "app.py"]
