import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import seaborn as sns
from mplfinance.original_flavor import candlestick_ohlc
import numpy as np
import pandas as pd
from scipy.stats import linregress
# from utils import is_far_from_level,gain,loss,send_msg,
from utils import send_photo
from constants import __TOKEN,__chat_id #,intervals,symbol

def chart_supres0315(pivots, df15, fname, caption): 
    fig = plt.figure(figsize=(10, 7))
    
    # levels = pivots[0]
    # df = df03
    # ax = fig.add_subplot(2, 1, 1)
    # candlestick_ohlc(ax, df.values, width=1/(3*60*1), colorup='deepskyblue', colordown='red', alpha=0.8)
    # ax.set_xticklabels([])
    # ax.set_xticks([])
    # ax.axes.get_xaxis().set_visible(False)
    # for level in levels:
    #     plt.hlines(level[1], xmin=df['date'][level[0]], xmax=max(df['date']), colors='cadetblue', linestyle='--')
    # plt.plot(df['upperBand'], 'r')
    # plt.plot(df['lowerBand'], 'b')
    # plt.title('Price Chart(3m)')
    # plt.plot(df['close'], label='Close price')
    # plt.legend()
    # plt.title("Bollinger (Bar 3, 15)\nETHUSDT_UMCBL Support and Resistance(03m)")

    levels = pivots[1]
    df = df15
    ax = fig.add_subplot(1, 1, 1)
    # ax = fig.add_subplot(2, 1, 2)
    candlestick_ohlc(ax, df.values, width=1/(3*60*1), colorup='lightsteelblue', colordown='red', alpha=0.8)
    ax.set_xticklabels([])
    ax.set_xticks([])
    ax.axes.get_xaxis().set_visible(False)
    for level in levels:
        plt.hlines(level[1], xmin=df['date'][level[0]], xmax=max(df['date']), colors='violet', linestyle='--')
    plt.plot(df['upperBand'], 'r')
    plt.plot(df['lowerBand'], 'b')
    plt.title('Price Chart(15m)')
    plt.plot(df['close'], label='Close price')
    plt.legend()
    plt.title("Bollinger (Bar 3, 15m)\nETHUSDT_UMCBL Support and Resistance(15m)")

    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.close(fig)
    plt.clf()
    send_photo(__TOKEN,__chat_id,fname,caption)

def plot_updntrends(df_doji):
    df_doji['Number'] = np.arange(df_doji.shape[0])+1    
    df_high = df_low = df_rsi = df_doji.copy()
    while len(df_high)>2:
        slope, intercept, _, _, _ = linregress(x=df_high['Number'], y=df_high['high'])
        df_high = df_high.loc[df_high['high'] > slope * df_high['Number'] + intercept] 
    if len(df_high)<2:
        df_high = pd.concat([df_high,pd.DataFrame(df_doji.iloc[-1]).transpose()],axis=0,ignore_index = False)
    slope, intercept, _, _, _ = linregress(x=df_high['Number'], y=df_high['close'])
    df_doji['Uptrend'] = slope * df_high['Number'] + intercept
    # print(f'df_high: slope={slope},intercept={intercept}')
    
    while len(df_low)>2:
        slope, intercept, _, _, _ = linregress(x=df_low['Number'], y=df_low['low'])
        df_low = df_low.loc[df_low['low'] < slope * df_low['Number'] + intercept]
    if len(df_low)<2:
        df_low = pd.concat([df_low,pd.DataFrame(df_doji.iloc[-1]).transpose()],axis=0,ignore_index = False)
    slope, intercept, _, _, _ = linregress(x=df_low['Number'], y=df_low['close'])
    df_doji['Downtrend'] = slope * df_low['Number'] + intercept
    # print(f'df_low: slope={slope},intercept={intercept}')
    
    while len(df_rsi)>2:
        slope, intercept, _, _, _ = linregress(x=df_rsi['Number'], y=df_rsi['RSI'])
        df_rsi = df_rsi.loc[df_rsi['RSI'] < slope * df_rsi['Number'] + intercept]
    slope, intercept, _, _, _ = linregress(x=df_rsi['Number'], y=df_rsi['RSI'])
    df_doji['RSItrend'] = slope * df_rsi['Number'] + intercept
    # print(f'df_rsi: slope={slope},intercept={intercept}')

    fig, (ax1,ax2) = plt.subplots(2)
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    xdate = [x.date() for x in df_doji.index]
    quotes = list(map(
        lambda x: x[1], 
        (df_doji
        .reset_index()
        .rename(columns={'date': 'time'})
        .assign(time=lambda df_doji: df_doji['time'].map(mpl_dates.date2num))
        .iterrows())))

    candlestick_ohlc(ax1, quotes[:], width=1/(3*60*1), colorup='green', colordown='red', alpha=0.8)

    ax1.xaxis_date()
    ax1.xaxis.set_major_locator(mpl_dates.HourLocator(interval = 1))

    df_up = df_doji[df_doji.Uptrend.notna()]
    df_dn = df_doji[df_doji.Downtrend.notna()]
    df_rs = df_doji[df_doji.RSItrend.notna()]
    ax11 = ax1.twiny() # ax2 and ax1 will have common y axis and different x axis, twiny
    ax11.plot(df_up.Number, df_up.Uptrend, label="uptrend")
    ax11.plot(df_dn.Number, df_dn.Downtrend, label="downtrend")

    ax2.plot(df_doji.RSI)
    ax22 = ax2.twiny()
    ax22.plot(df_rs.RSItrend, label="RSI trend")

    fig.autofmt_xdate()  
    fig.tight_layout()
    plt.grid()
    plt.legend()
    fname='trends.jpg'
    caption = f'Uptrend and Downtrend on the pattern'
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.clf()
    plt.close(fig)                       
    send_photo(__TOKEN,__chat_id,fname,caption)

def heikin_ashi(df):    
    ha_close = (df['open'] + df['close'] + df['high'] + df['low']) / 4    
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
    for close in ha_close[:-1]:
        ha_open.append((ha_open[-1] + close) / 2)    
    ha_open = np.array(ha_open)
    elements = df['high'], df['low'], ha_open, ha_close
    ha_high, ha_low = np.vstack(elements).max(axis=0), np.vstack(elements).min(axis=0)    
    df['open']=ha_open
    df['high']=ha_high
    df['low']=ha_low
    df['close']=ha_close
    return df 

def plot_ha_candlestick(df, size=(16,9)):
    fig, ax = plt.subplots()
    fig.set_size_inches(size)
    quotes = list(map(
        lambda x: x[1], 
        (df
         .reset_index()
         .rename(columns={'date': 'time'})
         .assign(time=lambda df: df['time'].map(mpl_dates.date2num))
         .iterrows())))
    candlestick_ohlc(ax, quotes, width=1/(3*60*1), colorup='green', colordown='red', alpha=0.8)
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mpl_dates.HourLocator(interval = 1) )
    fname='ha.jpg'
    caption = 'Heikin-Ashi'
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.clf()
    plt.close(fig)                       
    send_photo(__TOKEN,__chat_id,fname,caption)

def chart_three(df, window, fname, title, caption):
    Data = np.array(df)
    # plt.rc('font', family='NanumMyeongjo')
    fig, _ = plt.subplots(figsize=(16, 9))
    Chosen = Data[-window:, ]  
    for i in range(len(Chosen)):
      plt.vlines(x = i, ymin = Chosen[i, 2], ymax = Chosen[i, 1], color = 'black', linewidth = 2)       
      if Chosen[i, 3] > Chosen[i, 0]:
        color_chosen = 'blue'
        plt.vlines(x = i, ymin = Chosen[i, 0], ymax = Chosen[i, 3], color = color_chosen, linewidth = 24)        
      if Chosen[i, 3] < Chosen[i, 0]:
        color_chosen = 'red'
        plt.vlines(x = i, ymin = Chosen[i, 3], ymax = Chosen[i, 0], color = color_chosen, linewidth = 24)            
      if Chosen[i, 3] == Chosen[i, 0]:
        color_chosen = 'black'
        plt.vlines(x = i, ymin = Chosen[i, 3], ymax = Chosen[i, 0], color = color_chosen, linewidth = 24)  
    plt.axis('off')      
    plt.grid()
    plt.title(title)    
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.close(fig)
    plt.clf()
    send_photo(__TOKEN,__chat_id,fname,caption)

def chart_mfi(df):
    fig = plt.figure(figsize=(10, 7))
    # Define position of 1st subplot
    ax = fig.add_subplot(3, 1, 1)
    # Set the title and axis labels
    plt.title('Price Chart')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.plot(df['close'], label='Close price')
    # Add a legend to the axis
    plt.legend()
    # Define position of 2nd subplot
    bx = fig.add_subplot(3, 1, 2)
    # Set the title and axis labels
    plt.title('Money flow index')
    plt.xlabel('Date')
    plt.ylabel('MFI values')
    plt.plot(df['MFI'], 'm', label='MFI')
    plt.axhline(80, 0, 1, color='red', linestyle='-', linewidth=1)
    plt.axhline(20, 0, 1, color='red', linestyle='-', linewidth=1)
    # Add a legend to the axis
    plt.legend()
    # Define position of 3nd subplot
    bx = fig.add_subplot(3, 1, 3)
    # Set the title and axis labels
    plt.title('%B')
    plt.xlabel('Date')
    plt.ylabel('%B values')
    plt.plot(df['%B'], 'm', label='%B')
    plt.axhline(0.8, 0, 1, color='red', linestyle='-', linewidth=1)
    plt.axhline(0.2, 0, 1, color='red', linestyle='-', linewidth=1)
    # Add a legend to the axis
    plt.legend()
    plt.tight_layout()   
    fname='MFI.jpg'
    caption = 'MFI and %B'
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.clf()
    plt.close(fig)                       
    send_photo(__TOKEN,__chat_id,fname,caption)
    
def chart_fiboretrace(retracement_level):
    # Plot the Fibonacci retracement levels
    fig = plt.figure(figsize=(15, 8), tight_layout=False)
    # plt.figure(figsize=(15,8))
    # for i, retracement_level in enumerate(retracement_levels):
    # plt.axhline(retracement_level[4], linestyle='--', label=f'{retracements[4]*100}%')
    plt.axhline(retracement_level[5], color="limegreen", linestyle="--", label="100%")
    plt.axhline(retracement_level[4], color="slateblue", linestyle="--", label="78.6%")
    plt.axhline(retracement_level[3], color="mediumvioletred", linestyle="--", label="61.8%")
    plt.axhline(retracement_level[2], color="gold", linestyle="--", label="50%")
    plt.axhline(retracement_level[1], color="darkturquoise", linestyle="--", label="23.6%")
    plt.axhline(retracement_level[0], color="lightcoral", linestyle="--", label="0%")
    plt.legend()
    plt.title('Fibonacci Retracement Levels')
    plt.xlabel('date')
    plt.ylabel('close')
    fname='Fibo.jpg'
    caption = 'Fibonacci Retracement Levels on every 15mins'
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.close(fig)
    plt.clf()
    send_photo(__TOKEN,__chat_id,fname,caption)

def chart_ma(x,ys,lbls,fname,caption):
    ls=['k-' ,'r--','m-.','g:' ,'c.-','go--','r','b']
    fig = plt.figure(figsize=(5, 3), tight_layout=False)
    sns.set_style('darkgrid') # darkgrid, white grid, dark, white and ticks
    sns.color_palette('deep')                        
    plt.rc('axes',  titlesize=11)    # fontsize of the axes title
    plt.rc('axes',  labelsize=11)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
    plt.rc('legend',fontsize =10)    # legend fontsize
    plt.rc('font', size=10)    
    for y,lbl,l in zip(ys,lbls,ls):
        plt.plot(x, y, l, label=lbl)   
    plt.legend()
    plt.axis('off')        
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.close(fig)
    plt.clf()
    send_photo(__TOKEN,__chat_id,fname,caption)

def chart_supres(levels, df, fname, caption):    
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.xaxis.set_major_locator(mpl_dates.HourLocator(interval = 1))
    # set 5 seconds
    candlestick_ohlc(ax, df.values, width=1/(3*60*1), colorup='blue', colordown='red', alpha=0.8)
    
    # adjust x axis format
    date_format = mpl_dates.DateFormatter('%d %b %Y %H:%M')
    
    # major tick step 15 mins
#     major_min_loc = mpl_dates.MinuteLocator(byminute=range(0,60,15))    
#     ax.xaxis.set_major_locator(major_min_loc)
    ax.xaxis.set_major_formatter(date_format)
    
    # minor step 1 min
#     minor_min_loc = mpl_dates.MinuteLocator(byminute=range(60))
#     ax.xaxis.set_minor_locator(minor_min_loc)
    
    for level in levels:
        plt.hlines(level[1], xmin=df['date'][level[0]], xmax=max(df['date']), colors='blue', linestyle='--')
    plt.plot(df['upperBand'], 'r')
    plt.plot(df['lowerBand'], 'b')
    plt.xticks(rotation=45)
    plt.ylabel('close') 
    plt.xlabel('date') 
    plt.title("ETHUSDT_UMCBL Support and Resistance")        
    fig.savefig(fname, bbox_inches='tight', dpi=150)
    plt.close(fig)
    plt.clf()
    send_photo(__TOKEN,__chat_id,fname,caption)
