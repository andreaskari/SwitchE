# SwitchE

## Decription

Library and software for smart sensor that monitors a connected devices power consumption and controls whether it is one or off.
Created as final project for Civil Engineering 186 at UC Berkeley.

## Installation

### Login with Shell

Log into shell

```shell
$ ssh -i ~/Developer/CE186/switche/SwitchE.pem ubuntu@ec2-52-15-86-194.us-east-2.compute.amazonaws.com
```

Setup mongo db:

https://www.howtoforge.com/tutorial/install-mongodb-on-ubuntu-16.04/

Install all packages locally or create a virtualenv for development via pip.

```shell
$ cd switche/mongo-api/
$ pip3 install -r requirements.txt
```

Append the following to .bash_profile or .bash_rc file

```shell
export PATH=~/Downloads/mongodb/bin/:$PATH
```

Startup

```shell
$ cd switche/
$ mongod &
$ python3 mongo-api/api.py &
```
