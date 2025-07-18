#!/usr/bin/env python3

"""
Single-assignment async fan-out.

Usage:
  cat data.jsonl | python client.py endpoints.txt
"""
import asyncio, json, sys, aiohttp
from typing import List


async def stdin_reader() -> asyncio.Queue:
    """Non-blocking JSONL feed into an asyncio.Queue."""
    q: asyncio.Queue = asyncio.Queue()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin.buffer)

    async def _feed():
        async for line in reader:
            if not line:
                break
            try:
                await q.put(json.loads(line))
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"stdin: {e}"}), file=sys.stderr, flush=True)
        await q.put(None)  # EOF sentinel

    asyncio.create_task(_feed())
    return q


async def worker(
    session: aiohttp.ClientSession,
    url: str,
    inbox: asyncio.Queue,
    outbox: asyncio.Queue,
):
    """Pull one record at a time from inbox, POST, push result to outbox."""
    while True:
        record = await inbox.get()
        if record is None:  # graceful shutdown
            break
        try:
            async with session.post(url, json=record) as resp:
                result = await resp.json()
                await outbox.put(result)
        except Exception as e:
            await outbox.put({"error": str(e), "url": url})


async def printer(outbox: asyncio.Queue):
    """Print every result the instant it arrives."""
    while True:
        item = await outbox.get()
        if item is None:  # graceful shutdown
            break
        print(json.dumps(item), flush=True)


async def main():
    if len(sys.argv) != 2:
        print("usage: cat data.jsonl | python client.py endpoints.txt", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        endpoints: List[str] = [line.strip() for line in f if line.strip()]
    if not endpoints:
        print("no endpoints", file=sys.stderr)
        sys.exit(1)

    timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:

        inbox = asyncio.Queue()  # work queue
        outbox = asyncio.Queue()  # results queue

        # 1. Launch one worker per endpoint
        workers = [
            asyncio.create_task(worker(session, url, inbox, outbox))
            for url in endpoints
        ]

        # 2. Launch printer coroutine
        printer_task = asyncio.create_task(printer(outbox))

        # 3. Feed STDIN into the work queue
        stdin_q = await stdin_reader()
        while True:
            record = await stdin_q.get()
            if record is None:  # EOF
                break
            await inbox.put(record)  # non-blocking hand-off

        # 4. Shut down cleanly
        for _ in endpoints:
            await inbox.put(None)  # tell every worker to quit
        await asyncio.gather(*workers)
        await outbox.put(None)  # tell printer to quit
        await printer_task


if __name__ == "__main__":
    asyncio.run(main())
