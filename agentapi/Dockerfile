#syntax=docker/dockerfile:1.2
FROM --platform=$BUILDPLATFORM alpine:3.16 as builder

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG GH_VERSION=2.10.1

RUN export RELEASE_LOCATION="${GH_VERSION}_$(echo "${BUILDPLATFORM//\//_}")" && \
    apk add --no-cache wget rsync && \
    wget https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${RELEASE_LOCATION}.tar.gz && \
    tar -zxvf gh_${RELEASE_LOCATION}.tar.gz && \
    chmod +x gh_${RELEASE_LOCATION}/bin/gh && \
    rsync -az --remove-source-files gh_${RELEASE_LOCATION}/bin/ /usr/bin


FROM alpine:3.16 as gh

RUN apk add --no-cache git libc6-compat
COPY --from=builder /usr/bin/gh /usr/bin/

FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

COPY --from=gh /usr/bin/gh /usr/bin
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN git config --global user.name "AI Agent"
RUN git config --global user.email "mrai@xgeeks.io"

RUN echo "sdfosdkfk" | gh auth login --with-token

# Define environment variable
#ENV NAME world
ENV FLASK_APP=./app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]

EXPOSE 5001
# Run app.py when the container launches