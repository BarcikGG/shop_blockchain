#!/bin/bash

cd contract

sudo docker build -t shop .
sudo docker image tag shop localhost:5000/shop
sudo docker push localhost:5000/shop
sudo docker image ls|grep 'localhost:5000/shop'