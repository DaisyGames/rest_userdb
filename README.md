# rest_userdb
Mock-up of API for maintaining users, user groups and their relation within in-memory database.

## Prerequisites
- Ubuntu or WSL
- Docker
- Docker compose 

If you do not have these installed, please refer to the following guides:
- [Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview)
- [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/install/)

## Installation
Step 1) Download or clone this project


Step 2) Open your terminal in the project directory


Step 3) Build the Docker image with the following command
```bash
docker build -t rest-userdb .
```


Step 4) **Optional:** confirm the build has been successful with the following command)
```bash
docker images
```
You should now see a repository called rest-userdb


Step 5) Start the service with the following command
```bash
docker compose up
```


Step 6) Congratulations, you are done! The service is now hosted on your localhost.


## API Documentation
Once you completed the installation, please refer to the http://localhost:8000/docs for the documentation.
You can access this from the local device where you started the service.
