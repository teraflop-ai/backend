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

Create Organizations Table
```sql
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP 
);
```

Create Projects Table
```sql
CREATE TABLE IF NOT EXISTS projects(
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_projects_org
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE,
        
    CONSTRAINT unique_organization_project_name
        UNIQUE (organization_id, name)
);
```

Create Users Table
```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    last_selected_organization_id INTEGER,
    last_selected_project_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_logged_in_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_last_selected_organization
        FOREIGN KEY(last_selected_organization_id)
        REFERENCES organizations(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_last_selected_project
        FOREIGN KEY(last_selected_project_id)
        REFERENCES projects(id)
        ON DELETE SET NULL
);
```

Create Organization Members Table
```sql
CREATE TABLE IF NOT EXISTS organization_members (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_members_organization
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_members_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_organization_user
        UNIQUE (organization_id, user_id),

    CONSTRAINT check_role CHECK (role IN ('admin', 'member'))
);
```
Create API keys Table
```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    project_id INTEGER,
    name VARCHAR(255),
    hashed_key VARCHAR(255) UNIQUE NOT NULL,
    lookup_hash CHAR(64) NOT NULL UNIQUE,
    key_prefix VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_api_keys_organization
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_api_keys_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_api_keys_project
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE 
);
```
Create Organization Balance Table
```sql
CREATE TABLE IF NOT EXISTS organization_balance (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER UNIQUE NOT NULL,
    balance DECIMAL(19, 8) NOT NULL DEFAULT 0.00000000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_balance_organization
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE  
);
```

Create Organization Transactions Table
```sql
CREATE TABLE IF NOT EXISTS organization_transactions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    amount DECIMAL(19, 8) NOT NULL,
    status VARCHAR(64) NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    invoice_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transactions_organization
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE
);
```
Create Organization Token Usage Table
```sql
CREATE TABLE IF NOT EXISTS organization_token_usage (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    token_count INT DEFAULT 0 CHECK (token_count >= 0),
    request_count INT DEFAULT 0 CHECK (request_count >= 0),
    total_spend DECIMAL(19, 8) DEFAULT 0.00000000 CHECK (total_spend >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_token_usage_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_token_usage_organization
        FOREIGN KEY(organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_date 
        UNIQUE (user_id, organization_id, usage_date)
);
```

Create Projects Members Table
```sql
CREATE TABLE IF NOT EXISTS project_members(
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_project_members
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,
        
    CONSTRAINT fk_project_members_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
        
    CONSTRAINT unique_project_user
        UNIQUE (project_id, user_id),

    CONSTRAINT check_role CHECK (role IN ('admin', 'member'))
);
```
Create Projects Token Usage
```sql
CREATE TABLE IF NOT EXISTS project_token_usage (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    token_count INT DEFAULT 0 CHECK (token_count >= 0),
    request_count INT DEFAULT 0 CHECK (request_count >= 0),
    total_spend DECIMAL(19, 8) DEFAULT 0.00000000 CHECK (total_spend >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_project_token_usage
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_project_token_usage_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_project_date 
        UNIQUE (project_id, user_id, usage_date)
);
```
Project Balance
```sql
CREATE TABLE IF NOT EXISTS project_balance (
    id SERIAL PRIMARY KEY,
    project_id INTEGER UNIQUE NOT NULL,
    balance DECIMAL(19, 8) NOT NULL DEFAULT 0.00000000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_balance_project
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE  
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
Add multiple columns to table
```sql
ALTER TABLE user_transactions 
ADD COLUMN status VARCHAR(64),
ADD COLUMN invoice_number TEXT UNIQUE,
ADD COLUMN invoice_url TEXT; 
```
Drop table column
```sql
ALTER TABLE table_name DROP COLUMN column_name;
```
Change column type
```sql
ALTER TABLE table_name ALTER COLUMN column_name TYPE varchar(255);
```
Add foreign key constraint
```sql
ALTER TABLE table_name 
ADD CONSTRAINT fk_constraint
FOREIGN KEY (table_column)
REFERENCES table_name(table_column)
ON DELETE CASCADE;
``
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