'''
App para bajar todos los datos de stock en CSV
a la carpeta raw_data

File name: download.py

'''

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
#tickers = ['ALUA.BA', 'PAMP.BA', 'YPFD.BA','LOMA.BA']
tickers = ['AMZN']

# Periodo de datos a bajar
start_download = dt.datetime(2023,1,1)
end_download = dt.datetime.now() #-dt.timedelta(days = 5)

# Intervalo de los datos 1m --> 1 minuto, 1h --> 1 hora
#interval = ['1m','2m','5m','15m','30m','60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
interval = ['1d']

# Verificar si existe la carpeta en el disco donde se guardarán los archivos, sino la crea.
if not (os.path.exists('raw_data')):
    print ('Creado carpeta raw_data')
    os.mkdir('raw_data')
  
# Setear las variables de conteo
i = 1
j = len(tickers) * len(interval)

# Loop por los tickets, bajarlos y luego salvarlos en CSVs
# para levantarlos luego desde allí (desconectado)
'''
for ticker in tickers:
    
    for myinterval in interval:

        try:
        
            
            # Download the ticker data
            print(f'Download {ticker} timeframe {myinterval}...({i} de {j})')
                  

            if myinterval == '1m':
                start_download = dt.datetime.now()-dt.timedelta(days=6)    
            elif myinterval == '2m' or myinterval == '5m' or myinterval == '15m' or myinterval == '30m' or myinterval == '90m':
                start_download = dt.datetime.now()-dt.timedelta(days=58)
            elif myinterval == '60m'  or myinterval == '1h':
                start_download = dt.datetime.now()-dt.timedelta(days=729)
            elif myinterval == '':
                myinterval == '1d'
                start_download = dt.datetime(1980,1,1)
            else:
                start_download = dt.datetime(1980,1,1)
            
             # Bajar los datos del tickets
            df = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=myinterval)
            print (df)

            # Redondeo
            df = df.round({'Open':4, 'High':4, 'Low':4, 'Close':4, 'Volume':1, 'Dividends':1, 'Stock Splits':1})


            #print(df.tail(3))
            #df.index.tz_convert(None)
            # print(df.index.tz_convert(None))
            #print(df.index.tz_localize(None))
            #df.set_index(df.index.tz_localize(None))

            
            # ---
            # Volver a salvar el archivo con la info nueva
            df.to_csv(f'raw_data/{ticker}_{myinterval}.csv',index_label=False)
            # ---


            # Export data into raw_data folder
            print(f'Exportar a CSV raw_data/{ticker}_{myinterval} desde el {start_download}...')
            #df.to_csv(f'raw_data/{ticker}_{myinterval}.csv')
        
           
        except:
            pass

        i += 1

'''


# Setear las variables de conteo
i = 1
j = len(tickers) * len(interval)

# Leer los tickets desde el CSV
for ticker in tickers:
    for myinterval in interval:
        try:

            df1 = pd.read_csv(f'raw_data/{ticker}_{myinterval}.csv')
        except:
            pass

        i += 1


# Calculo de Emas, SMA, RSIs
df1["EMA_21"]=ta.ema(df1.Close, length=21)        
df1["SMA_30"]=ta.sma(df1.Close, length=30) 
df1["EMA_150"]=ta.ema(df1.Close, length=150)   
df1["EMA_200"]=ta.ema(df1.Close, length=200)   

# Señales de compras
df1.loc[(df1['Close'] > df1['EMA_21']), 'Buy_21'] = 'Yes'
df1.loc[(df1['Close'] <= df1['EMA_21']), 'Buy_21'] = 'No'
df1.loc[(df1['Close'] > df1['SMA_30']), 'Buy_30'] = 'Yes'
df1.loc[(df1['Close'] <= df1['SMA_30']), 'Buy_30'] = 'No'

# Señales de venta
df1.loc[(df1['Close'] < df1['EMA_21']), 'Sell_21'] = 'Yes'
df1.loc[(df1['Close'] >= df1['EMA_21']), 'Sell_21'] = 'No'
df1.loc[(df1['Close'] < df1['SMA_30']), 'Sell_30'] = 'Yes'
df1.loc[(df1['Close'] >= df1['SMA_30']), 'Sell_30'] = 'No'


#df1.to_csv(f'raw_data/{ticker}_{myinterval}_process.csv',index_label=False)
#file = dt.datetime.now().strftime("%Y_%m_%d") + '_rsi_data_' + ticker + '.xlsx'
#file = dt.datetime.now().strftime("%Y_%m_%d") + '_rsi_data.xls'
df1.to_excel(f'raw_data/{ticker}_{myinterval}_process.xlsx')

print (df1)
print ('Fin.')

'''
# Read data from csv file. Set the index to the correct column
# (dates column)
ticker = 'ALUA.BA'
print(f'Read {ticker}...')
df = pd.read_csv(f'raw_data/{ticker}.csv', parse_dates=True, index_col=0)
print(df.head(5))
print(df.tail(5))

# Verify type of index column
print(type(df))
print(type(df.index))
'''



"""
import yfinance as yf

msft = yf.Ticker("MSFT")

# get stock info
msft.info

# get historical market data
hist = msft.history(period="max")

# show actions (dividends, splits)
msft.actions

# show dividends
msft.dividends

# show splits
msft.splits

# show financials
msft.financials
msft.quarterly_financials

# show major holders
msft.major_holders

# show institutional holders
msft.institutional_holders

# show balance sheet
msft.balance_sheet
msft.quarterly_balance_sheet

# show cashflow
msft.cashflow
msft.quarterly_cashflow

# show earnings
msft.earnings
msft.quarterly_earnings

# show sustainability
msft.sustainability

# show analysts recommendations
msft.recommendations

# show next event (earnings, etc)
msft.calendar

# show all earnings dates
msft.earnings_dates

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
msft.isin

# show options expirations
msft.options

# show news
msft.news

# get option chain for specific expiration
opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts






import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials

yahoo_financials = YahooFinancials('AAPL')
data = yahoo_financials.get_historical_price_data(start_date='2019-01-01', 
                                                  end_date='2019-12-31', 
                                                  time_interval='weekly')
aapl_df = pd.DataFrame(data['AAPL']['prices'])
aapl_df = aapl_df.drop('date', axis=1).set_index('formatted_date')
aapl_df.head()

"""



"""
import yfinance as yf

data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = "SPY",

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = "7d",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "1m",

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )

print(data)
"""