#!/usr/bin/bash
coverage run --source server -m unittest discover ./server/test && coverage html && coverage report
