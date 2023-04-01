#!/usr/bin/env bash

podman create -v ./:/app --name=watchbot-container watchbot-image
