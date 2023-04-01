#!/usr/bin/env bash

set -e

dnf -y install git vim make pip python3-opencv
pip install pipenv

echo ". /usr/share/git-core/contrib/completion/git-prompt.sh" >> ~/.bashrc
echo "export PS1='[\[\e[01;34m\]\W\[\e[01;35m\]\$(__git_ps1 \" %s\")\[\e[00m\]]$\[\e[00m\] '" >> ~/.bashrc
