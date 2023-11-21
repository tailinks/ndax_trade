# ndax_trader

ndax_trader is a Python wrapper for the NDAX cryptocurrency exchange.


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