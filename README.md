# ndax_trader

`ndax_trader` is a Python wrapper for the NDAX cryptocurrency exchange API. It simplifies the process of making requests and managing responses from the NDAX WebSocket API.

## Installation

You can install `ndax_trader` using pip:

```bash
pip install ndax_trader
```

## Setup
Before using ndax_trader, you need to set up your environment variables. Create a file named keys.env in your project root directory and include the following variables:
```markdown
ACCOUNT_ID=your_account_id
2FA_SECRET_KEY=your_2fa_secret_key
USERNAME=your_username
PASSWORD=your_password

```
Replace your_account_id, your_2fa_secret_key, your_username, and your_password with your actual NDAX account details.

## Usage
```python
from ndax import NDAXClient

client = NDAXClient()

#initialize websocket connection
client.start()

#Requests account positions.
client.get_account_positions()

#Subscribe to level 1 data for specific instrument
client.subscribe_level1(7)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)