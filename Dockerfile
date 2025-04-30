# syntax=docker.io/docker/dockerfile:1.7-labs

# Base stage - build dependencies

FROM public.ecr.aws/amazonlinux/amazonlinux:latest as builder

# Update installed packages and install system dependencies
RUN dnf update -y \
    && dnf install -y make \
    && dnf install -y wget 

ARG PYTHON_VERSION

# Install python and pip 
RUN dnf install python${PYTHON_VERSION} -y \
    && dnf install python${PYTHON_VERSION}-pip -y

# Create Python Virtual Env
RUN python${PYTHON_VERSION} -m venv /venv

# Create and set work directory (make/pip need this to find Makefile and pyproject.toml)
WORKDIR /df-data-lineage

# Copy the application dependencies
COPY ./pyproject.toml /df-data-lineage
COPY ./Makefile /df-data-lineage

# Copy the app dependency source code into the container.
COPY --from=utils . /packages/utils
COPY --from=df-metadata . /packages/df-metadata
COPY --from=df-app-calendar . /packages/df-app-calendar
COPY --from=df-config --exclude=./cfg . /packages/df-config

# Install app dependencies
RUN source /venv/bin/activate \
    && make install

# Copy the app source code into the container.
COPY --exclude=*.env . /df-data-lineage

# Install app 
RUN source /venv/bin/activate \
    && make install 


# Final stage

FROM public.ecr.aws/amazonlinux/amazonlinux:latest as runner

# Update installed packages and install system dependencies
RUN dnf update -y \
    && dnf install -y make \
    && dnf install -y git \
    && dnf install -y findutils \
    && dnf install -y tree \
    && dnf install -y graphviz
# findutils is needed for xargs command
# shadow-utils is needed for useradd command
# && \ dnf install -y shadow-utils
# graphviz is needed for pydot

ARG PYTHON_VERSION

# Install python and pip 
RUN dnf install python${PYTHON_VERSION} -y \
    && dnf install python${PYTHON_VERSION}-pip -y

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/venv/bin:$PATH"
ENV AWS_JAVA_V1_DISABLE_DEPRECATION_ANNOUNCEMENT=true

COPY --from=builder /venv /venv

# Copy the app source code from current directory (where Dockerfile is) into the container.
COPY --exclude=*.env . /df-data-lineage
COPY --from=df-config ./cfg /packages/df-config/cfg

# Expose the port that the application listens on. i.e. container port
# This is just for documentation. Port should be exposed when the container is instantiated or via docker publish port.
ARG CONTAINER_PORT
EXPOSE ${CONTAINER_PORT}

# Set work directory for the app
WORKDIR /df-data-lineage

# Create a non-privileged user that the app will run under.
RUN useradd --create-home --shell /bin/bash app-user

# Switch to the non-privileged user to run the application.
USER app-user

# Run the application.
CMD ["/bin/bash"]
# CMD ["dl-app-api"]
# CMD ["dl-app-api", "--debug"]
# CMD ["dl-app-api", "--debug", "y"]
