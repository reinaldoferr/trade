
#
# Código basado en el video de youtube https://www.youtube.com/watch?v=C3bh6Y4LpGs&t=214s
# Mezclé luego con otro video donde explican como funciona el backtesting https://www.youtube.com/watch?v=e4ytbIm2Xg0
#
#
# Usa una EMA rápida de 30 y una lenta de 50 para determinar la tendencia
# Luego usa bandas de Bollinger, si el precio cruza las bandas de Bollinger acciona.
#
# Cosas que me fué pidiendo installar y que corrí en la Terminal:
# pip install pandas
# pip install pandas_ta
# pip install pandas_datareader
# pip install yahoo-finance
# pip install yahoo-fin
# pip install yfinance
# pip install pyarrow
# pip install XlsxWriter
# pip install plotly
# pip install backtest
# python.exe -m pip install --upgrade pip
# pip install backtesting
# pip install seaborn


import pandas as pd
import pandas_ta as ta

from tqdm import tqdm # es para mostrar el progreso de las tareas

# Para la parte grafica
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

import numpy as np

# Leer el archivo de datos, podría ser un .CSV o directamente la bajada de yahoo finance
# ORIGINAL--> df = pd.read_csv("raw_data/EURUSD_Candlestick_5M_30.09.2019-30.09.2022.csv")
df = pd.read_csv("raw_data/AAPL_Candlestick_1d_23.01.2023-22.01.2024.csv")
#df = pd.read_csv("raw_data/AMZN_Candlestick_5m_24.11.2023-22.01.2024.csv")
#df = pd.read_csv("raw_data/AAPL_Candlestick_5m_24.11.2023-22.01.2024.csv")
#print (df)

# Formateo de las fechas en el formato correcto
print ('Formateando las fechas...')
df["Gmt time"]=df["Gmt time"].str.replace(".000","")
df['Gmt time']=pd.to_datetime(df['Gmt time'],format='%d.%m.%Y %H:%M:%S')
df=df[df.High!=df.Low]
df.set_index("Gmt time", inplace=True)

# Calculo de las EMAs, RSI, Bollinger y ATR
# Usa el cruce de medias 30/50 para determinar la tendencia (alcista/bajista)
print ('Calculando EMAs / RSI...')
df["EMA_slow"]=ta.ema(df.Close, length=50)
df["EMA_fast"]=ta.ema(df.Close, length=30)
df['RSI']=ta.rsi(df.Close, length=10)

# Calculo de bandas de Bollinger
my_bbands = ta.bbands(df.Close, length=15, std=1.5)

# Calculo del ATR para establecer el stop-loss y el take-profit
print ('Calculando ATR...')
df['ATR']=ta.atr(df.High, df.Low, df.Close, length=7)

# Juntar lo que tiene ya el datareader con el datareader "my_bbands" bandas de bollinguer
df=df.join(my_bbands) 
#print (df.head(2))
#print (df.tail(2))


# Función que determina la tendencia
# Señales con la EMA (tendencia), dependiendo de la cantidad de Velas
# que querramos tomar (en backcandles)
def ema_signal(df, current_candle, backcandles):
    df_slice = df.reset_index().copy()
    # Get the range of candles to consider
    start = max(0, current_candle - backcandles)
    end = current_candle
    relevant_rows = df_slice.iloc[start:end]

    # Check if all EMA_fast values are below EMA_slow values
    # Detectar la tendencia, 1 = bajista, 2 = alcista, sino 0
    if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
        return 1 # Bajista
    elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
        return 2 # Alcista
    else:
        return 0 # Sin tendencia


# Cantidad de registros a procesar (arbitrario)
df=df[-1000:-1]

# Esto es para mostrar el proceso en la terminal, así no parece que est+a colgado
tqdm.pandas()
df.reset_index(inplace=True)
print ('Calculando la tendencia...')
# EMASignal debería llamarse TrendSignal---> Alcista/Bajista
# Exije que haya al menos 7 velas seguidas en tendencia Alcista/Bajista para determinar la tendencia
# se puede correr en vez de progress_apply, apply directamente no muestra nada y es más rápido.
#df['EMASignal'] = df.progress_apply(lambda row: ema_signal(df, row.name, 7) , axis=1) #if row.name >= 20 else 0
df['EMASignal'] = df.apply(lambda row: ema_signal(df, row.name, 7) , axis=1)
#print (df.head(2))
#print (df.tail(2))


# Función que determina si la tendencia es:
# 1 = bajista y ademas el cierre esté por encima de la banda de bollinger (devuelve 2), 
# 2 = alcista y ademas el cierre esté por debajo de la banda de bollinger (devuelve 1),
# 0 si nada.
def total_signal(df, current_candle, backcandles):
    if (ema_signal(df, current_candle, backcandles)==2
        and df.Close[current_candle]<=df['BBL_15_1.5'][current_candle]
        #and df.RSI[current_candle]<60
        ):
            return 2 #long signal (me parece que es al revés) 
    if (ema_signal(df, current_candle, backcandles)==1
        and df.Close[current_candle]>=df['BBU_15_1.5'][current_candle]
        #and df.RSI[current_candle]>40
        ):
    
            return 1 #short signal (me parece que es al revés)
    return 0

# Calculando las señales de compra y venta
print ('Calculando señales de buy/sell...')        
#df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name, 7), axis=1)
df['TotalSignal'] = df.apply(lambda row: total_signal(df, row.name, 7), axis=1)
#print(df[df.TotalSignal != 0].tail(5))


# Me parece que calcula posiciones en el gráfico donde poner las señales de 
# entrada/salida, un poco debajo o encima de los valores de cierre
def pointpos(x):
    if x['TotalSignal']==2:
        return x['Low']-1e-3
    elif x['TotalSignal']==1:
        return x['High']+1e-3
    else:
        return np.nan

print ('Calculando puntos de entrada...')
df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
#print(df[df.TotalSignal != 0].tail(5))


# Todo este código es para la parte gráfica
print ('Dibujando...')
st=100
dfpl = df[st:st+350]
#dfpl.reset_index(inplace=True)
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close']),

                go.Scatter(x=dfpl.index, y=dfpl['BBL_15_1.5'], 
                           line=dict(color='red', width=1), 
                           name="BBL"),
                go.Scatter(x=dfpl.index, y=dfpl['BBU_15_1.5'], 
                           line=dict(color='green', width=1), 
                           name="BBU"),
                go.Scatter(x=dfpl.index, y=dfpl['EMA_fast'], 
                           line=dict(color='gray', width=1), 
                           name="EMA_fast"),
                go.Scatter(x=dfpl.index, y=dfpl['EMA_slow'], 
                           line=dict(color='blue', width=2), 
                           name="EMA_slow")])

fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=5, color="MediumPurple"),
                name="entry")

fig.show()

def SIGNAL():
    return df.TotalSignal

from backtesting import Strategy
from backtesting import Backtest

class MyStrat(Strategy):
    mysize = 3000
    slcoef = 1.1
    TPSLRatio = 1.5
    rsi_length = 16
    
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        #df['RSI']=ta.rsi(df.Close, length=self.rsi_length)

    def next(self):
        super().next()
        slatr = self.slcoef*self.data.ATR[-1]
        TPSLRatio = self.TPSLRatio

        # if len(self.trades)>0:
        #     if self.trades[-1].is_long and self.data.RSI[-1]>=90:
        #         self.trades[-1].close()
        #     elif self.trades[-1].is_short and self.data.RSI[-1]<=10:
        #         self.trades[-1].close()
        
        if self.signal1==2 and len(self.trades)==0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr*TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        elif self.signal1==1 and len(self.trades)==0:         
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr*TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)

# Configurar el Backtest
print ('Ejecutando Backtest...')
bt = Backtest(df, MyStrat, cash=250, margin=1/30, commission=0.00)

# Ejecutar/correr, guardar los resultados en stats
#stats = bt.run()

# Ejecutar con optimizacion
stats, heatmap = bt.optimize(slcoef=[i/10 for i in range (10,21)],
                             TPSLRatio=[i/10 for i in range(10,21)],
                             maximize='Return [%]', max_tries=300, 
                             random_state=0,
                             return_heatmap=True)
# imprimir los resultados
print(stats)
# Dibujar el backtest
bt.plot()

# Parte grafica de la estadistica
import seaborn as sns
import matplotlib.pyplot as plt

#Convert multi-index serie to dataframe
print ('Optimización grafica...')
heatmap_df = heatmap.unstack()
plt.figure(figsize=(10,8))
sns.heatmap(heatmap_df, annot=True, cmap='viridis',fmt='.0f')
plt.show()

print ('Fin.')

