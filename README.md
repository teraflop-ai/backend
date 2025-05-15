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
Connect with super user
```bash
sudo -u postgres psql
```
Create role
```bash
CREATE ROLE myname LOGIN CREATEDB;
```
Create db
```bash
create mydb
```
Drop db
```bash
dropdb mydb
```