'''
App para bajar todos los datos de stock en CSV
a la carpeta raw_data

File name: download.py - prueba

'''

# Requerimientos, ejecutar en el terminal:
# pip install pandas
# pip install pandas_ta
# pip install pandas_datareader
# pip install yahoo-finance
# pip install yahoo-fin
# pip install yfinance
# pip install pyarrow
# pip install XlsxWriter

# pip install yfinance-timeframe-converter ????

import os
import pandas as pd  
import pandas_ta as ta 
import pandas_datareader as web
import datetime as dt
from yahoo_fin import stock_info as si
import yfinance as yf # esta es por si hay que sacarlo en un periodo que no sea diario
import pytz
import requests
import json

inicio = dt.datetime.now()

#----------------------------------------------------------------------------
# Traer la lista de simbolos desde internet
crypto_columns = ['id','symbol','create','market_cap','volume_24h']
#list_columns = ['symbol']
df_crypto = pd.DataFrame(columns=crypto_columns)

url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
#crypto_symbol = []
for start in range(1, 20000, 5000): #for start in range(1, 20000, 5000):
    params = {
        'start': start,
        'limit': 5000, 
    }
    r = requests.get(url, params=params)
    data = r.json()
    
    for number, item in enumerate(data['data']):
        #crypto_symbol.append(item['symbol']+'-'+'USD')
        df_crypto = pd.concat([df_crypto,pd.DataFrame.from_records([{'id':start+number,'symbol':item['symbol']+'-'+'USD','create':item['date_added'][:10], 'market_cap' : item['quote']['USD']['market_cap'], 'volume_24h': item['quote']['USD']['volume_24h'] }])])

#ORdernar por market cap
df_cryto = df_crypto.sort_values(by=['market_cap'], ascending=False)
#Converti a lista y mostrar los primeros 5
lista_cryto = df_crypto['symbol'].tolist()
tickers = lista_cryto[0:30]

#Solo los primeros 5 registros
#tickers = crypto_symbol[:5]
#----------------------------------------------------------------------------


# crypto-currency
#tickers = ['ADA-USD','AVAX-USD','BNB-USD','BTC-USD','DOGE-USD','DOT-USD','LINK-USD','MATIC-USD','ETH-USD','SHIB-USD','SOL-USD','TRIAS-USD','TON-USD','TRX-USD','XRP-USD']
#tickers = ['SOL-USD']


# Periodo de datos a bajar
start_download = dt.datetime.now()-dt.timedelta(days = 30)
end_download = dt.datetime.now() #-dt.timedelta(hours=2)


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

# Intervalo de los datos 1m --> 1 minuto, 1h --> 1 hora
#interval = ['1m','2m','5m','15m','30m','60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
myinterval = '4h'
change_interval = False

# Si hay un cambio a 4H hay que convertir luego los datos
if myinterval == '4h':
    change_interval = True
    input_timeframe = '1h'
else:
     input_timeframe = myinterval          
     
# Función que determina si 
# 1 = Sell
# 2 = Buy
# 0 = nada
def total_signal(df, current_candle, backcandles):
    if (df.rsi_9[current_candle]<30):
            return 2 #long signal
    if (df.rsi_9[current_candle]>70):
            return 1 #short signal
    return 0

# Esto se usa para convertir los datos de !H a 4H
ohlc = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}

# Verificar si existe la carpeta en el disco donde se guardarán los archivos, sino la crea.
if not (os.path.exists('raw_data')):
    print ('Creado carpeta raw_data')
    os.mkdir('raw_data')

   

#Crear un pandas.DataFrame para guardar los valores de los tickets que cumplan ciertas condiciones
#con las columnas Ticker,Latest_Price,Score,PE_Ratio,PEG_Ratio,SMA_150,SMA_200,52_Week_Low,52_Week_High
list_columns = ['ticker','date','close','volume','ema_21','sma_20','sma_30','ema_150','ema_200','rsi_9','rsi_14','buy_rsi_9','sell_rsi_9']
final_df = pd.DataFrame(columns=list_columns)
#tmp = pd.DataFrame(columns=list_columns)
#final_df.set_index('ticker')
#tmp.set_index('ticker')

# Setear las variables de conteo
i = 1
j = len(tickers) 

# Loop por los tickets, bajarlos y luego salvarlos en CSVs
# para levantarlos luego desde allí, pero ya desconectado

for ticker in tickers:
    
    try:
    
        # Download the ticker data
        print(f'Download {ticker} timeframe {input_timeframe}...({i} de {j} from {start_download} to {end_download})')
                        
        # Bajar los datos del tickets
        df_orig = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=input_timeframe, auto_adjust=True)

        # Cambio zona horaria
        # Mirar https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
        df_orig.index = df_orig.index.tz_convert('America/Buenos_Aires')
      
        # Salvar el archivo original descargado con el time frame correspondiente
        print(f'Exportar a CSV raw_data/{ticker}_{input_timeframe} desde el {start_download}...')
        df_orig.to_csv(f'raw_data/{ticker}_{input_timeframe}.csv',index_label=False)
        
        # Convertir de 1H a 4H si está así solicitado
        if change_interval == True:
            df = df_orig.resample('4h',offset='60min').agg(ohlc)

        # Redondeo
        #df = df.round({'Open':4, 'High':4, 'Low':4, 'Close':4, 'Volume':1, 'Dividends':1, 'Stock Splits':1})
        #print (df.head(2))
        #print (df.tail(2))

        # Volver a salvar el archivo convertido al timeframe que pidio el usuario
        print(f'Exportar a CSV raw_data/{ticker}_{myinterval} desde el {start_download}...')
        df.to_csv(f'raw_data/{ticker}_{myinterval}.csv',index_label=False)

    except:
        pass

    i += 1







# Setear las variables de conteo
i = 1
j = len(tickers)
if change_interval == True:
    h = 2
else:
    h = 1
#print(f'h:{h}')    

# Leer los tickets desde el CSV
for x in range(0, h):
    
       
    if x == 1:
        inter=input_timeframe
    else:
        inter=myinterval
    print(f'x:{x}, interval: {inter}') 
    for ticker in tickers:
        
        try:
            
            
            # Leer el archivo previamente descargado de yahoo finance
            df1 = pd.read_csv(f'raw_data/{ticker}_{inter}.csv')
            print(f'Leyendo ticket: raw_data/{ticker}_{inter}.csv...')
            
            # Calculo de Emas, SMA, RSIs, ADX
            df1["ema_21"] = ta.ema(df1.Close, length=21)        
            df1["sma_20"] = ta.sma(df1.Close, length=20) 
            df1["sma_30"] = ta.sma(df1.Close, length=30) 
            df1["ema_150"] = ta.ema(df1.Close, length=150)   
            df1["ema_200"] = ta.ema(df1.Close, length=200) 
            df1["rsi_9"] = ta.rsi(df1.Close, length=9)    
            df1["rsi_14"] = ta.rsi(df1.Close, length=14)  
            
            #ADX
            #a = ta.adx(df1['High'], df1['Low'], df1['Close'], length = 14)
            #df1 = df1.join(a)
        
            # Señales de compras 
            # según Andy Stop Loss, si está encima de la media de 21 en Arg es compra, encima de la media de 30 en EEUU es compra
            #df1.loc[(df1['Close'] > df1['EMA_21']), 'Buy_21'] = 'yes'
            #df1.loc[(df1['Close'] <= df1['EMA_21']), 'Buy_21'] = 'no'
            #df1.loc[(df1['Close'] > df1['SMA_30']), 'Buy_30'] = 'yes'
            #df1.loc[(df1['Close'] <= df1['SMA_30']), 'Buy_30'] = 'No'

            # Señal de compra Reinaldo
            df1.loc[(df1['rsi_9'] < 30), 'buy_rsi_9'] = 'yes'

            # Señales de venta
            # Según andy stop loss
            #df1.loc[(df1['Close'] < df1['EMA_21']), 'Sell_21'] = 'yes'
            #df1.loc[(df1['Close'] >= df1['EMA_21']), 'Sell_21'] = 'no'
            #df1.loc[(df1['Close'] < df1['SMA_30']), 'Sell_30'] = 'yes'
            #df1.loc[(df1['Close'] >= df1['SMA_30']), 'Sell_30'] = 'no'

            # Señal de venta Reinaldo
            df1.loc[(df1['rsi_9'] > 70), 'sell_rsi_9'] = 'yes'
            #print(df1.tail())

            # Calculando las señales de compra y venta
            #print ('Calculando señales de buy/sell...')  
            
            #df['TotalSignal'] = df.apply(lambda row: total_signal(df, row.name, 7), axis=1)   
            #df1['totalsignal'] = df1.apply(lambda row: total_signal(df1, row.name, 7), axis=1)
            #df1['totalsignal'] = 0

            # Exportar a Excel
            df1.to_excel(f'raw_data/{ticker}_{inter}_process.xlsx')
            
            # Construir un Dataframe Nuevo, Resumen de aquellos que tienen
            #print(df1.tail(1))
            
            #tomar solo la última fila del dataframe
            fecha = df1.index[-1]
            cierre = df1['Close'].iloc[-1]
            volume = df1['Volume'].iloc[-1]
            ema_21 = df1['ema_21'].iloc[-1]
            sma_20 = df1['sma_20'].iloc[-1]
            sma_30 = df1['sma_30'].iloc[-1]
            ema_150 = df1['ema_150'].iloc[-1]
            ema_200 = df1['ema_200'].iloc[-1]
            rsi_9 = df1['rsi_9'].iloc[-1]
            rsi_14 = df1['rsi_14'].iloc[-1]
            buy_rsi_9 = df1['buy_rsi_9'].iloc[-1]
            sell_rsi_9 = df1['sell_rsi_9'].iloc[-1]
            #signal = df1['totalsignal'][-1]
            #print(f'ticker: {ticker}-{inter}, Cierre: {cierre}, Fecha: {fecha}, volume: {volume}, ema_21: {ema_21}, sma_20: {sma_20}, sma_30: {sma_30}, ema_150: {ema_150}, ema_200: {ema_200}, rsi_9: {rsi_9}, rsi_14: {rsi_14}, buy_rsi_9: {buy_rsi_9}, sell_rsi_9: {sell_rsi_9}')

            #list_columns = ['ticker','date','close','volume','ema_21','sma_20','sma_30','ema_150','ema_200','rsi_9','rsi_14','buy_rsi_9','sell_rsi_9']
            try:
                print(inter == myinterval)
                if (inter == myinterval):
                    final_df = pd.concat([final_df,pd.DataFrame({'ticker' : ticker + '-' + inter, 
                                            'date' : fecha,
                                            'close' : cierre,
                                            'volume' : volume,
                                            'ema_21' : ema_21,
                                            'sma_20' : sma_20,
                                            'sma_30' : sma_30,
                                            'ema_150' : ema_150,
                                            'ema_200' : ema_200,
                                            'rsi_9' : rsi_9,
                                            'rsi_14' : rsi_14,
                                            'buy_rsi_9' : buy_rsi_9,
                                            'sell_rsi_9' : sell_rsi_9}, index=[i])], ignore_index=True)
            except Exception as e1:
                print(e1)
            
        except Exception as e2:
            print(e2)

        i += 1

#print(final_df)
#final_df.set_index('ticker')

# Exportar a Excel
final_df.to_excel('raw_data/resume.xlsx')

#Imprimir aquellos que tienen señal buy/sell
#df['column_name'] >= A & df['column_name'] <= B
#print(final_df.loc[final_df['sell_rsi_9'] == 'yes' | final_df['buy_rsi_9'] == 'yes'])
#print(final_df)
#Solo las que tiene señales
print(final_df.query('sell_rsi_9 == "yes" or buy_rsi_9 == "yes"'))
        
#print (df1.head(2))
#print (df1.tail(2))
fin = dt.datetime.now()
print (f'Inicio: {inicio} Fin: {fin}')
