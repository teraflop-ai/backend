import modal
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

image = modal.Image.debian_slim().pip_install("fastapi[standard]", "boto3")
app = modal.App(image=image)


class Item(BaseModel):
    name: str
    qty: int = 42


@app.function()
@modal.fastapi_endpoint(method="POST")
def f(item: Item):
    # do things with boto3...
    return HTMLResponse(f"<html>Hello, {item.name}!</html>")
