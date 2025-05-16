Secret manager: https://infisical.com/docs/documentation/guides/python

Set up machine identity: https://infisical.com/docs/documentation/platform/identities/universal-auth

Handle .env files: https://www.dotenv.org/

# Local Postegresql 

Installation
```bash
sudo apt update
sudo apt install postgresql
sudo apt install postgresql-client
```
Check version
```bash
psql --version
```
Connect to psql console with super user
```bash
sudo -u postgres psql
```
Create role
```bash
CREATE ROLE username LOGIN CREATEDB;
```
Change password
```
ALTER USER username PASSWORD "password";
```
Create db
```bash
create mydb
```
Drop db
```bash
dropdb mydb
```
Create Users Table
```
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    picture_url TEXT
);
```

# Fastapi

Start Fastapi server
```
uv run fastapi dev  ../backend/src/app/main.py
```