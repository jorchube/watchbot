#!/usr/bin/env bash

podman build -f ./container/Containerfile --tag watchbot-image .
