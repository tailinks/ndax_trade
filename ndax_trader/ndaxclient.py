from dotenv import load_dotenv
import os
import json
import threading
import websocket
import pyotp
import pandas as pd

load_dotenv("keys.env")


class NDAXClient:
    """
    A client for interacting with the NDAX API through WebSocket.

    Attributes:
        url (str): The WebSocket URL for the NDAX API.
        request_sequence_number (int): The sequence number for request messages.
        ws (WebSocketApp): The WebSocket connection object.
        positions (pd.DataFrame): DataFrame to store account positions.
    """

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
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

        if not username or not password:
            raise ValueError("Environment variables 'USERNAME' and 'PASSWORD' must be set.")

        payload = {
            "UserName": username,
            "Password": password,
        }
        self._send_request("authenticateuser", payload)


    def authenticate_2fa(self):
        """
        Sends a two-factor authentication request.
        """
        secret_key = os.environ.get("2FA_SECRET_KEY")
        if not secret_key:
            raise ValueError("Environment variables '2FA_SECRET_KEY' must be set.")

        totp = pyotp.TOTP(secret_key)
        two_fa_code = totp.now()
        payload = {"Code": two_fa_code}
        self._send_request("Authenticate2FA", payload)
    
    def get_account_positions(self):
        """
        Requests account positions.
        """
        account_id = os.environ.get("ACCOUNT_ID")
        if not account_id:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        payload = {"AccountId": int(account_id), "OMSId": 1}
        self._send_request("GetAccountPositions", payload)
    
    def subscribe_level1(self, instrument_id=None, symbol=None):
        """
        Subscribes to Level 1 data for a specific instrument.

        :param instrument_id: The ID of the instrument to subscribe to.
        :param symbol: The symbol of the instrument to subscribe to.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Symbol": symbol if symbol is not None else ""
        }
        self._send_request("SubscribeLevel1", payload)
        
    def subscribe_level2(self, instrument_id=None,  depth=10):
        """
        Subscribes to Level 2 data for a specific instrument.

        :param instrument_id: The ID of the instrument to subscribe to.
        :param depth: The depth of the Level 2 data to subscribe to.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Depth": depth
        }
        self._send_request("SubscribeLevel2", payload)
    
    def subscribe_ticker(self, instrument_id, interval=60, include_last_count=100):
        """
        Subscribes to ticker data for a specific instrument.

        :param instrument_id: The ID of the instrument to subscribe to.
        :param interval: The interval in seconds for the ticker data.
        :param include_last_count: The number of previous ticker data to include.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "Interval": interval,
            "IncludeLastCount": include_last_count
        }
        self._send_request("SubscribeTicker", payload)
    
    def subscribe_trades(self, instrument_id, include_last_count=100):
        """
        Subscribes to trade data for a specific instrument.

        :param instrument_id: The ID of the instrument to subscribe to.
        :param include_last_count: The number of previous trade data to include.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "IncludeLastCount": include_last_count
        }
        self._send_request("SubscribeTrades", payload)

    def get_l2_snapshot(self, instrument_id, depth=10):
        """
        Requests a Level 2 snapshot for a specific instrument.

        :param instrument_id: The ID of the instrument to request the snapshot for.
        :param depth: The depth of the snapshot data to request.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            'Depth': depth
        }
        self._send_request("GetL2Snapshot", payload)
        
    def getlevel1(self, instrument_id):
        """
        Requests Level 1 data for a specific instrument.

        :param instrument_id: The ID of the instrument to request the data for.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id
        }
        self._send_request("GetLevel1", payload)
        
    def logout(self):
        """
        Sends a logout request.
        """
        self._send_request("LogOut", {})
        
    def subscribeaccountevents(self,):
        """
        Subscribes to account events.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("SubscribeAccountEvents", payload)
    
    def unsubscribe_level1(self, instrument_id=None, symbol=None):
        """
        Unsubscribes from Level 1 data for a specific instrument.

        :param instrument_id: The ID of the instrument to unsubscribe from.
        :param symbol: The symbol of the instrument to unsubscribe from.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Symbol": symbol if symbol is not None else ""
        }
        self._send_request("UnsubscribeLevel1", payload)
        
    def unsubscribe_level2(self, instrument_id=None,  depth=10):
        """
        Unsubscribes from Level 2 data for a specific instrument.

        :param instrument_id: The ID of the instrument to unsubscribe from.
        :param depth: The depth of the Level 2 data to unsubscribe from.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id if instrument_id is not None else 0,
            "Depth": depth
        }
        self._send_request("UnsubscribeLevel2", payload)
    
    def unsubscribe_ticker(self, instrument_id, interval=60, include_last_count=100):
        """
        Unsubscribes from ticker data for a specific instrument.

        :param instrument_id: The ID of the instrument to unsubscribe from.
        :param interval: The interval in seconds for the ticker data.
        :param include_last_count: The number of previous ticker data to include.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "Interval": interval,
            "IncludeLastCount": include_last_count
        }
        self._send_request("UnsubscribeTicker", payload)
    
    def unsubscribe_trades(self, instrument_id, include_last_count=100):
        """
        Unsubscribes from trade data for a specific instrument.

        :param instrument_id: The ID of the instrument to unsubscribe from.
        :param include_last_count: The number of previous trade data to include.
        """
        payload = {
            "OMSId": 1,
            "InstrumentId": instrument_id,
            "IncludeLastCount": include_last_count
        }
        self._send_request("UnsubscribeTrades", payload)
        
    def getaccountinfo(self):
        """
        Requests account information.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("GetAccountInfo", payload)
    
    def getopentradereports(self):
        """
        Requests open trade reports.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("GetOpenTradeReports", payload)
    
    def gettickerhistory(self):
        """
        Requests ticker history.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("GetTickerHistory", payload)
    
    def cancellallorders(self):
        """
        Cancels all orders.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("CancelAllOrders", payload)
        
    def cancelorder(self, order_id):
        """_summary_

        Args:
            order_id (_type_): _description_
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID")),
            "OrderId": order_id
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("CancelOrder", payload)
        
    def getopenorders(self):
        """
        Requests open orders.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID"))
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("GetOpenOrders", payload)
    
    def sendorder(self, instrument_id, side, order_type, quantity, timeinforce, usedisplayquantity=False, price=None):
        """
        Sends an order.

        :param instrument_id: The ID of the instrument to send the order for.
        :param side: The side of the order.
        :param order_type: The type of the order.
        :param quantity: The quantity of the order.
        :param price: The price of the order.
        """
        payload = {
            "OMSId": 1,
            "AccountId": int(os.environ.get("ACCOUNT_ID")),
            "InstrumentId": instrument_id,
            "TimeInForce": timeinforce,
            "Side": side,
            "OrderType": order_type,
            "UseDisplayQuantity": usedisplayquantity,
            "Quantity": quantity,
            "LimitPrice": price if price is not None else 0
        }
        if not payload["AccountId"]:
            raise ValueError("Environment variables 'ACCOUNT_ID' must be set.")
        self._send_request("SendOrder", payload)
        
    def getproducts(self):
        """
        Requests products.
        """
        payload = {
            "OMSId": 1
        }
        self._send_request("GetProducts", payload)