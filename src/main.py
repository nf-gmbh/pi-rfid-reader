from aiohttp import web
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import aiohttp_cors
import logging
import argparse
from pi_rfid_reader import PiRFIDReader


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



def create_app():
    """
    Create and configure the aiohttp web application.
    """
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    rfid_reader = PiRFIDReader(args.timeout)
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
    app = create_app()
    web.run_app(app, port=args.port, access_log=None)
