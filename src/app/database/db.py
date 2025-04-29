from app.secrets.infisical import (SUPABASE_URL, SUPABASE_KEY)

supabase_url: str = SUPABASE_URL.secretValue
supabase_key: str = SUPABASE_KEY.secretValue

async def create_supabase_client():
    """
    Creates the supabase client
    """
    supabase_client: AsyncClient = await create_client(
        supabase_url, 
        supabase_key,
        options=AsyncClientOptions(
            postgrest_client_timeout=10, 
            storage_client_timeout=10
        )
    )
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
    return supabase_client