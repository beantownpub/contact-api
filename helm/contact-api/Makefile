.PHONY: all test clean

name := $(subst _,-,$(@D))
image := contact-api
# tag := $(shell grep 'appVersion:' $(@D)/Chart.yaml | cut -f 2 -d' ')
port := 5012

SHELL := /bin/bash

ifeq ($(env),dev)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
	slack_orders_webhook_url = ${SLACK_ORDERS_WEBHOOK_URL_DEV}
	slack_partys_webhook_url = ${SLACK_PARTYS_WEBHOOK_URL_DEV}
	email_recipient = ${TEST_EMAIL_RECIPIENT}
	log_level ?= DEBUG
else ifeq ($(env),prod)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
	slack_orders_webhook_url = ${SLACK_ORDERS_WEBHOOK_URL_PROD}
	slack_partys_webhook_url = ${SLACK_PARTYS_WEBHOOK_URL_PROD}
	email_recipient = ${EMAIL_RECIPIENT}
	log_level ?= INFO
endif

helm/clean:
		rm helm/contact-api/*.tgz || true

helm/context:
	kubectl config use-context $(context)

## Publish contact Helm chart
helm/publish:
	cd helm/contact-api && helm package . && \
		cd - && \
		helm repo index . --url https://beantownpub.github.io/helm/ && \
		git add contact-api/

## Deploy contact-api to cluster
helm/install: helm/context
	cd helm/contact-api && \
	helm upgrade --install contact-api . \
		--namespace $(namespace) \
		--set global.env=$(env) \
		--set logLevel=$(log_level) \
		--set aws_access_key_id="${CONTACT_API_AWS_ACCESS_KEY_ID}" \
		--set aws_secret_access_key="${CONTACT_API_AWS_SECRET_ACCESS_KEY}" \
		--set aws_secret_name="${AWS_SECRET_NAME}" \
		--set aws_default_region="${AWS_DEFAULT_REGION}" \
		--set email_recipient="$(email_recipient)" \
		--set second_email_recipient="${SECOND_EMAIL_RECIPIENT}" \
		--set slack_channel="${SLACK_WEBHOOK_CHANNEL}" \
		--set slack_user="${SLACK_USER}" \
		--set slack_webhook_url="${SLACK_WEBHOOK_URL}" \
		--set support_email_address="${SUPPORT_EMAIL_ADDRESS}" \
		--set support_phone_number="${SUPPORT_PHONE_NUMBER}" \
		--set slack_partys_channel="${SLACK_PARTYS_CHANNEL}" \
		--set slack_orders_channel="${SLACK_ORDERS_CHANNEL}" \
		--set slack_orders_webhook_url=$(slack_orders_webhook_url) \
		--set slack_partys_webhook_url=$(slack_partys_webhook_url) \
		--set test_email_recipient="${TEST_EMAIL_RECIPIENT}" \
		--debug
	@echo $(name)

## Create db secret
helm/db_secret: helm/context
	kubectl create secret generic db-creds \
		--namespace "${NAMESPACE}" \
		--from-literal=db_admin_user="${DB_ADMIN_USER}" \
		--from-literal=db_admin_pass="${DB_ADMIN_PASS}" \
		--from-literal=db_user="${DB_USER}" \
		--from-literal=db_pass="${DB_PASS}" \
		--from-literal=contact_db_name="${CONTACT_DB_NAME}" \
		--from-literal=menu_db_name="${MENU_DB_NAME}" \
		--from-literal=merch_db_name="${MERCH_DB_NAME}" \
		--from-literal=users_db_name="${USERS_DB_NAME}"

## Deploy contact-api to cluster
helm/deploy/db: helm/context
	helm upgrade --install contact-api helm/contact-api/ \
		--namespace $(namespace) \
		--set global.env=$(env) \
		--set logLevel=$(log_level) \
		--set aws_access_key_id="${CONTACT_API_AWS_ACCESS_KEY_ID}" \
		--set aws_secret_access_key="${CONTACT_API_AWS_SECRET_ACCESS_KEY}" \
		--set aws_default_region="${AWS_DEFAULT_REGION}" \
		--set email_recipient="$(email_recipient)" \
		--set second_email_recipient="${SECOND_EMAIL_RECIPIENT}" \
		--set slack_channel="${SLACK_WEBHOOK_CHANNEL}" \
		--set slack_user="${SLACK_USER}" \
		--set slack_webhook_url="${SLACK_WEBHOOK_URL}" \
		--set support_email_address="${SUPPORT_EMAIL_ADDRESS}" \
		--set support_phone_number="${SUPPORT_PHONE_NUMBER}" \
		--set slack_partys_channel="${SLACK_PARTYS_CHANNEL}" \
		--set slack_orders_channel="${SLACK_ORDERS_CHANNEL}" \
		--set slack_orders_webhook_url=$(slack_orders_webhook_url) \
		--set slack_partys_webhook_url=$(slack_partys_webhook_url) \
		--set test_email_recipient="${TEST_EMAIL_RECIPIENT}" \
		--set database.enabled=true \
		--set postgres.fullnameOverride=postgres \
		--set postgres.contact_db_name=${CONTACT_DB_NAME} \
		--set postgres.db_admin_pass=${DB_ADMIN_PASS} \
		--set postgres.db_admin_user=${DB_ADMIN_USER} \
		--set postgres.db_pass=${DB_PASS} \
		--set postgres.db_user=${DB_USER} \
		--set postgres.menu_db_name=${MENU_DB_NAME} \
		--set postgres.merch_db_name=${MERCH_DB_NAME} \
		--set postgres.users_db_name=${USERS_DB_NAME} \
		--debug

## Render contact-api templates
helm/template:
	helm template  contact-api helm/contact-api/ \
		--namespace $(namespace) \
		--set global.env=$(env) \
		--set logLevel=$(log_level) \
		--set aws_access_key_id="${AWS_ACCESS_KEY_ID}" \
		--set aws_secret_access_key="${AWS_SECRET_ACCESS_KEY}" \
		--set aws_default_region="${AWS_DEFAULT_REGION}" \
		--set email_recipient="$(email_recipient)" \
		--set second_email_recipient="${SECOND_EMAIL_RECIPIENT}" \
		--set slack_channel="${SLACK_WEBHOOK_CHANNEL}" \
		--set slack_user="${SLACK_USER}" \
		--set slack_webhook_url="${SLACK_WEBHOOK_URL}" \
		--set support_email_address="${SUPPORT_EMAIL_ADDRESS}" \
		--set test_email_recipient="${TEST_EMAIL_RECIPIENT}" \
		--set support_phone_number="${SUPPORT_PHONE_NUMBER}" \
		--set slack_partys_channel="${SLACK_PARTYS_CHANNEL}" \
		--set slack_orders_channel="${SLACK_ORDERS_CHANNEL}" \
		--set slack_orders_webhook_url=$(slack_orders_webhook_url) \
		--set slack_partys_webhook_url=$(slack_partys_webhook_url) \
		--set database.enabled=true \
		--set postgres.contact_db_name=${CONTACT_DB_NAME} \
		--set postgres.db_admin_pass=${DB_ADMIN_PASS} \
		--set postgres.db_admin_user=${DB_ADMIN_USER} \
		--set postgres.db_pass=${DB_PASS} \
		--set postgres.db_user=${DB_USER} \
		--set postgres.menu_db_name=${MENU_DB_NAME} \
		--set postgres.merch_db_name=${MERCH_DB_NAME} \
		--set postgres.users_db_name=${USERS_DB_NAME} \
		--debug

helm/port_forward: helm/context
		kubectl port-forward --namespace $(namespace) svc/contact-api $(port):$(port)
