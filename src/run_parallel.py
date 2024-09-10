import sys
import asyncio
import time
from collections import deque


async def execute_command(host, command):
    try:
        start_time = time.perf_counter()
        process = await asyncio.create_subprocess_exec(
            "ssh",
            host,
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        end_time = time.perf_counter()

        print(f"Host: {host}, Command: {command}")
        if process.returncode == 0:
            print(f"Output: {stdout.decode().strip()}")
        else:
            print(f"Error: {stderr.decode().strip()}")

        print(f"Execution time: {end_time - start_time:.4f} seconds")
        print("---")
    except asyncio.TimeoutError:
        print(f"Host: {host}, Command: {command}")
        print("Error: Command execution timed out")
        print("---")
    except Exception as e:
        print(f"Host: {host}, Command: {command}")
        print(f"Error: {str(e)}")
        print("---")


async def process_commands(hosts, commands):
    host_queue = deque(hosts)
    command_queue = deque(commands)
    tasks = []

    # Start initial tasks for each host
    for _ in range(min(len(hosts), len(commands))):
        host = host_queue[0]
        command = command_queue.popleft()
        task = asyncio.create_task(execute_command(host, command))
        tasks.append(task)
        host_queue.rotate(-1)

    # Process remaining commands
    while tasks:
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for _ in done:
            if command_queue:
                host = host_queue[0]
                command = command_queue.popleft()
                task = asyncio.create_task(execute_command(host, command))
                tasks.add(task)
                host_queue.rotate(-1)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py host1 host2 ...", file=sys.stderr)
        sys.exit(1)

    hosts = sys.argv[1:]
    commands = [line.strip() for line in sys.stdin if line.strip()]

    await process_commands(hosts, commands)


if __name__ == "__main__":
    asyncio.run(main())
