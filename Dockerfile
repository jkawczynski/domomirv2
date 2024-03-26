FROM python:3.12-alpine
MAINTAINER jkawczynski

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION


ENV APP_ROOT=/code
WORKDIR $APP_ROOT

ADD requirements.txt $APP_ROOT
ADD docker_entrypoint.sh $APP_ROOT
RUN chmod +x $APP_ROOT/docker_entrypoint.sh

RUN pip install uv
RUN uv venv
RUN uv pip install -r requirements.txt

ADD ./app $APP_ROOT/app

EXPOSE 8000
ENTRYPOINT ["/code/docker_entrypoint.sh"]
