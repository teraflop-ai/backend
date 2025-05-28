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
```sql
CREATE ROLE username LOGIN CREATEDB;
```
Change password
```sql
ALTER USER username PASSWORD "password";
```
Create db
```sql
create mydb
```
Drop db
```sql
dropdb mydb
```
Create Users Table

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_logged_in_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
Create User API keys Table
```sql
CREATE TABLE IF NOT EXISTS user_api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255),
    hashed_key VARCHAR(255) UNIQUE NOT NULL,
    lookup_hash CHAR(64) NOT NULL UNIQUE,
    key_prefix VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_api_keys_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE 
);
```
Create User Balance Table
```sql
CREATE TABLE IF NOT EXISTS user_balance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    balance DECIMAL(19, 8) NOT NULL DEFAULT 0.00000000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_balance_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE  
);
```

Add multiple columns to table
```sql
ALTER TABLE user_transactions 
ADD COLUMN status VARCHAR(64),
ADD COLUMN invoice_number TEXT UNIQUE,
ADD COLUMN invoice_url TEXT; 
```

Create User Transactions Table
```sql
CREATE TABLE IF NOT EXISTS user_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount DECIMAL(19, 8) NOT NULL,
    status VARCHAR(64) NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    invoice_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
```
Create User Token Usage Table
```sql
CREATE TABLE IF NOT EXISTS user_token_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    token_count INT DEFAULT 0 CHECK (token_count >= 0),
    request_count INT DEFAULT 0 CHECK (request_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_token_usage_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_date 
        UNIQUE (user_id, usage_date)
);
```
Create User Subscriptions Table
```sql
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTERGER UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_type VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
);
```
Create Models Table
```sql
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
);
```
Create Table Indexes
```sql
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_logged_in_at);
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_token_usage_date ON user_token_usage(usage_date);
CREATE INDEX idx_user_token_usage_user_date ON user_token_usage(user_id, usage_date);
```
List tables
```sql
\dt
```
Rename table column
```sql
ALTER TABLE table_name RENAME COLUMN column_name to new_name;
```
Add table column
```sql
ALTER TABLE table_name ADD column_name varchar(255);
```
Drop table column
```sql
ALTER TABLE table_name DROP COLUMN column_name;
```
Change column type
```sql
ALTER TABLE table_name ALTER COLUMN column_name TYPE varchar(255);
```

# Fastapi

Start Fastapi server
```
uv run fastapi dev  ../backend/src/app/main.py
```

# Development dependencies

```
minio
batched
truss
sentence-transformers
pytest-playwright
```