# wadhwani_farmer_app

## Installation
Steps to follow to run the code:

1) Clone the repo
2) Make sure to have python on the system, here are commands to install: 
    i) [ubuntu](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu)
    ii) [mac](https://www.scaler.com/topics/python/how-to-install-python-on-macos/)
    ii) [windows](https://www.digitalocean.com/community/tutorials/install-python-windows-10)
3) Go to the parent directory and start a virutal environment, command is: ```$ python -m venv env```
4) Then activate the virtual environment using: 
     i) ubuntu or mac: ```$ source ./env/bin/activate```
     ii) windows:
         a) Git Bash: ```$ source ./env/Scripts/activate```
         b) PowerShell: ```$ .\env\Scripts\Activate.ps1```
5) To make sure that the terminal is picking the right python run:
     i) ubuntu or mac: ```$ which python```
     ii) windows (PowerShell): ```$ Get-Command python```
   It should return something like `/home/user/code/apiapp/env/bin/python`
6) Now install all the requirements listed in `requirements.txt` using command: ```$ pip install -r requirements.txt```
7) To make sure again that we have right python run:
     i) ubuntu or mac: ```$ which uvicorn```
     ii) windows: ```$ Get-Command python```
   It should return the same result as before `/home/user/code/apiapp/env/bin/python`
8) Run the file using command ```$ uvicorn app.main:app --reload```
