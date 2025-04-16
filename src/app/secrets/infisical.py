import os
from dotenv_vault import load_dotenv
from infisical_sdk import InfisicalSDKClient

load_dotenv()

client = InfisicalSDKClient(host="https://app.infisical.com")

INFISICAL_PROJECT_ID = os.getenv("INFISICAL_PROJECT_ID")

client.auth.universal_auth.login(
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET"),
)

GOOGLE_CLIENT_ID = client.secrets.get_secret_by_name(
    secret_name="GOOGLE_CLIENT_ID",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

GOOGLE_CLIENT_SECRET = client.secrets.get_secret_by_name(
    secret_name="GOOGLE_CLIENT_SECRET",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

SESSION_SECRET_KEY = client.secrets.get_secret_by_name(
    secret_name="SESSION_SECRET_KEY",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

STRIPE_SECRET_KEY = client.secrets.get_secret_by_name(
    secret_name="STRIPE_SECRET_KEY",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

STRIPE_PUBLISHABLE_KEY = client.secrets.get_secret_by_name(
    secret_name="STRIPE_PUBLISHABLE_KEY",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

SUPABASE_URL = client.secrets.get_secret_by_name(
    secret_name="SUPABASE_URL",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)

SUPABASE_KEY = client.secrets.get_secret_by_name(
    secret_name="SUPABASE_KEY",
    project_id=INFISICAL_PROJECT_ID,
    environment_slug="dev",
    secret_path="/",
)