.PHONY: all test clean

email_recipient ?= ${CONTACT_API_EMAIL_RECIPIENT}
second_recipient ?= ${CONTACT_API_EMAIL_SECOND_RECIPIENT}
tag ?= $(shell yq eval '.info.version' swagger.yaml)
image ?= contact_api
repo ?= ${DOCKER_REPO}

build:
		@echo "\033[1;32m. . . Building Contact API image . . .\033[1;37m\n"
		docker build -t $(image):$(tag) .

publish: build
		docker tag $(image):$(tag) $(repo)/$(image):$(tag)
		docker push $(repo)/$(image):$(tag)

start:
		@echo "\033[1;32m. . . Starting Contact API container . . .\033[1;37m\n"
		docker run \
			--name contact_api \
			--restart always \
			-p "5012:5012" \
			-e DEBUG_CONTACT_API='True' \
			-e SLACK_WEBHOOK_URL=${CONTACT_API_SLACK_WEBHOOK_URL} \
			-e SLACK_WEBHOOK_CHANNEL=${CONTACT_API_SLACK_WEBHOOK_CHANNEL} \
			-e SLACK_WEBHOOK_USER=${CONTACT_API_SLACK_WEBHOOK_USER} \
			-e EMAIL_SENDER=${CONTACT_API_EMAIL_SENDER} \
			-e EMAIL_RECIPIENT=$(email_recipient) \
			-e AWS_ACCESS_KEY_ID=${AWS_KEY_ID} \
			-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
			-e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
			$(image):$(tag)

stop:
		docker rm -f contact_api || true
clean:
		rm -rf api/__pycache__ || true
		rm .DS_Store || true
		rm api/*.pyc