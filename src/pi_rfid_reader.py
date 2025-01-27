from aiohttp import web
import RPi.GPIO as GPIO
from mfrc522 import MFRC522, SimpleMFRC522
import logging
import time
import asyncio
import binascii


class PiRFIDReader:
    """
    A class to handle RFID reading and HTTP response generation for an aiohttp web server.
    """

    def __init__(self, timeout):
        """
        Initialize the RFIDReader with a given RFID reader device.
        """
        self.simple_reader = SimpleMFRC522()
        self.reader = MFRC522()
        self.timeout = timeout

    async def _read_no_block_timeout(self):
        """
        Continuously read the RFID until an ID is found or the timeout is reached.
        """
        ts_end = time.monotonic() + self.timeout
        id = self.simple_reader.read_id_no_block()
        text = ''
        while not id and ts_end > time.monotonic():
            await asyncio.sleep(0.001)
            id, text = self.simple_reader.read_no_block()
        return id, text

    async def _read_uid_NTAG203(self):
        """
        Continuously read the RFID until an ID is found or the timeout is reached.
        It returns a string that represents the UID for NTAG203 in hex.
        """
        ts_end = time.monotonic() + self.timeout
        while ts_end > time.monotonic():
            await asyncio.sleep(0.001)
            (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status is self.reader.MI_OK:
                (status, uid) = self.reader.MFRC522_Anticoll()
                if status is self.reader.MI_OK:
                    tag = self.reader.MFRC522_SelectTag(uid)
                    raw_data = self.reader.MFRC522_Read(0)
                    if not raw_data:
                        raise Exception("Could not read uid. Probably not an NTAG203.")
                    b = bytearray(raw_data)
                    id = str(binascii.b2a_hex(b[0:3] + b[4:8]), 'utf-8')
                    return id.lower()
        return None

    async def scan_handler(self, request):
        """
        Handle incoming scan requests, read RFID, and return JSON response.
        """
        try:
            maybe_id = None
            text = None

            if "tag" in request.query and request.query["tag"].lower() == "ntag203":
                maybe_id = await self._read_uid_NTAG203()
            else:
                maybe_id, text = await self._read_no_block_timeout()

            if maybe_id is not None:
                data = { "id": maybe_id }
                if text:
                    data["text"] = text.replace("\u0000", "")
                logging.info(f"Scanned ID: {maybe_id}")
                return web.json_response(data)
            else:
                logging.warning("No ID found before timeout")
                return web.HTTPRequestTimeout()
        except Exception as ex:
            logging.error(f"Error during operation: {str(ex)}", exc_info=True)
            return web.HTTPBadRequest(reason=str(ex))
