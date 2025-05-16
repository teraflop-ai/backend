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
```bash
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    picture_url TEXT
);
```
List tables
```bash
\dt
```
Rename table column
```
ALTER TABLE table_name RENAME COLUMN name to new_name;
```
Drop table column
```
ALTER TABLE table_name DROP COLUMN name;
```

# Fastapi

Start Fastapi server
```
uv run fastapi dev  ../backend/src/app/main.py
```