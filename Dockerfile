FROM frolvlad/alpine-glibc as base

FROM base AS build

WORKDIR /opt

RUN apk --no-cache add py-pip python-dev git 

RUN apk --no-cache add gcc g++ make libffi-dev openssl-dev && pip install --upgrade pip

COPY . /opt/

RUN pip install --install-option="--prefix=/build" -r /opt/requirements.txt

#Multistage build requires docker => 17.05

FROM base

WORKDIR /opt

RUN apk --no-cache add py-pip python 

COPY --from=build /build /usr
COPY --from=build /opt /opt

RUN pip install -r /opt/requirements.txt

RUN chmod +x /opt/start.py

ENTRYPOINT /opt/start.py
