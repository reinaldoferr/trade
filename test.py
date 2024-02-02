#import yfinance_timeframe_converter.converter as c
#import yfinance_timeframe_converter as converter
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import pandas as pd 
import pytz
import os

'''
# set if load dataframe from Intenet or saved .csv 
download_from_internet = True

# set Datetime period
start_download = dt.datetime.now()-dt.timedelta(days = 3)
end_download = dt.datetime.now() -dt.timedelta(days = 1) #-dt.timedelta(hours=2)

# create both timezone objects
old_timezone = pytz.timezone("America/Buenos_Aires") ## Zona horaria de la PC
new_timezone = pytz.timezone("Europe/London") ## Zona horaria de cotización de yahoo finance

# alterar las fechas desde-hasta para el periodo
localized_start_download = old_timezone.localize(start_download)
new_start_download = localized_start_download.astimezone(new_timezone)
localized_end_download = old_timezone.localize(end_download)
new_end_download = localized_end_download.astimezone(new_timezone)
print (f'desde: {start_download} hasta: {end_download} timezone: {old_timezone}')
print (f'desde: {new_start_download} hasta: {new_end_download} timezone: {new_timezone}')
start_download = new_start_download
end_download = new_end_download

ticket = "SOL-USD"
input_timeframe = "1h"
output_timeframe  = "1wk"

# Verificar si existe la carpeta en el disco donde se guardarán los archivos, sino la crea.
if not (os.path.exists('raw_data')):
    print ('Creado carpeta raw_data')
    os.mkdir('raw_data')


if (download_from_internet == False):
    df = pd.read_csv(f'raw_data/{ticket}_{input_timeframe}.csv')
else:
    yf.pdr_override()  
    df = pdr.get_data_yahoo(tickers=ticket, interval=input_timeframe,start=start_download,end=end_download)
    df.index = df.index.tz_convert('America/Buenos_Aires')

print (df.tail(10))
df.to_csv(f'raw_test/{ticket}_{input_timeframe}.csv',index_label=False)



#df2 = yf.Ticker(ticket).history(start=start_download, end=end_download, interval=input_timeframe, auto_adjust=True)
#df2.index = df2.index.tz_convert('America/Buenos_Aires')
#print (df2.tail(10))

ohlc = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}

#df = df.resample('4h', base=15).apply(ohlc)
#df = df.between_time('09:30', '15:30')

#anda...
#df = df.resample('4h',base=1).apply(ohlc)
#Anda...
#df_4h = df.resample('4h').agg(ohlc)

#Activos andaba con este
#df_4h = df.resample('4h', offset='90min').agg(ohlc)
#Crypto andaba con este
#df_4h = df.resample('4h',offset='240min').agg(ohlc)

#Test sin nada
df_4h = df.resample('4h',offset='60min').agg(ohlc)

#eliminar los nullos
#df_4h = df_4h.drop(df_4h[df_4h.Open.isnull()].index)
print (df_4h.tail(10))
df_4h.to_csv(f'raw_test/{ticket}_4H.csv',index_label=False)


'''


import requests
import json

list_columns = ['id','symbol','create','market_cap','volume_24h']
#list_columns = ['symbol']
df = pd.DataFrame(columns=list_columns)


url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
a = []
#for start in range(1, 20000, 5000):  original
#for start in range(1, 10, 5000):
for start in range(1, 5000, 5000): 

    params = {
        'start': start,
        'limit': 5000, #'limit': 5000,
    }

    r = requests.get(url, params=params)
    data = r.json()

   #volume_24h
    
    for number, item in enumerate(data['data']):
        #Andando: print(f"{start+number:4} | {item['symbol']:5} | {item['date_added'][:10]} | marketcup: {item['quote']['USD']['market_cap']} | volume_24h: {item['quote']['USD']['volume_24h']}")

        df = pd.concat([df,pd.DataFrame.from_records([{'id':start+number,'symbol':item['symbol']+'-'+'USD','create':item['date_added'][:10], 'market_cap' : item['quote']['USD']['market_cap'], 'volume_24h': item['quote']['USD']['volume_24h'] }])])
        a.append(item['symbol']+'-'+'USD')
        #print(f"marketcup: {item['quote']['USD']['market_cap']}")
        #print(f"volume_24h: {item['quote']['USD']['volume_24h']}")
        #print(f"{item['market_cap']}")
        #dict = {'id':start+number,'symbol':item['symbol'],'create':item['date_added'][:10]}

#Corto la lista
print(a[0:2]) 

#Primeros 10 por market_cap (descendente)
print(df.sort_values(by=['market_cap'], ascending=False).head(100))
#Converti a lista y mostrar los primeros 5
lista = df['symbol'].tolist()
print(lista[0:5]) 




'''
#print(df)
# Grabar a disco en json
df.to_json('raw_data/cryptosymbol.json', orient='records')#, lines=True)


f= open('raw_data/cryptosymbol.json')
prueba = json.load(f)
# Closing file
f.close()

#print(prueba)

#resultList = list(prueba.items())
resultList = json.loads(prueba)
#resultList = resultList[:4]
# printing the resultant list of a dictionary
#print(resultList)

# Iterating through the json
# list
#for i in prueba['symbol']:
#    print(i)
 

    a = []
for i in range(5):
    # change a = a.append(i) to    
    a.append(i)
print(a)
# [0, 1, 2, 3, 4]

'''