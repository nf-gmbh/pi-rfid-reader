from aiohttp import web
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import aiohttp_cors
import logging
import time
import asyncio
import argparse


class RFIDReader:
    """
    A class to handle RFID reading and HTTP response generation for an aiohttp web server.
    """

    def __init__(self, reader):
        """
        Initialize the RFIDReader with a given RFID reader device.
        """
        self.reader = reader

    async def read_no_block_timeout(self):
        """
        Continuously read the RFID until an ID is found or the timeout is reached.
        """
        ts_end = time.monotonic() + args.timeout
        id = self.reader.read_id_no_block()
        while not id and ts_end > time.monotonic():
            await asyncio.sleep(0.001)
            id, text = self.reader.read_no_block()
        return id, text

    async def scan_handler(self, _):
        """
        Handle incoming scan requests, read RFID, and return JSON response.
        """
        try:
            maybe_id, maybe_text = await self.read_no_block_timeout()
            if maybe_id is not None:
                data = {
                    "id": maybe_id,
                    "text": maybe_text.replace("\u0000", "") if maybe_text else "",
                }
                logging.info(f"Scanned ID: {maybe_id}")
                return web.json_response(data)
            else:
                logging.warning("No ID found before timeout")
                return web.HTTPRequestTimeout()
        except Exception as ex:
            log_exception(ex)
            return web.HTTPBadRequest(reason=str(ex))


def setup_logging(log_path):
    """
    Configure the logging with detailed format including timestamps, level, and message.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def log_exception(ex):
    """
    Log an exception to the configured log file.
    """
    logging.error(f"Error during operation: {str(ex)}", exc_info=True)


def parse_args():
    """
    Parse command line arguments for the log file location and server port.
    """
    parser = argparse.ArgumentParser(description="RFID Reader Server Configuration")
    parser.add_argument("--log", required=True, help="Location of the log file")
    parser.add_argument(
        "--port", type=int, required=True, help="Port on which the app runs"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        required=False,
        help="Timeout of scan process. Default is 5",
        default=5,
    )
    return parser.parse_args()


async def on_shutdown(app):
    """
    Cleanup GPIO pins when the application is shutting down.
    """
    try:
        logging.info("Starting cleanup of GPIO.")
        GPIO.cleanup()
        logging.info("GPIO cleanup completed successfully.")
    except Exception as e:
        logging.error(f"Failed during GPIO cleanup: {str(e)}")



def create_app(reader):
    """
    Create and configure the aiohttp web application.
    """
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    rfid_reader = RFIDReader(reader)
    cors = aiohttp_cors.setup(app)
    resource = cors.add(app.router.add_resource("/scan"))
    cors.add(
        resource.add_route("GET", rfid_reader.scan_handler),
        {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers=("X-Custom-Server-Header",),
                allow_headers=("X-Requested-With", "Content-Type"),
            )
        },
    )
    return app


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.log)
    logging.info("Startup RFID reader.")
    reader = SimpleMFRC522()
    app = create_app(reader)
    web.run_app(app, port=args.port, access_log=None)
