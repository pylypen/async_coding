import asyncio
import random


async def read_weather_data(reader):
    shutdown_count = random.uniform(5, 25)
    count = 0
    while True:
        count += 1
        data = await reader.read(100)
        if not data:
            break
        if shutdown_count <= count:
            break
        print(f"Received: {data.decode()}")


async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        await read_weather_data(reader)
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
