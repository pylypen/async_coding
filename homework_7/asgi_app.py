import uvicorn
from typing import Callable, Awaitable, Dict


async def app(scope: Dict, receive: Callable, send: Callable) -> None:
    if scope['type'] == 'http':
        response = b"hello world"
        headers = [(b"content-type", b"text/plain")]
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': headers,
        })
        await send({
            'type': 'http.response.body',
            'body': response,
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
