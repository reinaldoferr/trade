import pandas as pd
import numpy as np
import pandas_ta as ta


import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# -----------
# Si no funciona pip install matplotlib usar dentro del codigo de python:
#import pip
#pip.main(["install","matplotlib"])
from matplotlib import pyplot
# -----------


#df = pd.read_csv("raw_test/ADA-USD_4h.csv")
#df = pd.read_csv("raw_test/SOL-USD_4h.csv")
df = pd.read_csv("raw_test/ETH-USD_4h.csv")
df.columns=['time','open', 'high', 'low', 'close', 'volume']
#Check if NA values are in data
df=df[df['volume']!=0]
df.reset_index(drop=True, inplace=True)
df.isna().sum()
#print(df.head(10))

df['rsi'] = df.ta.rsi(length=9)


# Da diferente porque el de padas_ta usa EMA en vez de SMA lo que entendí, 
# el myRSI es más rabioso
def myRSI(price, n=9):
    delta = price['close'].diff()
    dUp, dDown = delta.copy(), delta.copy()
    dUp[dUp < 0] = 0
    dDown[dDown > 0] = 0

    RolUp = dUp.rolling(window=n).mean()
    RolDown = dDown.rolling(window=n).mean().abs()
    
    RS = RolUp / RolDown
    rsi= 100.0 - (100.0 / (1.0 + RS))
    return rsi

#df['my_rsi'] = myRSI(df)

#df.dropna(inplace=True)
#df.reset_index(drop=True, inplace=True)
#print(df.tail(20))

def pivotid(df1, l, n1, n2): #n1 n2 before and after candle l
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0
    
    pividlow=1
    pividhigh=1
    for i in range(l-n1, l+n2+1):
        if(df1.low[l]>df1.low[i]):
            pividlow=0
        if(df1.high[l]<df1.high[i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0

def RSIpivotid(df1, l, n1, n2): #n1 n2 before and after candle l
    
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0

    pividlow=1
    pividhigh=1
    for i in range(l-n1, l+n2+1):
        if(df1.rsi[l]>df1.rsi[i]):
            pividlow=0
        if(df1.rsi[l]<df1.rsi[i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0 
 
df['pivot'] = df.apply(lambda x: pivotid(df, x.name,2,3), axis=1)
df['rsi_pivot'] = df.apply(lambda x: RSIpivotid(df, x.name, 2, 3), axis=1)

#print(df[df.rsi_pivot==1])   
 
def pointpos(x):
    if x['pivot']==1:
        return x['low']-1000e-3
    elif x['pivot']==2:
        return x['high']+1000e-3
    else:
        return np.nan

def RSIpointpos(x):
    if x['rsi_pivot']==1:
        return x['rsi']-2
    elif x['rsi_pivot']==2:
        return x['rsi']+2
    else:
        return np.nan

def DIVRSIpointpos(x):
    if x['divergence']==1:
        return x['rsi']-1
    elif x['divergence']==2:
        return x['rsi']+1
    else:
        return np.nan

def DIVCANDLEpointpos(x):
    if x['divergence']==1:
        return x['low']-1000e-3
    elif x['divergence']==2:
        return x['high']+1000e-3
    else:
        return np.nan
        
df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
df['rsi_pointpos'] = df.apply(lambda row: RSIpointpos(row), axis=1) 
    
  
def divsignal(x, nbackcandles):
    backcandles=nbackcandles 
    candleid = int(x.name)

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    maximRSI = np.array([])
    minimRSI = np.array([])
    xxminRSI = np.array([])
    xxmaxRSI = np.array([])

    for i in range(candleid-backcandles, candleid+1):
        if df.iloc[i].pivot == 1:
            minim = np.append(minim, df.iloc[i].low)
            xxmin = np.append(xxmin, i) #could be i instead df.iloc[i].name
        if df.iloc[i].pivot == 2:
            maxim = np.append(maxim, df.iloc[i].high)
            xxmax = np.append(xxmax, i) # df.iloc[i].name
        if df.iloc[i].rsi_pivot == 1:
            minimRSI = np.append(minimRSI, df.iloc[i].rsi)
            xxminRSI = np.append(xxminRSI, df.iloc[i].name)
        if df.iloc[i].rsi_pivot == 2:
            maximRSI = np.append(maximRSI, df.iloc[i].rsi)
            xxmaxRSI = np.append(xxmaxRSI, df.iloc[i].name)

    if maxim.size<2 or minim.size<2 or maximRSI.size<2 or minimRSI.size<2:
        return 0
    
    slmin, intercmin = np.polyfit(xxmin, minim,1)
    slmax, intercmax = np.polyfit(xxmax, maxim,1)
    slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI,1)
    slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI,1)
    
    
    if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI <-0.1:
        return 1
    elif slmin < -1e-4 and slmax < -1e-4 and slminRSI > 0.1:
        return 2
    else:
        return 0


def divsignal2(x, nbackcandles):
    backcandles=nbackcandles 
    candleid = int(x.name)

    closp = np.array([])
    xxclos = np.array([])
    
    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    maximRSI = np.array([])
    minimRSI = np.array([])
    xxminRSI = np.array([])
    xxmaxRSI = np.array([])

    for i in range(candleid-backcandles, candleid+1):
        closp = np.append(closp, df.iloc[i].close)
        xxclos = np.append(xxclos, i)
        if df.iloc[i].pivot == 1:
            minim = np.append(minim, df.iloc[i].low)
            xxmin = np.append(xxmin, i) #could be i instead df.iloc[i].name
        if df.iloc[i].pivot == 2:
            maxim = np.append(maxim, df.iloc[i].high)
            xxmax = np.append(xxmax, i) # df.iloc[i].name
        if df.iloc[i].rsi_pivot == 1:
            minimRSI = np.append(minimRSI, df.iloc[i].rsi)
            xxminRSI = np.append(xxminRSI, df.iloc[i].name)
        if df.iloc[i].rsi_pivot == 2:
            maximRSI = np.append(maximRSI, df.iloc[i].rsi)
            xxmaxRSI = np.append(xxmaxRSI, df.iloc[i].name)

    slclos, interclos = np.polyfit(xxclos, closp,1)
    
    if slclos > 1e-4 and (maximRSI.size<2 or maxim.size<2):
        return 0
    if slclos < -1e-4 and (minimRSI.size<2 or minim.size<2):
        return 0
# signal decisions here !!!
    if slclos > 1e-4:
        if maximRSI[-1]<maximRSI[-2] and maxim[-1]>maxim[-2]:
            return 1
    elif slclos < -1e-4:
        if minimRSI[-1]>minimRSI[-2] and minim[-1]<minim[-2]:
            return 2
    else:
        return 0

'''
def rsi_divergence(data, lookback_period=10):
    rsi_values = data['rsi']
    divergence_points = []
    for i in range(lookback_period,len(data)-1):
        recent_rsi_values = rsi_values[i-lookback_period:i]
        recent_price_values = data['close'].iloc[i-lookback_period:i]
        if (data['close'].iloc[i] < min(recent_price_values) and rsi_values[i] >= min(recent_rsi_values)+2) or (data['close'].iloc[i] > max(recent_price_values) and rsi_values[i] <= max(recent_rsi_values)-2):
            divergence_points.append[i]
            
    data['divergence'] = False
    data.loc[divergence_points,'divergence'] = True   
    return data
'''

def rsi_divergence(data, lookback_period=10):
    rsi_values = data['rsi']
    data['divergence'] = 0
    divergence_points = []
    for i in range(lookback_period,len(data)-1):
        recent_rsi_values = rsi_values[i-lookback_period:i]
        recent_price_values = data['close'].iloc[i-lookback_period:i]
        # Bullish divergence
        if (data['close'].iloc[i] < min(recent_price_values) and rsi_values[i] >= min(recent_rsi_values)): 
            #data['divergence'].iloc[i] = 2
            data.loc[i,'divergence'] = 2
        # Bearish divergence
        if (data['close'].iloc[i] > max(recent_price_values) and rsi_values[i] <= max(recent_rsi_values)):
            #data['divergence'].iloc[i] = 1
            data.loc[i,'divergence'] = 1
            
    return data

def rsi_divergence_sma(data, lookback_period=3):
    #Para calcular la pendiente
    data['candle_sma'] = ta.sma(data['close'], length=lookback_period)
    data['candle_diff'] = data['candle_sma'].diff(periods=lookback_period)
    data['rsi_sma'] = ta.sma(data['rsi'],length=lookback_period)
    data['rsi_diff'] = data['rsi_sma'].diff(periods=lookback_period)

    return data


def signals(data):
    
    data['signal'] = 0
    
    for i in range(len(df)): #for i in data.index:
        if data['candle_diff'].iloc[i] < 0 and data['rsi_diff'].iloc[i] > 0 and data['divergence'].iloc[i] == 2 and data['rsi'].iloc[i] <= 30:
            #data['signal'].iloc[i] = 2 # Bullish Signal
            data.loc[i,'signal'] = 2 # Bullish Signal
        if data['candle_diff'].iloc[i] > 0 and data['rsi_diff'].iloc[i] < 0 and data['divergence'].iloc[i] == 1 and data['rsi'].iloc[i] >= 70:    
            #data['signal'].iloc[i] = 1 # Bearish Signal
            data.loc[i,'signal'] = 1 # Bearish Signal
        
        
    return data
   
df = rsi_divergence(df,6)
df = rsi_divergence_sma(df,3)
df = signals(df)

#print(df[df['divergence']!=0])
#print(df[115:120])

df_tmp = df[df['signal']!=0]
df_tmp = df_tmp[['time','close','volume','rsi','candle_sma','candle_diff','rsi_sma','rsi_diff','signal']]
print(df_tmp)

df['div_rsi_pointpos'] = df.apply(lambda row: DIVRSIpointpos(row), axis=1) 
df['div_candle_pointpos'] = df.apply(lambda row: DIVCANDLEpointpos(row), axis=1) 

dfpl = df #df[28100:28200]
    
# Grafico de Pivots------------------------------------------------------

fig = make_subplots(rows=2, cols=1)
fig.append_trace(go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close'],
                text=dfpl['time']), row=1, col=1)
fig.append_trace(go.Scatter(
    x=dfpl.index,
    y=dfpl['rsi'],
), row=2, col=1)

fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=4, color="MediumPurple"),
                name="pivot", row=1, col=1)



fig.append_trace(go.Scatter(x=dfpl.index, y=dfpl['rsi']), row=2, col=1)

fig.add_scatter(x=dfpl.index, y=dfpl['rsi_pointpos'], mode="markers",
                marker=dict(size=4, color="MediumPurple"),
                name="rsi_pivot", row=2, col=1)       

#Dibujar los puntos de divervencia
#fig.add_scatter(x=dfpl.index, y=dfpl['div_rsi_pointpos'], mode="markers",
#                marker=dict(size=6, color="Blue"),
#                name="divergence_rsi", row=2, col=1)   

#fig.add_scatter(x=dfpl.index, y=dfpl['div_candle_pointpos'], mode="markers",
#                marker=dict(size=6, color="Red"),
#                name="divergence_candle", row=1, col=1)  
      
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

# entre la 116-119 hay divergnecia





# Grafico de divergencias------------------------------------------------------
'''
backcandles= 60 #backcandles= 60
#ackcandles= 60

#candleid = 8800
candleid = 120 #candleid = 85

maxim = np.array([])
minim = np.array([])
xxmin = np.array([])
xxmax = np.array([])

maximRSI = np.array([])
minimRSI = np.array([])
xxminRSI = np.array([])
xxmaxRSI = np.array([])

for i in range(candleid-backcandles, candleid+1):
    if df.iloc[i].pivot == 1:
        minim = np.append(minim, df.iloc[i].low)
        xxmin = np.append(xxmin, i) #could be i instead df.iloc[i].name
    if df.iloc[i].pivot == 2:
        maxim = np.append(maxim, df.iloc[i].high)
        xxmax = np.append(xxmax, i) # df.iloc[i].name
    if df.iloc[i].rsi_pivot == 1:
        minimRSI = np.append(minimRSI, df.iloc[i].rsi)
        xxminRSI = np.append(xxminRSI, df.iloc[i].name)
    if df.iloc[i].rsi_pivot == 2:
        maximRSI = np.append(maximRSI, df.iloc[i].rsi)
        xxmaxRSI = np.append(xxmaxRSI, df.iloc[i].name)
        
slmin, intercmin = np.polyfit(xxmin, minim,1)
slmax, intercmax = np.polyfit(xxmax, maxim,1)
slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI,1)
slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI,1)

print(slmin, slmax, slminRSI, slmaxRSI)


dfpl = df[candleid-backcandles-5:candleid+backcandles]
fig = make_subplots(rows=2, cols=1)
fig.append_trace(go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close']), row=1, col=1)
fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=4, color="MediumPurple"),
                name="pivot", row=1, col=1)
fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + intercmin, mode='lines', name='min slope'), row=1, col=1)
fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + intercmax, mode='lines', name='max slope'), row=1, col=1)

fig.append_trace(go.Scatter(x=dfpl.index, y=dfpl['rsi']), row=2, col=1)
fig.add_scatter(x=dfpl.index, y=dfpl['rsi_pointpos'], mode="markers",
                marker=dict(size=2, color="MediumPurple"),
                name="pivot", row=2, col=1)
fig.add_trace(go.Scatter(x=xxminRSI, y=slminRSI*xxminRSI + intercminRSI, mode='lines', name='min slope'), row=2, col=1)
fig.add_trace(go.Scatter(x=xxmaxRSI, y=slmaxRSI*xxmaxRSI + intercmaxRSI, mode='lines', name='max slope'), row=2, col=1)

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
'''



#dfpl['div_signal'] = dfpl.apply(lambda row: divsignal(row,30), axis=1)   
#dfpl['div_signal2'] = dfpl.apply(lambda row: divsignal2(row,30), axis=1)

#print(dfpl.tail())
#print(dfpl.loc[dfpl['div_signal'] == 1])
#print(dfpl.loc[dfpl['div_signal2'] == 1])

#print(dfpl.loc[dfpl['div_signal2'] == 1])
#print(dfpl.loc[dfpl['div_signal2'] == 2])
#print(len(dfpl[dfpl.div_signal==2]))
#print(len(dfpl[dfpl.div_signal2==1]))
#print(len(dfpl[dfpl.div_signal2==2]))






