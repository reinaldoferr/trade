

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
import math
import numpy as np

RAD_TO_DEGREE = 180/3.14159265359 
TOP_ANGLE = 3.
BOTTOM_ANGLE = -3.

# Stock Symbols
#tickers = ['AMZN','AAPL','PEP','PG']
tickers = ['AMZN']


# Periodo de datos a bajar
start_download = dt.datetime.now()-dt.timedelta(days = 20 )
end_download = dt.datetime.now() #-dt.timedelta(hours=2)

# create both timezone objects
old_timezone = pytz.timezone("America/Buenos_Aires") ## Zona horaria de la PC GMT-3
new_timezone = pytz.timezone("America/New_York") ## Zona horaria de cotización New York GMT-5

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
myinterval = '1h'
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


#Crear un pandas.DataFrame para guardar los valores de los tickets que cumplan ciertas condiciones
#con las columnas Ticker,Latest_Price,Score,PE_Ratio,PEG_Ratio,SMA_150,SMA_200,52_Week_Low,52_Week_High
#list_columns = ['ticker','date','close','volume','ema_21','sma_20','sma_30','ema_150','ema_200','rsi_9','rsi_14','buy_rsi_9','sell_rsi_9','rsi_9_signal']
list_columns = ['ticker','date','close','volume','ema_21','sma_20','sma_30','ema_150','ema_200','rsi_9','rsi_14','rsi_9_signal']
final_df = pd.DataFrame(columns=list_columns)

'''
def total_signal(df, current_candle, backcandles):
    if (ema_signal(df, current_candle, backcandles)==2
        and df.Close[current_candle]<=df['BBL_15_1.5'][current_candle]
        #and df.RSI[current_candle]<60
        ):
            return 2
    if (ema_signal(df, current_candle, backcandles)==1
        and df.Close[current_candle]>=df['BBU_15_1.5'][current_candle]
        #and df.RSI[current_candle]>40
        ):
    
            return 1
    return 0
# sample        
#df['TotalSignal'] = df.apply(lambda row: total_signal(df, row.name, 7), axis=1)
'''


def find_pivot_highs(data, length):
    pivot_highs = []
    for i in range(length, len(data) - length):
        if (
            data[i] > max(data[i - length : i])
            and data[i] > max(data[i + 1 : i + length + 1])
        ):
            #pivot_highs.append(i)
            print(f'pivot_high: {data[i]}')
            pivot_highs.append(data.index[i])
           
    return pivot_highs


def find_pivot_lows(data, length):
    pivot_lows = []
    for i in range(length, len(data) - length):
        if (
            data[i] < min(data[i - length : i])
            and data[i] < min(data[i + 1 : i + length + 1])
        ):
            #pivot_lows.append(i)
            print(f'pivot_low: {data[i]}')
            pivot_lows.append(data.index[i])

    return pivot_lows


# Setear las variables de conteo
i = 1
j = len(tickers) 

# Loop por los tickets, bajarlos y luego salvarlos en CSVs
# para levantarlos luego desde allí, pero ya desconectado

for ticker in tickers:
    
    try:
    
        # Download the ticker data
        print(f'Download {ticker} timeframe {myinterval}...({i} de {j} from {start_download} to {end_download})')
                        
        # Bajar los datos del tickets
        df = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=input_timeframe, auto_adjust=True)
        #print(df.tail(5))
        
        # Cambio zona horaria
        # Mirar https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
        df.index = df.index.tz_convert('America/Buenos_Aires')
        #print(df.tail(5))

        # Convertir de 1H a 4H si está así solicitado
        if change_interval == True:
            df = df.resample('4h',offset='60min').agg(ohlc)

        # Calculo de Emas, SMA, RSIs, ADX
        df["ema_21"] = ta.ema(df.Close, length=21)        
        df["sma_20"] = ta.sma(df.Close, length=20) 
        df["sma_30"] = ta.sma(df.Close, length=30) 
        df["ema_150"] = ta.ema(df.Close, length=150)   
        df["ema_200"] = ta.ema(df.Close, length=200) 
        df["rsi_9"] = ta.rsi(df.Close, length=9)    
        df["rsi_14"] = ta.rsi(df.Close, length=14)
        atr = ta.adx(df['High'], df['Low'], df['Close'], length = 14)
        df = df.join(atr)

        #---------------
        # Cruce de precio con la SMA 30 Andy
        df['andy_sma_30_signal'] = 0
        df.loc[(df['sma_30'] < df["Close"]), 'andy_sma_30_signal'] = 2
        df.loc[(df['sma_30'] > df["Close"]), 'andy_sma_30_signal'] = 1
        df['andy_ema_21_signal'] = 0
        df.loc[(df['ema_21'] < df["Close"]), 'andy_ema_21_signal'] = 2
        df.loc[(df['ema_21'] > df["Close"]), 'andy_ema_21_signal'] = 1
        #---------------


        '''
        # Otras Medias con ejemplo de cruce 
        df['sma_10'] = ta.sma(df['Close'],length=10)
        df['sma_50'] = ta.sma(df['Close'],length=50)
        df['sma_200'] = ta.sma(df['Close'],length=200)
        df['10_cross_30'] = np.where(df['sma_10'] > df['sma_30'], 1, 0)
        df['abv_50'] = np.where((df['sma_30']>df['sma_50'])&(df['sma_10']>df['sma_50']), 1, 0)
    
        df['abv_200'] = np.where((df['sma_30']>df['sma_200'])&(df['sma_10']>df['sma_200'])&(df['sma_50']>df['sma_200']), 1, 0)
        '''


        #--------------------------------
        # MACD
        # Calculate the 12-period EMA
        
        # Nueva forma de calculo
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal_line'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']

        # Vieja forma de calculo
        # Calculate the 26-period EMA
        #ema_fast = df['Close'].ewm(span=12, adjust=False).mean()
        #ema_slow = df['Close'].ewm(span=26, adjust=False).mean()
        # Calculate MACD (the difference between 12-period EMA and 26-period EMA)
        #df['macd'] = ema_fast - ema_slow
        # Calculate the 9-period EMA of MACD (Signal Line)
        #df['macd_signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        #df['macd_hist'] = df['macd'] - df['macd_signal_line']

        # Cruces
        df['macd_signal_macd'] = np.where(df['macd_signal_line'] < df['macd'], 1, 0)
        df['macd_lim'] = np.where(df['macd']>0, 1, 0)
        #--------------------------------



        '''
        #--------------------------------
        # Calculo de Altos + altos y Bajos mas bajos
        #df['hh'] = np.where(df['High'] > df['High'].shift(1), True, False)
        #df['ll'] = np.where(df['Low'] < df['Low'].shift(1), True, False)

        
        # initialize new columns with np.nan or any other fill value
        df['ph'] = np.nan
        df['pl'] = np.nan
        print('Calculo de HH-LL...')
        pivot_highs = find_pivot_highs(df['High'], 3)
        print(f'pivot_highs: {pivot_highs}')
        pivot_lows = find_pivot_lows(df['Low'], 3)
        print(f'pivot_lows: {pivot_lows}')
        
        # assign the value True to the corresponding indices
        for x in pivot_highs:
            df.loc[x,'ph'] = True  #df.iloc[i, 'ph'] = True

        for x in pivot_lows:
            df.loc[x,'pl'] = True  #df.iloc[i, 'pl'] = True
        
        atr = ta.atr(df['High'], df['Low'], df['Close'], 14)
        df['slope_atr'] = atr / 14
        df['slope_ph'] = df['slope_atr'].where(df['ph'] == True).ffill()
        df['slope_pl'] = df['slope_atr'].where(df['pl'] == True).ffill()
        df['upper'] = df['ph'].where(df['ph'] == True).ffill() - df['slope_ph']
        df['lower'] = df['pl'].where(df['pl'] == True).ffill() + df['slope_pl']
        #--------------------------------
        '''


        '''

        # Señal de compra/ventas Reinaldo

        # Calculo de la pendiente del RSI
        #coc = df['rsi_9'].diff()
        #df['rsi_9_slope'] = RAD_TO_DEGREE * coc.astype(float).apply(math.tan)
        #df['rsi_9_diff'] = df['rsi_9'].diff()
        # Calculo señal 1=bajsita, 2=alcista, 0=nada
        #df['rsi_9_signal'] = 0
        #df.loc[(df['rsi_9'] < 30), 'rsi_9_signal'] = 2
        #df.loc[(df['rsi_9'] > 70), 'rsi_9_signal'] = 1
        
        #----------------------------------------------------------------
        #ATR 14
        #atr = ta.atr(df['High'], df['Low'], df['Close'], length=14)

        #df['ohlc4'] = (df['Open'] + df['High'] + df['Low'] + df['Close'])  / 4 

        # Calcular el Cociente entre la diferencia entre el valor y el anterior (eso hace diff) 
        # de una EMA de 55 de OHLC4 / ATR de 14 al cierre 
        #df['ema_slope'] = df['rsi_9'].ewm(span=14, adjust=True).mean() #df['ohlc4'].ewm(span=55, adjust=True).mean()

        #coc = df['ema_slope'].diff() / atr

        # Calcular la inclinación del angulo
        #df['ma_slope'] = RAD_TO_DEGREE * coc.astype(float).apply(math.tan)  

        #df['ma_slope_signal'] = 0
        #df.loc[(df['ma_slope'] > TOP_ANGLE), 'ma_slope_signal'] = 2
        #df.loc[(df['ma_slope'] < BOTTOM_ANGLE), 'ma_slope_signal'] = 1
        '''
        #----------------------------------------------------------------
        

        df=df.tz_localize(None)
        df.to_excel(f'raw_test/{ticker}_{myinterval}_process.xlsx')
        print(df.tail(5))

        # Calculando las señales de compra y venta
        #print ('Calculando señales de buy/sell...')  
        
        #df['TotalSignal'] = df.apply(lambda row: total_signal(df, row.name, 7), axis=1)   
        #df1['totalsignal'] = df1.apply(lambda row: total_signal(df1, row.name, 7), axis=1)
        #df1['totalsignal'] = 0
        
        '''
        #tomar solo la última fila del dataframe
        fecha = df.index[-1]
        cierre = df['Close'][-1]
        volume = df['Volume'][-1]
        ema_21 = df['ema_21'][-1]
        sma_20 = df['sma_20'][-1]
        sma_30 = df['sma_30'][-1]
        ema_150 = df['ema_150'][-1]
        ema_200 = df['ema_200'][-1]
        rsi_9 = df['rsi_9'][-1]
        rsi_14 = df['rsi_14'][-1]
        #buy_rsi_9 = df['buy_rsi_9'][-1]
        #sell_rsi_9 = df['sell_rsi_9'][-1]
        rsi_9_signal = df['rsi_9_signal'][-1]

        


        final_df = final_df.append({'ticker' : ticker, 
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
                                        #'buy_rsi_9' : buy_rsi_9,
                                        #'sell_rsi_9' : sell_rsi_9,
                                        'rsi_9_signal' : rsi_9_signal}, 
                                        ignore_index=True)
   '''     

    except:
        pass

    i += 1



#print(final_df)

#Imprimir aquellos que tienen señal buy/sell
#print(df.query('rsi_9_signal != 0'))
        
print ('Fin.')
