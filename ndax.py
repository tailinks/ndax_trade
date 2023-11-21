import time
from dotenv import load_dotenv
import os
import json
import threading
import websocket
import pyotp
import pandas as pd

load_dotenv("keys.env")


class NDAXClient:
    def __init__(self, url: str = "wss://api.ndax.io/WSGateway/"):
        """
        Initialize the NDAXClient with a WebSocket URL.

        :param url: WebSocket URL for the NDAX API.
        """
        self.url = url
        self.request_sequence_number = 2
        self.ws = None
        self.positions = pd.DataFrame()
        self.connect()

    def connect(self):
        """
        Establishes a WebSocket connection.
        """
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        
    def start(self):
        """
        Starts the WebSocket connection in a separate thread.
        """
        thread = threading.Thread(target=self.ws.run_forever)
        thread.start()

    def on_open(self, ws):
        """
        Callback for when the WebSocket connection is opened.

        :param ws: WebSocket object.
        """
        print("WebSocket opened")
        self.authenticate()

    def on_message(self, ws, message: str):
        """
        Callback for when a message is received from the WebSocket.

        :param ws: WebSocket object.
        :param message: The message received.
        """
        response = json.loads(message)
        method_name = response.get("n")
        payload = json.loads(response.get("o", "{}"))
        print("Received message:", method_name)
        print("Payload:", payload)
    def on_error(self, ws, error: Exception):
        """
        Callback for when an error occurs.

        :param ws: WebSocket object.
        :param error: The error encountered.
        """
        print("Error occurred:", error)

    def on_close(self, ws, close_status_code: int, close_msg: str):
        """
        Callback for when the WebSocket connection is closed.

        :param ws: WebSocket object.
        :param close_status_code: Status code for the closure.
        :param close_msg: The message associated with the closure.
        """
        print("WebSocket closed, trying to reconnect...")
        self.connect()
        
    def _send_request(self, method_name: str, payload: dict):
        """
        Sends a request through the WebSocket.

        :param method_name: The name of the method to call.
        :param payload: The payload of the request.
        """
        frame = {
            "m": 0,  # Message type for request
            "i": self.request_sequence_number,
            "n": method_name,
            "o": json.dumps(payload)
        }
        self.ws.send(json.dumps(frame))
        self.request_sequence_number += 2

    def authenticate(self):
        """
        Sends an authentication request.
        """
        payload = {
            "UserName": os.environ.get("USERNAME"),
            "Password": os.environ.get("PASSWORD"),
        }
        self._send_request("authenticateuser", payload)

    def authenticate_2fa(self):
        """
        Sends a two-factor authentication request.
        """
        secret_key = os.environ.get("2FA_SECRET_KEY")
        totp = pyotp.TOTP(secret_key)
        two_fa_code = totp.now()
        payload = {"Code": two_fa_code}
        self._send_request("Authenticate2FA", payload)
    
    def get_account_positions(self):
        """
        Requests account positions.
        """
        account_id = os.environ.get("ACCOUNT_ID")
        payload = {"AccountId": int(account_id), "OMSId": 1}
        self._send_request("GetAccountPositions", payload)
    
    def subscribe_level1(self, instrument_id=None, symbol=None):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Symbol": symbol if symbol is not None else ""
        }
        self._send_request("SubscribeLevel1", payload)
        
    def subscribe_level2(self, instrument_id=None,  depth=10):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Depth": depth
        }
        self._send_request("SubscribeLevel2", payload)
    def subscribe_ticker(self, instrument_id, interval=60, include_last_count=100):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "Interval": interval,
            "IncludeLastCount": include_last_count
        }
        self._send_request("SubscribeTicker", payload)
    def subscribe_trades(self, instrument_id, include_last_count=100):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "IncludeLastCount": include_last_count
        }
        self._send_request("SubscribeTrades", payload)

    def get_l2_snapshot(self, instrument_id, depth=10):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            'Depth': depth
        }
        self._send_request("GetL2Snapshot", payload)
        
    def getlevel1(self, instrument_id):
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id
        }
        self._send_request("GetLevel1", payload)
        
    