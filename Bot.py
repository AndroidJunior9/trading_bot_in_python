import os
from dotenv import load_dotenv
from alpaca.trading.requests import MarketOrderRequest,StopLossRequest
from alpaca.data.requests import CryptoBarsRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.trading.client import TradingClient
import time



from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

# Get today's date
end = datetime.now()

# Calculate the date one month ago
start = end - timedelta(days=2)





load_dotenv()  # Load environment variables from .env

API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


#

# Market order
# market_order = trading_client.submit_order(
#                 order_data=market_order_data
#                )




while True:
    account_money = trading_client.get_account().cash
    client = CryptoHistoricalDataClient()



    # single symbol request
    request_params = CryptoBarsRequest(
                            symbol_or_symbols=["BTC/USD"],
                            timeframe=TimeFrame(amount=1, unit = TimeFrameUnit.Minute),
                            start=start,
                            end=end,
                            time_in_force= TimeInForce.GTC
                    )

    bars = client.get_crypto_bars(request_params)

    df = bars.df


    # Calculate the moving averages
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()

    # Define the signal
    df['Signal'] = 0.0  
    df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1.0
    df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1.0
    latest_data_point = df.iloc[-1]
   
    

    
  
    # Check if the 20-day moving average has crossed the 50-day moving average

    notional = 0.01*account_money
    
    if latest_data_point['SMA_20'] > latest_data_point['SMA_50']:
        print("Buy signal: The 20-minute moving average has crossed above the 50-minute moving average.")
        market_order_data = MarketOrderRequest(
            symbol = "BTC/USD",
            notional = notional,
            side = OrderSide.BUY,
            stop_loss = StopLossRequest(stop_price=latest_data_point['close']*0.95),
            time_in_force = TimeInForce.GTC
        )
        market_order = trading_client.submit_order(market_order_data)
    elif latest_data_point['SMA_20']<latest_data_point['SMA_50']:
        print("Closing All positions")
        trading_client.close_all_positions(cancel_orders=True)
        


    


    
    time.sleep(60)  # Sleep for 1 Minute

        