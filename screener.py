'''
App para bajar todos los datos de stock en CSV
a la carpeta raw_data

File name: download.py

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
import os
import pandas as pd  
import pandas_ta as ta 
import pandas_datareader as web
import datetime as dt
from yahoo_fin import stock_info as si
import yfinance as yf # esta es por si hay que sacarlo en un periodo que no sea diario


# Merval 
merval = ['ALUA.BA', 'BBAR.BA', 'BMA.BA', 'BYMA.BA', 'GGAL.BA', 'SUPV.BA', 'PAMP.BA', 'YPFD.BA', 'VALO.BA', 'CEPU.BA', 'TRAN.BA', 'TXAR.BA', 'LOMA.BA', 'HARG.BA', 'COME.BA', 'CRES.BA', 'TGNO4.BA', 'TGSU2.BA', 'EDN.BA', 'CVH.BA', 'MIRG.BA', 'TECO2.BA']

# Otras Argentinas (Panel General, no Merval)
otras = ['AGRO.BA', 'OEST.BA', 'AUSO.BA']

# SP500
sp500 = si.tickers_sp500()

# NySE
nyse = si.tickers_dow()

# NASDAQ
nasdaq = si.tickers_nasdaq()

# Ejemplo para eliminar repetidas con un conjunto
#tickers = list(set(merval+otras+sp500+nyse+nasdaq))
#tickers = list(set(merval+otras))
tickers = ['ALUA.BA', 'PAMP.BA', 'YPFD.BA','LOMA.BA']
#tickers = ['AMZN']

# Periodo de datos a bajar
start_download = dt.datetime.now()-dt.timedelta(days = 30)
end_download = dt.datetime.now() -dt.timedelta(days = 1)

# Intervalo de los datos 1m --> 1 minuto, 1h --> 1 hora
#interval = ['1m','2m','5m','15m','30m','60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
myinterval = '1h'

# Verificar si existe la carpeta en el disco donde se guardarán los archivos, sino la crea.
if not (os.path.exists('raw_data')):
    print ('Creado carpeta raw_data')
    os.mkdir('raw_data')


# Setear las variables de conteo
i = 1
j = len(tickers) 

# Loop por los tickets, bajarlos y luego salvarlos en CSVs
# para levantarlos luego desde allí, pero ya desconectado
"""
for ticker in tickers:
    
    try:
    
        # Download the ticker data
        print(f'Download {ticker} timeframe {myinterval}...({i} de {j})')
                        
        # Bajar los datos del tickets
        df = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=myinterval, auto_adjust=True)

        # Redondeo
        df = df.round({'Open':4, 'High':4, 'Low':4, 'Close':4, 'Volume':1, 'Dividends':1, 'Stock Splits':1})
        print (df.head(2))
        print (df.tail(2))

        # Volver a salvar el archivo con la info nueva
        print(f'Exportar a CSV raw_data/{ticker}_{myinterval} desde el {start_download}...')
        df.to_csv(f'raw_data/{ticker}_{myinterval}.csv',index_label=False)
   
    except:
        pass

    i += 1
"""

# Setear las variables de conteo
i = 1
j = len(tickers)

# Leer los tickets desde el CSV
for ticker in tickers:
    
    try:
        
        # Leer el archivo previamente descargado de yahoo finance
        df1 = pd.read_csv(f'raw_data/{ticker}_{myinterval}.csv')
        
        # Calculo de Emas, SMA, RSIs
        df1["EMA_21"] = ta.ema(df1.Close, length=21)        
        df1["SMA_30"] = ta.sma(df1.Close, length=30) 
        df1["EMA_150"] = ta.ema(df1.Close, length=150)   
        df1["EMA_200"] = ta.ema(df1.Close, length=200) 
        df1["RSI_9"] = ta.rsi(df1.Close, length=9)    
        df1["RSI_14"] = ta.rsi(df1.Close, length=14)  
        
        
        # Señales de compras 
        # según Andy Stop Loss, si está encima de la media de 21 en Arg es compra, encima de la media de 30 en EEUU es compra
        #df1.loc[(df1['Close'] > df1['EMA_21']), 'Buy_21'] = 'Yes'
        #df1.loc[(df1['Close'] <= df1['EMA_21']), 'Buy_21'] = 'No'
        #df1.loc[(df1['Close'] > df1['SMA_30']), 'Buy_30'] = 'Yes'
        #df1.loc[(df1['Close'] <= df1['SMA_30']), 'Buy_30'] = 'No'

        # Señal de compra Reinaldo
        df1.loc[(df1['RSI_9'] < 30), 'Buy_RSI_9'] = 'Yes'

        # Señales de venta
        # Según andy stop loss
        #df1.loc[(df1['Close'] < df1['EMA_21']), 'Sell_21'] = 'Yes'
        #df1.loc[(df1['Close'] >= df1['EMA_21']), 'Sell_21'] = 'No'
        #df1.loc[(df1['Close'] < df1['SMA_30']), 'Sell_30'] = 'Yes'
        #df1.loc[(df1['Close'] >= df1['SMA_30']), 'Sell_30'] = 'No'

        # Señal de venta Reinaldo
        df1.loc[(df1['RSI_9'] > 70), 'Sell_RSI_9'] = 'Yes'

        # Exportar a Excel
        df1.to_excel(f'raw_data/{ticker}_{myinterval}_process.xlsx')

    except:
        pass

    i += 1





#print (df1.head(2))
#print (df1.tail(2))
print ('Fin.')
