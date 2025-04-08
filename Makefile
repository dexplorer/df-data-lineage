# Local

APP := dl_app

install-dev: pyproject.toml
	pip install --upgrade pip &&\
	pip install --editable .[all-dev]

lint:
	pylint --disable=R,C src/${APP}/*.py &&\
	pylint --disable=R,C src/${APP}/*/*.py &&\
	pylint --disable=R,C tests/*.py

test:
	python -m pytest -vv --cov=src/${APP} tests

format:
	black src/${APP}/*.py &&\
	black src/${APP}/*/*.py &&\
	black tests/*.py

local-all: install-dev lint format test

# Docker

IMAGE := df-data-lineage
IMAGE_TAG := latest
PYTHON_VERSION := 3.12
HOST_PORT := 9090
CONTAINER_PORT := 9090

# export DOCKER_BUILDKIT := 1

install: pyproject.toml
	pip install --upgrade pip &&\
	pip install .[all]

build-image:
	docker build \
	--build-context workspaces=/home/ec2-user/workspaces \
	--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
	--build-arg CONTAINER_PORT=${CONTAINER_PORT} \
	--no-cache \
	-t ${IMAGE}:${IMAGE_TAG} .

run-container:
	docker run \
	--mount=type=bind,src=/home/ec2-user/workspaces/nas,dst=/nas \
	-p ${HOST_PORT}:${CONTAINER_PORT} \
	-t -i ${IMAGE}:${IMAGE_TAG}

# AWS 
AWS_ECR := public.ecr.aws/d0h7o5k8
AWS_ECR_REPO_NAMESPACE := dexplorer
AWS_ECR_REPO := dexplorer/df-data-lineage

aws-auth-to-ecr:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/d0h7o5k8

aws-build-image:
	docker build \
	--build-context workspaces=/home/ec2-user/workspaces \
	--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
	--build-arg CONTAINER_PORT=${CONTAINER_PORT} \
	--no-cache \
	-t ${AWS_ECR_REPO} .

aws-tag-image:
	# docker tag ${AWS_ECR_REPO}:${IMAGE_TAG} ${AWS_ECR}/${AWS_ECR_REPO}:${IMAGE_TAG}
	docker tag ${IMAGE}:${IMAGE_TAG} ${AWS_ECR}/${AWS_ECR_REPO}:${IMAGE_TAG}

aws-push-image:
	docker push ${AWS_ECR}/${AWS_ECR_REPO}:${IMAGE_TAG}

aws-all: aws-auth-to-ecr aws-build-image aws-tag-image aws-push-image
