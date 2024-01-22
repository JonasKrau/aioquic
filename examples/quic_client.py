import asyncio
import argparse
import os
import ssl
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, ConnectionTerminated
from aioquic.quic.logger import QuicFileLogger
from aioquic.h3.connection import H3_ALPN

# Custom QUIC client class extending the QuicConnectionProtocol
class CustomQuicClient(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Handle events received from the QUIC connection
    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            print("Handshake completed, sending data")
            
            # 4. Set a new stream id to 2024, instead of "Issue a new connectionID of 2024"
            stream_id_1 = 2024
            stream_id_2 = 2026

            # 5. Create two new streams and send the payload ”NPA” and "QUIC"
            self._quic.send_stream_data(stream_id_1, b'NPA', end_stream=True)
            print(f"Sent 'NPA' on stream {stream_id_1}")
            self._quic.send_stream_data(stream_id_2, b'QUIC', end_stream=True)
            print(f"Sent 'QUIC' on stream {stream_id_2}")
            
            # 7. Close the connection
            self._quic.close()
            print("Connection closed")
        elif isinstance(event, ConnectionTerminated):
            print("Connection terminated")

# Main coroutine to run the QUIC clien
async def run(host, port, configuration):

    # 1. Establish a QUIC connection to a server
    async with connect(host, port, configuration=configuration, create_protocol=CustomQuicClient):
        await asyncio.Future()

# Entry point for the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom QUIC client")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=4433)
    args = parser.parse_args()

    # Configure the QUIC connection
    configuration = QuicConfiguration(is_client=True)

    # Sets HTTP/3 as the protocol for the QUIC connection.
    configuration.alpn_protocols = H3_ALPN

    # 2. Set the idle_timeout to 5 seconds instead of MAX ACK DELAY to 5 seconds
    configuration.idle_timeout = 5 

    # 3. Set the maximum stream data to 2024 instead of "Set the maximum number of parallel streams to 2024."
    configuration.max_stream_data = 2024

    # Deactivates the certificate check for development purposes.
    configuration.verify_mode = ssl.CERT_NONE  

    

# QLOG-Konfiguration
# 6. Log the connection in QLOG
current_directory = os.getcwd()
qlog_directory = os.path.join(current_directory, "logs")
os.makedirs(qlog_directory, exist_ok=True)
configuration.quic_logger = QuicFileLogger(qlog_directory)

# Execute the run coroutine to start the client
asyncio.run(run(args.host, args.port, configuration))

