
# Farmer App

The application will allow the users to fetch the data in their desired language after they are authenticated.

- Fronted code link: https://github.com/Mohiiit/farmer_app_frontend
- API documentation can be found at http://localhost:8000/docs#/ after starting the app.

## Assumptions Made

- There would be no commas in the farmer data.
- If X add data of Y using csv upload method then password for Y would be their phone number.




## Run Locally

### Clone the project

```bash
  git clone https://github.com/Mohiiit/wadhwani_farmer_app.git
```

### Go to the project directory

```bash
  cd wadhwani_farmer_app
```

### Make a virutal environment

```bash
  python -m venv env
```

### Activate the virtual environment

In mac or ubuntu using: 

```bash
  source ./env/bin/activate
```

In windows Git Bash: 

```bash
  source ./env/Scripts/activate
```

In windows PowerShell: 

```bash
  .\env\Scripts\Activate.ps1
```

### Make sure virtual environment is active 

In mac or ubuntu using: 

```bash
  source ./env/bin/activate
```

In windows(PowerShell): 

```bash
  Get-Command python
```

It should return something like:
```bash
/path/to/project/wadhwani_farmer_app/env/bin/python
```

### Install Project Requirements

Install project requirements using command: 
```bash
  pip install -r requirements.txt
```


### Environment Variables

To run this project, following environment variables needs to be added in .env file:

`SECERT_KEY = "YOUR_FAST_API_SECRET_KEY"`

`ALGORITHM ="YOUR_ALGORITHM"`

`ACCESS_TOKEN_EXPIRES_MINUTES = "TIME_IN_SECONDS"`

You can copy it from `env_structure.txt`


### Token for Google translate Api

In order to access the google api, file named `token.json` with valid token needs to be added in the project directory.

### Launch App

Run the command to start project locally: 

```bash
  uvicorn app.main:app --reload
```

### Api Docs

Go to localhost for the api documentation:
```bash
  http://localhost:8000/docs#/
```

## Running Tests

### Before running tests

Add a file named `test.csv` in project directory.

### Run tests

Run tests using command:
```bash
  pytest
```

