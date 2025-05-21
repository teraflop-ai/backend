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
Create User API keys Table
```bash
CREATE TABLE IF NOT EXISTS user_api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255),
    hashed_key VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE 
);
```
Create User Balance Table
```bash
CREATE TABLE IF NOT EXISTS user_balance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    balance DECIMAL(19, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE  
);
```
Creat Models Table
```bash
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
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