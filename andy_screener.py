

# Basado en la estrategia de Andy




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



# Merval 
#merval = ['ALUA.BA', 'BBAR.BA', 'BMA.BA', 'BYMA.BA', 'GGAL.BA', 'SUPV.BA', 'PAMP.BA', 'YPFD.BA', 'VALO.BA', 'CEPU.BA', 'TRAN.BA', 'TXAR.BA', 'LOMA.BA', 'HARG.BA', 'COME.BA', 'CRES.BA', 'TGNO4.BA', 'TGSU2.BA', 'EDN.BA', 'CVH.BA', 'MIRG.BA', 'TECO2.BA']

# Otras Argentinas (Panel General, no Merval)
#otras = ['AGRO.BA', 'OEST.BA', 'AUSO.BA']

# SP500
sp500 = si.tickers_sp500()

# NySE
nyse = si.tickers_dow()

# NASDAQ
nasdaq = si.tickers_nasdaq()

# Ejemplo para eliminar repetidas con un conjunto
tickers = list(set(sp500+nyse+nasdaq))

#tickers = ['AMZN']
#tickers = list(set(nyse))

# Periodo de datos a bajar
start_download = dt.datetime.now()-dt.timedelta(days = 365 )
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
myinterval1 = '1d'
myinterval2 = '1wk'


# Esto se usa para convertir los datos de !H a 4H
ohlc = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}

#Crear un pandas.DataFrame para guardar los valores de los tickets que cumplan ciertas condiciones
#con las columnas 
list_columns = ['ticker','date','close','volume','ema_21_d','sma_30_d','ema_150_d','ema_200_d','rsi_14_d','wma_10_w','wma_30_w','wma_50_w','sma_200_w','rsi_14_w']
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

'''
def my_function(dataframe):
  my_df=dataframe.copy()
  my_df=my_df.drop(0)
  return(my_df)

new_df=my_function(old_df)
print(type(new_df))
'''

    



# Setear las variables de conteo
i = 1
j = len(tickers) 

# Loop por los tickets, bajarlos y luego salvarlos en CSVs
# para levantarlos luego desde allí, pero ya desconectado

for ticker in tickers:
    
    try:
    
        # Download the ticker data
        print(f'Download {ticker} timeframe {myinterval1}...({i} de {j} from {start_download} to {end_download})')
                        
        # Bajar los datos del tickets
        df_d = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=myinterval1, auto_adjust=True)
        #print(df.tail(5))
        
        # Cambio zona horaria
        # Mirar https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
        df_d.index = df_d.index.tz_convert('America/Buenos_Aires')
        #print(df_d.tail(5))

        # Download the ticker data
        print(f'Download {ticker} timeframe {myinterval2}...({i} de {j} from {start_download} to {end_download})')
                        
        # Bajar los datos del tickets
        df_w = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=myinterval2, auto_adjust=True)
        #print(df.tail(5))
        
        # Cambio zona horaria
        # Mirar https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
        df_w.index = df_w.index.tz_convert('America/Buenos_Aires')
        #print(df_w.tail(5))

        df_d["ema_21_d"] = ta.ema(df_d.Close, length=21)  
        df_d["sma_30_d"] = ta.sma(df_d.Close, length=30)       
        df_d["ema_150_d"] = ta.ema(df_d.Close, length=150)        
        df_d["ema_200_d"] = ta.ema(df_d.Close, length=200)  
        df_d["rsi_14_d"] = ta.rsi(df_d.Close, length=14)
        
        #atr = ta.adx(df['High'], df['Low'], df['Close'], length = 14)
        #df = df.join(atr)

        macd = ta.macd(df_d['Close'], fast=12, slow=26, signal=9)
        df_d['macd_d'] = macd['MACD_12_26_9']
        df_d['macd_signal_line_d'] = macd['MACDs_12_26_9']
        df_d['macd_hist_d'] = macd['MACDh_12_26_9']
    
        df_w["wma_10_w"] = ta.wma(df_w.Close, length=10)  
        df_w["wma_30_w"] = ta.wma(df_w.Close, length=30) 
        df_w["wma_50_w"] = ta.wma(df_w.Close, length=50) 
        df_w["sma_200_w"] = ta.sma(df_w.Close, length=200) 
        df_w["rsi_14_w"] = ta.rsi(df_w.Close, length=14)

        macd = ta.macd(df_w['Close'], fast=12, slow=26, signal=9)
        df_w['macd_w'] = macd['MACD_12_26_9']
        df_w['macd_signal_line_w'] = macd['MACDs_12_26_9']
        df_w['macd_hist_w'] = macd['MACDh_12_26_9']

        '''
        #---------------
        # Cruce de precio con la SMA 30 Andy
        df['andy_sma_30_signal'] = 0
        df.loc[(df['sma_30'] < df["Close"]), 'andy_sma_30_signal'] = 2
        df.loc[(df['sma_30'] > df["Close"]), 'andy_sma_30_signal'] = 1
        df['andy_ema_21_signal'] = 0
        df.loc[(df['ema_21'] < df["Close"]), 'andy_ema_21_signal'] = 2
        df.loc[(df['ema_21'] > df["Close"]), 'andy_ema_21_signal'] = 1
        #---------------

        # Otras Medias con ejemplo de cruce 
        df['sma_10'] = ta.sma(df['Close'],length=10)
        df['sma_50'] = ta.sma(df['Close'],length=50)
        df['sma_200'] = ta.sma(df['Close'],length=200)
        df['10_cross_30'] = np.where(df['sma_10'] > df['sma_30'], 1, 0)
        df['abv_50'] = np.where((df['sma_30']>df['sma_50'])&(df['sma_10']>df['sma_50']), 1, 0)
    
        df['abv_200'] = np.where((df['sma_30']>df['sma_200'])&(df['sma_10']>df['sma_200'])&(df['sma_50']>df['sma_200']), 1, 0)


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
        

        #df=df.tz_localize(None)
        #df.to_excel(f'raw_test/{ticker}_{myinterval}_process.xlsx')
        #print(df.tail(5))

        # Calculando las señales de compra y venta
        #print ('Calculando señales de buy/sell...')  
        
        #df['TotalSignal'] = df.apply(lambda row: total_signal(df, row.name, 7), axis=1)   
        #df1['totalsignal'] = df1.apply(lambda row: total_signal(df1, row.name, 7), axis=1)
        #df1['totalsignal'] = 0
        
        
        #tomar solo la última fila del dataframe
        fecha = df_d.index[-1]
        cierre = df_d['Close'].iloc[-1]
        volume = df_d['Volume'].iloc[-1]
        ema_21_d = df_d['ema_21_d'].iloc[-1]
        sma_30_d = df_d['sma_30_d'].iloc[-1]
        ema_150_d = df_d['ema_150_d'].iloc[-1]
        ema_200_d = df_d['ema_200_d'].iloc[-1]
        rsi_14_d = df_d['rsi_14_d'].iloc[-1]
        wma_10_w = df_w['wma_10_w'].iloc[-1]
        wma_30_w = df_w['wma_30_w'].iloc[-1]
        wma_50_w = df_w['wma_50_w'].iloc[-1]
        sma_200_w = df_w['sma_200_w'].iloc[-1]
        rsi_14_w = df_w['rsi_14_w'].iloc[-1]
        
        #print(f'ticker: {ticker}, Cierre: {cierre}, Fecha: {fecha}, volume: {volume}, ema_21_d: {ema_21_d}, sma_30_d: {sma_30_d}, ema_150_d: {ema_150_d}, ema_200_d: {ema_200_d}, rsi_14_d: {rsi_14_d}, wma_10_w: {wma_10_w}, wma_30_w: {wma_30_w}, wma_50_w: {wma_50_w}, sma_200_w: {sma_200_w}, rsi_14_w: {rsi_14_w}')

        'ticker','date','close','volume','ema_21_d','sma_30_d','ema_150_d','ema_200_d','rsi_14_d','wma_10_w','wma_30_w','wma_50_w','sma_200_w','rsi_14_w'
        #df = pd.concat([df, pd.DataFrame.from_records([{ 'a': 1, 'b': 2 }])])
        final_df = final_df.append({'ticker' : ticker, 
                                    'date' : fecha,
                                        'close' : cierre,
                                        'volume' : volume,
                                        'ema_21_d' : ema_21_d,
                                        'sma_30_d' : sma_30_d,
                                        'ema_150_d' : ema_150_d,
                                        'ema_200_d' : ema_200_d,
                                        'rsi_14_d' : rsi_14_d,
                                        'wma_10_w' : wma_10_w,
                                        'wma_30_w' : wma_30_w,
                                        'wma_50_w' : wma_50_w,
                                        'sma_200_w' : sma_200_w,
                                        'rsi_14_w' : rsi_14_w}, 
                                        ignore_index=True)
     

    except:
        pass

    i += 1



#print(final_df)
#Cortar columnas
final_df=final_df[['ticker','date','close','volume','rsi_14_d','rsi_14_w']]
#print(final_df)
#Filtrar Columnas
print(final_df.query('rsi_14_d < 30 or rsi_14_d > 70 or rsi_14_w < 30 or rsi_14_w > 70'))
#Imprimir aquellos que tienen señal buy/sell
#print(df.query('rsi_9_signal != 0'))
        
print ('Fin.')
