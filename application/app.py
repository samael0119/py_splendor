from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware
from uvicorn import run

from router.v1.websocket_router import socket_router

app = FastAPI()
base_url = '/api/v1'
# app.add_middleware(SessionMiddleware, secret_key='py-splendor')
# app.add_middleware(AuthenticationMiddleware, backend=AuthenticationBackend)

# APIRouter has 403 bug, adhoc use mount: https://github.com/tiangolo/fastapi/issues/98
app.mount(f"{base_url}/ws", socket_router)


@app.get("/test")
async def test():
    return "success"


if __name__ == '__main__':
    run("app:app", host='0.0.0.0', port=9999, reload=True, workers=4)
