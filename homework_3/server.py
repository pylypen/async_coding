import asyncio
import random


async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    print(f"Client {address} connected")

    while True:
        temperature = random.uniform(-30, 40)  # Temperature in Celsius
        humidity = random.uniform(0, 100)  # Humidity in percentage
        pressure = random.uniform(950, 1050)  # Pressure in hPa

        weather_data = f"Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %, Pressure: {pressure:.2f} hPa\n"
        writer.write(weather_data.encode())
        try:
            await writer.drain()
        except ConnectionResetError:
            break

        await asyncio.sleep(5)  # Send data every 5 seconds

    writer.close()
    print(f"Client {address} disconnected")


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    address = server.sockets[0].getsockname()
    print(f"Serving on {address}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
