import asyncio
import aiohttp
import os
from argparse import ArgumentParser
from aiohttp import ClientError


async def fetch(session: aiohttp.ClientSession, url: str, timeout: aiohttp.ClientTimeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            print(f"Request to {url}")
            content = await response.read()
            return content
    except asyncio.TimeoutError:
        print(f"Timeout error on {url}")
        return None
    except ClientError as e:
        print(f"Client error on {url}: {e}")
        return None


async def download_all(urls: list, timeout: aiohttp.ClientTimeout, output_dir: str):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url, timeout))

        responses = await asyncio.gather(*tasks)

        for i, content in enumerate(responses):
            if content:
                file_name = os.path.join(output_dir, f"response_{i}.html")
                with open(file_name, 'wb') as f:
                    f.write(content)
                    print(f"Saved response from {urls[i]} to {file_name}")


def parse_args():
    parser = ArgumentParser(description="Download content from URLs and save to files.")
    parser.add_argument("input_file", help="File containing URLs, one per line.")
    parser.add_argument("output_dir", help="Directory to save the downloaded files.")
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    with open(args.input_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    timeout = aiohttp.ClientTimeout(total=1)

    asyncio.run(download_all(urls, timeout, args.output_dir))


if __name__ == "__main__":
    main()
