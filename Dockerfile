FROM alpine:edge

RUN apk add --update py3-pip
RUN python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY Website/ /usr/src/app/Website
COPY instance/ /usr/src/app/instance
COPY main.py /usr/src/app/main.py

RUN ls -la /usr/src/app/

EXPOSE 5000

CMD ["python3", "/usr/src/app/main.py"]