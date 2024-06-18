from aiohttp import web
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import logging
import time
import asyncio


class PiRFIDReader:
    """
    A class to handle RFID reading and HTTP response generation for an aiohttp web server.
    """

    def __init__(self, timeout):
        """
        Initialize the RFIDReader with a given RFID reader device.
        """
        self.reader = SimpleMFRC522()
        self.timeout = timeout

    async def _read_no_block_timeout(self):
        """
        Continuously read the RFID until an ID is found or the timeout is reached.
        """
        ts_end = time.monotonic() + self.timeout
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
            maybe_id, maybe_text = await self._read_no_block_timeout()
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
            logging.error(f"Error during operation: {str(ex)}", exc_info=True)
            return web.HTTPBadRequest(reason=str(ex))
