# Esto baja de forma simple los archivos de datos similar al ejemplo que venía en youTube
# que sacaba de Dukascopy
# EURUSD_Candlestick_5_M_ASK_30.09.2019-30.09.2022.csv
#
# Exporta convirtiendo la fecha en el mismo formato

import os
import pandas as pd  
import pandas_ta as ta 
import pandas_datareader as web
import datetime as dt
from yahoo_fin import stock_info as si
import yfinance as yf # esta es por si hay que sacarlo en un periodo que no sea diario

# Periodo de datos a bajar
# Intervalo 5m --> se pueden descargar solo  60 días (ultimos 60 dias)
interval = '1h'
ticker = 'SOL-USD'
#start_download = dt.datetime(2023,1,1)
start_download = dt.datetime.now()-dt.timedelta(days = 15)
end_download = dt.datetime.now()-dt.timedelta(days = 1)


# Download
df = yf.Ticker(ticker).history(start=start_download, end=end_download, interval=interval, auto_adjust=True)
print(df.tail(5))

# Esto quita la zona horaria, pero no la traslada al pais de donde estaría abriendo los datos
df.index = df.index.tz_localize(None)
print(df.tail(5))

# Formato de la fecha (se puede cambiar / por - o por . cambiar el orden, etc.)
df.index = pd.to_datetime(df.index, format = '%Y/%m/%d %H:%M:%S').strftime('%d.%m.%Y %H:%M:%S.000')
print(df.tail(5))

# Esto le quita la zona horario pero sumando o restando lo que corresponde
#df.index = df.index.tz_convert(None)
#print(df.tail(5))

#Exportar a .csv
start=start_download.strftime('%d.%m.%Y')
end=end_download.strftime('%d.%m.%Y')

df.to_csv(f'raw_data/{ticker}_Candlestick_{interval}_{start}-{end}.csv',index_label='Gmt time')