from supabase import create_client, Client

from app.secrets.infisical import (SUPABASE_URL, SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL.secretValue, SUPABASE_KEY.secretValue)