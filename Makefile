.PHONY: all test clean

tag ?= latest

build:
		@echo "\033[1;32m. . . Building Contact API image . . .\033[1;37m\n"
		docker build -t contact_api .

build_no_cache:
		@echo "\033[1;32m. . . No cache Contact API image build . . .\033[1;37m\n"
		docker build -t contact_api . --no-cache=true

publish: build
		docker tag contact_api jalgraves/contact_api:$(tag)
		docker push jalgraves/contact_api:$(tag)

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
			-e EMAIL_RECIPIENT=${CONTACT_API_EMAIL_RECIPIENT} \
			-e CONTACT_GMAIL_PASSWORD=${CONTACT_API_GMAIL_PASSWORD} \
			-e AWS_ACCESS_KEY_ID=${AWS_KEY_ID} \
			-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
			-e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
			contact_api

stop:
		docker rm -f contact_api || true
clean:
		rm -rf api/__pycache__ || true
		rm .DS_Store || true
		rm api/*.pyc