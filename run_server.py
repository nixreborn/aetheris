#!/usr/bin/env python3
"""
Quick start script to run the Shards of Eternity master server.

Usage:
    python run_server.py [--host HOST] [--port PORT]

Examples:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 9000
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from network import MasterServer


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/server.log")
        ]
    )


async def main():
    """Run the master server."""
    parser = argparse.ArgumentParser(
        description="Shards of Eternity Master Server"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Server host address (default: from settings)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (default: from settings)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)

    # Get settings
    settings = get_settings()

    # Determine host and port
    host = args.host or settings.master_server_host
    port = args.port or settings.master_server_port

    # Create and start server
    logger.info("="*60)
    logger.info("  Shards of Eternity - Master Server")
    logger.info("="*60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"URL: http://{host}:{port}")
    logger.info(f"WebSocket: ws://{host}:{port}/ws")
    logger.info("="*60)

    server = MasterServer(host=host, port=port)

    try:
        await server.start()
        logger.info("Server started successfully")
        logger.info("Press Ctrl+C to stop the server")

        # Keep running
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down server...")
        await server.stop()
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
