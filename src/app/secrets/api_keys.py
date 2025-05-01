from secrets import token_urlsafe

async def create_api_key():
    api_key = token_urlsafe(32)
    return api_key

async def delete_api_key():
    pass
