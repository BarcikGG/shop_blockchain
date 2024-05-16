#!/bin/bash

cd contract

sudo docker build -t mail .
sudo docker image tag mail localhost:5000/mail
sudo docker push localhost:5000/mail
sudo docker image ls|grep 'localhost:5000/mail'