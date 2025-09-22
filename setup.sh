#!/bin/bash

apt-get -y build-essential
apt-get -y install python3 python3-pip python3-venv
apt-get -y install iverilog

pip install virtualenv

virtualenv /autograder/venv/
/autograder/venv/bin/pip install cocotb
