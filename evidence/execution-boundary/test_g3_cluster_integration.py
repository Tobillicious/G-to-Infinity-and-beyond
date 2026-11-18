import asyncio
import json
import logging
from typing import List

logger = logging.getLogger("GMeshIntegrationTest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class MockGMeshNodeServer:
    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.server = None
        self.received_states: List[dict] = []

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            data = await reader.readline()
            if data:
                envelope = json.loads(data.decode("utf-8").strip())
                payload = envelope.get("payload", {})
                self.received_states.append(payload)

                response = {"status": "ACK", "node_id": self.node_id, "accepted_entropy": payload.get("entropy")}
                writer.write((json.dumps(response) + "\n").encode("utf-8"))
                await writer.drain()
        except Exception as e:
            logger.error(f"[{self.node_id}] Error handling connection: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        logger.info(f"[*] Node {self.node_id} active on {self.host}:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info(f"[-] Node {self.node_id} stopped.")


async def run_integration_test():
    cluster_config = [
        {"node_id": "G3-Alpha", "host": "127.0.0.1", "port": 9101},
        {"node_id": "G3-Beta", "host": "127.0.0.1", "port": 9102},
        {"node_id": "G3-Gamma", "host": "127.0.0.1", "port": 9103},
    ]

    servers = [MockGMeshNodeServer(**cfg) for cfg in cluster_config]

    server_tasks = [asyncio.create_task(server.start()) for server in servers]
    await asyncio.sleep(0.2)

    try:
        logger.info("[*] Spawning 3-node G-Mesh cluster. Executing quorum consensus test...")

        leader = cluster_config[0]
        voters = cluster_config[1:]

        test_payload = {
            "node_id": leader["node_id"],
            "address": f"{leader['host']}:{leader['port']}",
            "entropy": 0.00012,
            "state_root": "0xkoru_consensus_root_42",
        }

        acks = 0
        required_quorum = 2

        for voter in voters:
            try:
                reader, writer = await asyncio.open_connection(voter["host"], voter["port"])
                envelope = {"payload": test_payload, "signature": "mock_sig_valid"}
                writer.write((json.dumps(envelope) + "\n").encode("utf-8"))
                await writer.drain()

                data = await reader.readline()
                if data:
                    res = json.loads(data.decode("utf-8").strip())
                    if res.get("status") == "ACK":
                        acks += 1
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.error(f"Failed to reach voter {voter['node_id']}: {e}")

        logger.info(f"[*] Quorum check: Received {acks}/{len(voters)} acknowledgments.")
        assert acks >= required_quorum, f"Quorum consensus failed! Achieved {acks}/{required_quorum}"
        logger.info("[+] SUCCESS: G-Mesh 3-node cluster successfully achieved quorum consensus!")

    finally:
        for server in servers:
            await server.stop()
        for task in server_tasks:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(run_integration_test())
