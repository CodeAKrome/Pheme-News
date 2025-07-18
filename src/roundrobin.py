#!/usr/bin/env python3

import asyncio
import asyncssh
import sys
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Server:
    host: str
    username: str
    port: int = 22
    key_file: Optional[str] = None
    password: Optional[str] = None


class SSHRoundRobin:
    def __init__(self, servers: List[Server]):
        self.servers = servers
        self.server_queue = deque(servers)
        self.connections: Dict[str, asyncssh.SSHClientConnection] = {}
        self.busy_servers = set()

    async def connect_to_servers(self):
        """Establish SSH connections to all servers"""
        tasks = []
        for server in self.servers:
            tasks.append(self._connect_server(server))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for connection failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to connect to {self.servers[i].host}: {result}")
            else:
                logger.info(f"Connected to {self.servers[i].host}")

    async def _connect_server(self, server: Server):
        """Connect to a single server"""
        try:
            connect_kwargs = {
                "host": server.host,
                "port": server.port,
                "username": server.username,
                "known_hosts": None,  # Disable host key checking for demo
            }

            if server.key_file:
                connect_kwargs["client_keys"] = [server.key_file]
            elif server.password:
                connect_kwargs["password"] = server.password

            conn = await asyncssh.connect(**connect_kwargs)
            self.connections[server.host] = conn
            return conn

        except Exception as e:
            logger.error(f"Failed to connect to {server.host}: {e}")
            raise

    async def get_next_available_server(self) -> Optional[Server]:
        """Get the next available server in round-robin fashion"""
        # Wait until at least one server is available
        while len(self.busy_servers) >= len(self.connections):
            await asyncio.sleep(0.1)

        # Find next available server
        attempts = 0
        while attempts < len(self.server_queue):
            server = self.server_queue[0]
            self.server_queue.rotate(-1)  # Move to end

            if server.host in self.connections and server.host not in self.busy_servers:
                return server

            attempts += 1

        return None

    async def execute_command(self, command: str) -> tuple[str, str, str]:
        """Execute command on next available server"""
        server = await self.get_next_available_server()
        if not server:
            return "", "No available servers", server.host if server else "unknown"

        # Mark server as busy
        self.busy_servers.add(server.host)

        try:
            conn = self.connections[server.host]
            logger.info(f"Executing on {server.host}: {command.strip()}")

            result = await conn.run(command)

            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""

            if result.exit_status == 0:
                logger.info(f"Command completed on {server.host}")
            else:
                logger.warning(
                    f"Command failed on {server.host} with exit code {result.exit_status}"
                )

            return stdout, stderr, server.host

        except Exception as e:
            logger.error(f"Error executing command on {server.host}: {e}")
            return "", str(e), server.host

        finally:
            # Mark server as available
            self.busy_servers.discard(server.host)

    async def close_connections(self):
        """Close all SSH connections"""
        for host, conn in self.connections.items():
            try:
                conn.close()
                await conn.wait_closed()
                logger.info(f"Closed connection to {host}")
            except Exception as e:
                logger.error(f"Error closing connection to {host}: {e}")


async def read_stdin_commands():
    """Read commands from stdin asynchronously"""
    loop = asyncio.get_event_loop()

    def read_line():
        return sys.stdin.readline()

    while True:
        try:
            # Read line from stdin in a non-blocking way
            line = await loop.run_in_executor(None, read_line)
            if not line:  # EOF
                break

            command = line.strip()
            if command:
                yield command

        except KeyboardInterrupt:
            break


async def main():
    # Configure your servers here
    servers = [
        Server(host="server1.example.com", username="user"),
        Server(host="server2.example.com", username="user"),
        Server(host="server3.example.com", username="user"),
        # Add more servers as needed
        # Server(host="server4.example.com", username="user", key_file="/path/to/key"),
        # Server(host="server5.example.com", username="user", password="password123"),
    ]

    if not servers:
        logger.error("No servers configured. Please add servers to the list.")
        return

    ssh_manager = SSHRoundRobin(servers)

    try:
        # Connect to all servers
        logger.info("Connecting to servers...")
        await ssh_manager.connect_to_servers()

        if not ssh_manager.connections:
            logger.error("No successful connections established")
            return

        logger.info(f"Successfully connected to {len(ssh_manager.connections)} servers")
        logger.info("Ready to execute commands. Type commands or press Ctrl+C to exit.")

        # Process commands from stdin
        async for command in read_stdin_commands():
            if command.lower() in ["exit", "quit"]:
                break

            # Execute command asynchronously
            stdout, stderr, host = await ssh_manager.execute_command(command)

            # Print results
            print(f"=== Results from {host} ===")
            if stdout:
                print("STDOUT:")
                print(stdout)
            if stderr:
                print("STDERR:")
                print(stderr)
            print("=" * (len(f"=== Results from {host} ===")) + "\n")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    finally:
        logger.info("Closing connections...")
        await ssh_manager.close_connections()


if __name__ == "__main__":
    # Install required package: pip install asyncssh
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
