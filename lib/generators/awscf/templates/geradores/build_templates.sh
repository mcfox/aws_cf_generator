#!/usr/bin/env bash
python app-ami-generator.py
python app-stack-generator.py staging
python app-stack-generator.py production
