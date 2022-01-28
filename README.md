# FIS
This repository contains the implementation of the Dutch Forensics system for the Secure Software Development course by University of Essex.

# Instruction to run
* Install the required dependencies (it is suggested to setup a virtual env):

``pip install -r /path/to/requirements.txt``

* Run as a process:

    ``flask run -h localhost -p 5005 src/auth/Authenticate``
  
  this is going to start the authentication service


* Run as a separate process:
  
    ``flask run src/web/application``
