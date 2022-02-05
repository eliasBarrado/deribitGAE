from flask import Flask
from datetime import datetime, timezone, timedelta
import Option
import requests
import time 
import datastore

params = datastore.get_params()

SYMBOL             = params['SYMBOL']
CLOUD_RUN_URL      = params['CLOUD_RUN_URL']

DEBUG = False

app = Flask(__name__)


def get_index_price(index_name):
    payload = {'index_name': index_name}

    resp = requests.post("{}/get_index_price".format(CLOUD_RUN_URL), json=payload)

    print(resp.json())
    
    return resp.json()['result']['index_price']

def get_estimated_delivery_price(index_name):
    
    payload = {'index_name': index_name}

    resp = requests.post("{}/get_index_price".format(CLOUD_RUN_URL), json=payload)
    
    return resp.json()['result']['estimated_delivery_price']

def get_positions(currency, kind):

    payload = {'currency': currency, 'kind': kind}

    resp = requests.post("{}/get_positions".format(CLOUD_RUN_URL), json=payload)

    return resp.json()['result']

def get_call_sold():
    """Assumes there is only an option sold. Return False if there isn't any"""

    options_positions = get_positions(SYMBOL,'option')

    print(options_positions)

    for position in options_positions:
        if(abs(position['size'])) > 0:
            option = Option.Option(position['instrument_name'])
            return option

    return False

def send_market_order(instrument_name, quantity, side):

    payload = {'instrument_name': instrument_name, 'quantity': quantity, 'side': side}

    resp = requests.post("{}/market_order".format(CLOUD_RUN_URL), json=payload)

    print(resp.json())

    return resp.json()['result']

def get_status():

    status = {}

    call_sold = get_call_sold()

    status['call_sold'] = bool(call_sold)

    if(status['call_sold']):
        status['option'] = call_sold

    status['contracts'] = get_perp_contracts()

    status['long_future_covering'] = bool(status['contracts'])

    print(status)

    return status

def sleep(price, strike):
    
    ratio = abs(price/strike - 1)
    seconds_to_sleep = max(0.5, round(ratio*100,2))
    
    print("price: {} strike: {} Putting to sleep for {} seconds".format(price,strike,seconds_to_sleep))
    if(DEBUG):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        time.sleep(20)
    else:
        time.sleep(seconds_to_sleep)
    
    return seconds_to_sleep


def get_perpetual_position():

    positions = get_positions(SYMBOL,'future')

    for x in positions:
        if(x['instrument_name'] == SYMBOL+'-PERPETUAL'):
            perp_positions = x
            return perp_positions 

    return 0

def get_perp_contracts():

    perp_positions = get_perpetual_position()
    if(perp_positions):
        return int(perp_positions['size'])
    
    return 0
    



@app.route('/test')
def test():
    x = '1'
    return str(x)


@app.route('/_ah/start')
def start():


    while(True):
        status = get_status()

        if(status['call_sold']):
            
            strike          = status['option'].get_strike()
            expiration_date = status['option'].get_date()
            

            while(datetime.now(timezone.utc) < expiration_date - timedelta(seconds=10) and status['call_sold']):

                price = get_index_price('{}_usd'.format(SYMBOL.lower()))
                
                if(price > strike):
                    if(status['long_future_covering'] == False):
                        if(SYMBOL == 'BTC'):
                            contracts = round(price/100,-1)
                        if(SYMBOL == 'ETH'):
                            contracts = round(price)
                        print("{} > {} Sending market order to buy {} contracts of underlying".format(price, strike, contracts))
                        send_market_order('{}-PERPETUAL'.format(SYMBOL), contracts, 'buy')
                    else:
                        print("The call is covered")
                        

                if(price < strike):
                    if(status['long_future_covering']):
                        print("{} < {} Sending market order to sell {} contracts of underlying".format(price, strike, status['contracts']))
                        send_market_order('{}-PERPETUAL'.format(SYMBOL), status['contracts'], 'sell')
                    else:
                        print("Call sold is OTM")
                        
                sleep(price,strike)
                status = get_status()
                if(status['call_sold'] == False):
                    break

            while(status['contracts'] > 0):
                print("Call option has expired or has been undone. Selling underlying hedge")
                try:
                    send_market_order('{}-PERPETUAL'.format(SYMBOL), status['contracts'], 'sell')
                except Exception as e:
                    print(e)
                status = get_status()


        else:
            print("There isn't any call sold")
            time.sleep(30)
            status = get_status()

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)









    





