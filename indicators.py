import pandas as pd 
import numpy as np
from utils import gain,loss,is_far_from_level
from charts import chart_ma, chart_supres,chart_fiboretrace,chart_three
from charts import chart_supres0315
from constants import __TOKEN, pattern_names, LS, ID
from patterns import doji, gravestone_doji, dragonfly_doji, longleg_doji, hammer_hanging_man, inv_hammer, spinning_top, marubozu, engulf, engulfing, harami, dark_cloud_cover, piercing_pattern

def calcSupRes0315(df15):    
    # https://medium.com/@patelsaadn/top-5-swing-trading-algorithms-simplified-theory-and-python-implementation-b597156ab8df
    pivots = []
    for df in (df15):
    # for df in (df03, df15):
        pivot_levels = []
        maxi_list = []
        mini_list = []
        for i in range(5, len(df)-5):
            # taking a window of 9 candles
            high_range = df['high'][i-5:i+4]
            current_maxi = high_range.max()
            # if we find a new maximum value, empty the maxi_list 
            if current_maxi not in maxi_list:
                maxi_list = []
            maxi_list.append(current_maxi)
            # if the maximum value remains the same after shifting 5 times
            if len(maxi_list)==5 and is_far_from_level(current_maxi,pivot_levels,df):
                pivot_levels.append((high_range.idxmax(), current_maxi))
            
            low_range = df['low'][i-5:i+5]
            current_mini = low_range.min()
            if current_mini not in mini_list:
                mini_list = []
            mini_list.append(current_mini)
            if len(mini_list)==5 and is_far_from_level(current_mini,pivot_levels,df):
                pivot_levels.append((low_range.idxmin(), current_mini))
        pivots.append(pivot_levels)

    chart_supres0315(pivots, df15, 'supres.jpg','Support and Resistance Levels')

def lastDoji(df):
    df_doji = df.copy()
    df_doji.rename(columns = {'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'}, inplace = True)
    df_doji = doji(df_doji)
    return df_doji.Doji.values[-2]

def patterns(df):
    df_pattern = df.copy()
    df_pattern.rename(columns = {'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'}, inplace = True)
    df_pattern = doji(df_pattern)
    df_pattern = gravestone_doji(df_pattern)
    df_pattern = dragonfly_doji(df_pattern)
    df_pattern = longleg_doji(df_pattern)
    df_pattern = hammer_hanging_man(df_pattern)
    df_pattern = inv_hammer(df_pattern)
    # df_pattern = spinning_top(df_pattern)
    # df_pattern = marubozu(df_pattern)
    # df_pattern = engulf(df_pattern)
    # df_pattern = engulfing(df_pattern)
    # df_pattern = harami(df_pattern)
    df_pattern = dark_cloud_cover(df_pattern)
    df_pattern = piercing_pattern(df_pattern)
    return { col : df_pattern[col].values[-2] for col in df_pattern.columns if col in pattern_names }

def threeSoldiers(df, body=0.05):
    # https://medium.com/geekculture/trading-the-three-white-soldiers-three-black-crows-the-full-guide-9663c5979cfa
    # Three White Soldiers & Three Black Crows
    if df['close'].iloc[-1] > df['open'].iloc[-1] and (df['close'].iloc[-1] - df['open'].iloc[-1]) >= body and df['close'].iloc[-1] > df['close'].iloc[-2] and df['close'].iloc[-2] > df['open'].iloc[-2] and (df['close'].iloc[-2] - df['open'].iloc[-2]) >= body and df['close'].iloc[-2] > df['close'].iloc[-3] and df['close'].iloc[-3] > df['open'].iloc[-3] and (df['close'].iloc[-3] - df['open'].iloc[-3]) >= body and df['close'].iloc[-3] > df['close'].iloc[-4]:            
        chart_three(df, 15, 'three.jpg','Three White Soldiers', '적삼병')
        return 'Three White Soldiers : 적삼병', LS.LONG, ID.THREE_WHITE_SOLDIERS            
    if df['close'].iloc[-1] < df['open'].iloc[-1] and (df['open'].iloc[-1] - df['close'].iloc[-1]) >= body and df['close'].iloc[-1] < df['close'].iloc[-2] and df['close'].iloc[-2] < df['open'].iloc[-2] and (df['open'].iloc[-2] - df['close'].iloc[-2]) >= body and df['close'].iloc[-2] < df['close'].iloc[-3] and df['close'].iloc[-3] < df['open'].iloc[-3] and (df['open'].iloc[-3] - df['close'].iloc[-3]) >= body and df['close'].iloc[-3] < df['close'].iloc[-4]:    
        chart_three(df, 15, 'three.jpg','Three Black Crows', '흑삼병')
        return 'Three Black Crows : 흑삼병', LS.SHORT, ID.THREE_BLACK_CROWS
    
    # Bullish Engulfing & Bearish Engulfing
    if (df['open'].iloc[-2] < df['close'].iloc[-1]) and (df['close'].iloc[-2] > df['open'].iloc[-1]): 
        return 'Bullish Engulfing : 상승장악', LS.LONG, ID.BULLISH_ENGULFING
    if (df['close'].iloc[-2] < df['open'].iloc[-1]) and (df['open'].iloc[-2] > df['close'].iloc[-1]): 
        return 'Bearish Engulfing : 하락장악', LS.SHORT, ID.BEARISH_ENGULFING
    return '', LS.NIL, None

def calcFiboRetrace(df):
    # Calculate the high, low, and close prices
    high = df['high']
    low = df['low']
    # close = df['close']
    # Calculate the range of the price movement
    range_price = high - low
    # Calculate the retracement levels
    retracements = [0,0.236, 0.5, 0.618, 0.786,1]
    # Calculate the retracement levels in terms of price levels
    retracement_levels = []
    for retracement in retracements:
        retracement_level = high - (range_price * retracement)
        retracement_levels.append(retracement_level)
    chart_fiboretrace(retracement_levels)
    

def calcSupRes(df):
    # https://medium.com/@patelsaadn/top-5-swing-trading-algorithms-simplified-theory-and-python-implementation-b597156ab8df
    pivot_levels = []
    maxi_list = []
    mini_list = []
    for i in range(5, len(df)-5):
        # taking a window of 9 candles
        high_range = df['high'][i-5:i+4]
        current_maxi = high_range.max()
        # if we find a new maximum value, empty the maxi_list 
        if current_maxi not in maxi_list:
            maxi_list = []
        maxi_list.append(current_maxi)
        # if the maximum value remains the same after shifting 5 times
        if len(maxi_list)==5 and is_far_from_level(current_maxi,pivot_levels,df):
            pivot_levels.append((high_range.idxmax(), current_maxi))
        
        low_range = df['low'][i-5:i+5]
        current_mini = low_range.min()
        if current_mini not in mini_list:
            mini_list = []
        mini_list.append(current_mini)
        if len(mini_list)==5 and is_far_from_level(current_mini,pivot_levels,df):
            pivot_levels.append((low_range.idxmin(), current_mini))

    chart_supres(pivot_levels, df, 'supres.jpg','Support and Resistance Levels')

def calcMFI(df, n=14):
    high=df['high']
    low=df['low']
    close=df['close']
    volume=df['volume']
    typical_price = (high + low + close)/3
    money_flow = typical_price * volume
    mf_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
    signed_mf = money_flow * mf_sign
    mf_avg_gain = signed_mf.rolling(n).apply(gain, raw=True)
    mf_avg_loss = signed_mf.rolling(n).apply(loss, raw=True)
    df['MFI'] = (100 - (100 / (1 + (mf_avg_gain / abs(mf_avg_loss))))).to_numpy()    
    return df

def calcMACD(df):
    # MACD
    # 시그널선은 일정 기간 동안의 MACD지수 이동평균으로 정의되며 일반적으로 MACD의 9일 지수이동평균이 이용된다. 
    # 즉 12일 동안의 지수이동평균과 26일 동안의 지수이동평균을 구한 후 이들 간의 차이를 다시 9일 동안의 지수이동평균으로 산출하는 것이다. 
    # MACD선과 시그널선이 교차하는 시점이 바로 단기 이동평균과 장기 이동평균간의 차이가 가장 큰 것으로 간주된다. 
    # 그래서 MACD선이 시그널선 위로 올라가게 되면 MACD가 9일 동안의 평균보다 높게 형성되었다는 의미이므로 
    # 매수 신호, 반대로 MACD선이 시그널선 아래로 내려가게 되면 MACD가 9일 동안의 평균보다 낮게 형성되었다는 의미이므로 매도 신호로 해석된다.    
    macd_short, macd_long, macd_signal = 12, 26, 9 #기본값
    df["MACD_short"]=df["close"].ewm(span=macd_short).mean()
    df["MACD_long"]=df["close"].ewm(span=macd_long).mean()
    df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()  
    df["MACD_oscillator"]=df.apply(lambda x:(x["MACD"]-x["MACD_signal"]), axis=1)
    df["MACD_sign"]=df.apply(lambda x: ("Long" if x["MACD"]>x["MACD_signal"] else "Short"), axis=1)
    return df

def calcRSI(df):
    # RSI
    df['chgClose'] = df['close'] - df['close'].shift(1)
    df['chgUp'] = np.where(df['chgClose']>=0, df['chgClose'], 0)
    df['chgDown'] = np.where(df['chgClose'] <0, df['chgClose'].abs(), 0)

    # welles moving average
    df['AU'] = df['chgUp'].ewm(alpha=1/14, min_periods=14).mean()
    df['AD'] = df['chgDown'].ewm(alpha=1/14, min_periods=14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100
    df['RSI_signal'] = df['RSI'].rolling(9).mean()
    # df[['RSI']].tail(n=10)
    return df

def calcMA(df):
    len = df.shape[0]
    # print(f'[calcMA] df.shape[0]:{len}')
    # 이평선 5/10/20/60/120 차트 Shard 구간시
    maIntervals = {'ma5':5,'ma10':10,'ma20':20,'ma60':60,'ma120':120}
    for k, v in maIntervals.items():
        if len<v:
            v = len-10
        df[k] = df['close'].rolling(window=v).mean()
    # print(f'calcMA:\n{df.head(10)}')
    # print(f'calcMA:\n{df.tail(10)}')
    return df

def calcBol(df):
    period = 20
    multiplier = 2
    df['upperBand'] = df['close'].rolling(period).mean() + df['close'].rolling(period).std() * multiplier
    df['lowerBand'] = df['close'].rolling(period).mean() - df['close'].rolling(period).std() * multiplier
    df['%B'] = (df['close'] - df['lowerBand']) / (df['upperBand'] - df['lowerBand'])
    return df

def calcCCI(df):
    df['pt'] = (df['high']+df['low']+df['close'])/3
    df['sma']= df['pt'].rolling(20).mean()
    df['mad']= df['pt'].rolling(20).apply(lambda x: pd.Series(x).mean())
    df['cci'] = (df['pt']-df['sma'])/(0.015*df['mad'])
    return df