FROM whatwewant/zmicro:v1

RUN zmicro package install python

RUN apt install -y python3-dev libldap2-dev libsasl2-dev libmysqlclient-dev

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY ./entrypoint.sh .

CMD ./entrypoint.sh
