import sys
import os
import matplotlib.dates as mpl_dates
import asyncio
import ccxt
import pandas as pd
from twisted.internet import task, reactor
from time import strftime, localtime
import logging
from logging.config import dictConfig

from constants import __TOKEN,__chat_id,symbol,intervals,pattern_hnames, LS, ID
from indicators import calcBol,calcFiboRetrace,calcCCI,calcMA,calcMACD,calcMFI,calcRSI,calcSupRes,threeSoldiers,patterns
# from indicators import calcSupRes0315
from charts import chart_ma,chart_mfi,plot_updntrends,chart_three
from utils import send_msg
from db import execute_statement
from paper import pThree, pMACD, pMFI, pCCI, pMA

async def bitget_ohlcv(): 
    glThree =  pThree()
    glMACD = pMACD()
    glMFI = pMFI()
    glCCI = pCCI()
    glMA = pMA()

    def doOHLCV():
        # timeframe03='3m'
        timeframe15='15m'
        limit=129
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} Just get started~')
        pd.set_option('display.float_format', lambda x: '%.2f' % x)   
        try:
            bitget = ccxt.bitget()    
            # ohlcv03 = bitget.fetch_ohlcv(symbol=symbol, timeframe=timeframe03, limit=limit)
            ohlcv15 = bitget.fetch_ohlcv(symbol=symbol, timeframe=timeframe15, limit=limit)
            print('Succeed in getting the candle data')            
        except:
            msg = f"{dt} Oops! Something went wrong on the way of getting OHLCV from Bitget exchange.\nPlease bear with me until it's fixed"
            send_msg(__TOKEN, __chat_id, msg)
            print('Oops! Something went wrong on the way of getting OHLCV from Bitget exchange.')            
            # logger.info(msg)
        else:    
            # dfOhlcv03 = pd.DataFrame(ohlcv03, columns=['date', 'open', 'high', 'low', 'close', 'volume']) 
            dfOhlcv15 = pd.DataFrame(ohlcv15, columns=['date', 'open', 'high', 'low', 'close', 'volume']) 
            # dfOhlcv03['date'] = pd.to_datetime(dfOhlcv03['date'], unit='ms')
            dfOhlcv15['date'] = pd.to_datetime(dfOhlcv15['date'], unit='ms')
            # dfOhlcv03.set_index('date',inplace=True, drop=False)
            dfOhlcv15.set_index('date',inplace=True, drop=False)
            # dfOhlcv03['date'] = dfOhlcv03['date'].apply(mpl_dates.date2num)
            dfOhlcv15['date'] = dfOhlcv15['date'].apply(mpl_dates.date2num)
            # dfOhlcv03 = dfOhlcv03.loc[:,['date','open', 'high', 'low', 'close', 'volume']]
            dfOhlcv15 = dfOhlcv15.loc[:,['date','open', 'high', 'low', 'close', 'volume']]
            # print(f'{dt} doOHLCV03() : row count :{dfOhlcv03.shape[0]}  doOHLCV15() : row count :{dfOhlcv15.shape[0]}')
            print(f'{dt} doOHLCV15() : row count :{dfOhlcv15.shape[0]}')
            currentPx = dfOhlcv15['close'].iloc[-1]

            doThree(dfOhlcv15)
            doMFI(dfOhlcv15)
            doMA(dfOhlcv15)
            doMACDRSI(dfOhlcv15)
            doSUPRES(dfOhlcv15)
            # doSUPRES0315(dfOhlcv03,dfOhlcv15)
            # doTrends(dfOhlcv15)
            doPatterns(dfOhlcv15)

    # def doSUPRES0315(df03, df15):
    #     dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
    #     print(f'{dt} doSupRes0315()')
    #     # timeframe15 = '15m'  
    #     calcBol(df03)
    #     calcBol(df15)
    #     ub03=df03['upperBand'].iloc[-1]
    #     lb03=df03['lowerBand'].iloc[-1]
    #     ub15=df15['upperBand'].iloc[-1]
    #     lb15=df15['lowerBand'].iloc[-1]
    #     pxclose03=df03['close'].iloc[-1]
    #     pxopen03=df03['open'].iloc[-1]
    #     pxclose15=df15['close'].iloc[-1]
    #     pxopen15=df15['open'].iloc[-1]
    #     if not((lb03<pxopen03<ub03) and (lb03<pxclose03<ub03)) and not((lb15<pxopen15<ub15) and (lb15<pxclose15<ub15)):
    #         calcSupRes0315(df03[-61:], df15[-61:])
    #         logger.info('doSupRes')

    def doPatterns(df):
        msg = ''
        bln = False
        # timeframe = '15m'
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doPatterns()')
        ptn = patterns(df)
        df = df.loc[:,['open', 'high', 'low', 'close']]
        for k, v in ptn.items():
            if v==True:
                bln = True 
                chart_three(df, 15, f'{k}.jpg', f'{k} pattern', f'{pattern_hnames[k]}')
                # df = df[df['RSI'].notna()]
                df = calcRSI(df)
                df = df[df['RSI'].notna()]
                # plot_updntrends(df,k)
                # msg = f"{pattern_hnames[k]} 발생"
                # print(msg)
                # msg += f"\n*발신간격: {intervals['PATTERNS']}m\n*수신간격: {timeframe}"
                # send_msg(__TOKEN, __chat_id, msg)
                # logger.info(msg)
        if bln:
            plot_updntrends(df)

    # def doTrends(df):
    #     dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
    #     print(f'{dt} doTrends()')
    #     msg = ''
    #     timeframe = '15m'
    #     df = calcRSI(df)
    #     df = heikin_ashi(df)
    #     df = df[df['RSI'].notna()]
    #     plot_updntrends(df)
    #     if lastDoji(df):
    #         df = df.loc[:,['open', 'high', 'low', 'close']]
    #         chart_three(df, 15, 'dojee.jpg','Doji pattern', '도지패턴')
    #         # msg = f"DOJI 발생"
    #         # msg += f"\n*발신간격: {intervals['MFI']}m\n*수신간격: {timeframe}"
    #         # send_msg(__TOKEN, __chat_id, msg)
    #         # logger.info(msg)
    #         df.rename(columsns = {'Open':'open','High':'high','Low':'low','Close':'close','Volume':'Volume'}, inplace = True)
    #         df = df[df['RSI'].notna()]
    #         plot_updntrends(df)
    #         logger.info('Uptrend and Downtrend')
            
    def doThree(df):
        rtn:float = 0.0
        msg:str = ''
        timeframe:str = '15m'  
        df = df.loc[:,['open', 'high', 'low', 'close']]
        currentPx:float = df['close'].iloc[-1]
        msg, signal, indicator = threeSoldiers(df)
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())

        # print('---------------- ',signal, glThree.Long, glThree.Short, glThree.Nil)
        
        if signal==LS.LONG and glThree.Long==False and glThree.Nil==True:
            # 롱포지션 신규 - 롱시그널 발생+기존없음
            glThree.Long = True              
            glThree.Nil = False 
            glThree.EntryPx = df['close'].iloc[-1] 
            msg += f"\n롱포지션 개시: 진입 @{glThree.EntryPx:.2f}"
            sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.THREE_WHITE_SOLDIERS.value},{signal.value},{glThree.EntryPx});"
            execute_statement(sql)
        # elif signal==LS.LONG.value and doThreeLong==True and doThreeNil==False:

        elif signal==LS.SHORT and glThree.Long==True:
            # 롱포지션 청산
            glThree.Long = False
            glThree.Nil = True
            glThree.ExitPx = df['close'].iloc[-1] 
            rtn = (glThree.ExitPx/glThree.EntryPx)-1
            msg += f"\n롱포지션 청산: 진입{glThree.EntryPx:.2f}, 청산:{glThree.ExitPx:.2f}"
            msg += f"\n수익률(%): {rtn:.2f}"
            sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.THREE_WHITE_SOLDIERS.value},{LS.CLOSE_LONG.value},{glThree.ExitPx});"
            execute_statement(sql)

        elif signal==LS.LONG and glThree.Short==True:
            # 숏포지션 청산
            glThree.Short = False 
            glThree.Nil = True
            glThree.ExitPx = df['close'].iloc[-1] 
            rtn = 1-(glThree.ExitPx/glThree.EntryPx)
            msg += f"\n숏포지션 청산: 진입 @{glThree.EntryPx:.2f}, 청산@{glThree.ExitPx:.2f}"            
            msg += f"\n수익률(%): {rtn:.2f}"
            sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.THREE_BLACK_CROWS.value},{LS.CLOSE_SHORT.value},{glThree.ExitPx});"
            execute_statement(sql)

        elif signal==LS.SHORT and glThree.Short==False and glThree.Nil==True:
            # 숏포지션 신규
            glThree.Short = True             
            glThree.Nil = False 
            glThree.EntryPx = df['close'].iloc[-1] 
            msg += f"\n숏포지션 신규: 진입 @{glThree.EntryPx:.2f}"
            sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.THREE_BLACK_CROWS.value},{signal.value},{glThree.EntryPx});"
            execute_statement(sql)

        elif glThree.Nil==False:
            # 포지션 보유중, 평가
            msg += f"\n* 페이퍼 트레이딩(Three Soldiers) *"                
            if glThree.Long == True:
                rtn = (currentPx-glThree.EntryPx)/glThree.EntryPx                 
                msg += f"\n* 포지션 : 롱(LONG)"                 
            elif glThree.Short == True:
                rtn = (glThree.EntryPx-currentPx)/glThree.EntryPx
                msg += f"\n* 포지션 : 숏(SHORT)"                 
            rtn = rtn * 10
            msg += f"\n* 진입가격: {glThree.EntryPx:.2f}"                
            msg += f"\n* 현재가격: {currentPx:.2f}"                
            msg += f"\n* 평가수익률(%): {rtn:.2f}"                
        print(f'{dt} doThree()')
        if glThree.Nil==False:                         
            send_msg(__TOKEN, __chat_id, msg)
        # logger.info(msg)

    def doMFI(df):
        rtn:float = 0.0
        msg = pmsg = ''
        timeframe = '15m'
        currentPx:float = df['close'].iloc[-1]  
        df = calcMFI(df, 10)
        df = calcBol(df)
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        mfi = df['MFI'].iloc[-1]
        _B = df['%B'].iloc[-1]
        print(f'{dt} doMFI()')
        if mfi>=80 and _B>=1.0:
            msg = f'Symbol: {symbol}\nDatetime: {dt}\nMFI\t: {mfi:,.2f}\n%B\t: {_B:,.2f}'
            msg += f'\nSignal\t: Long'
            if glMFI.Short==True:
                glMFI.ExitPx=df["close"].iloc[-1]
                glMFI.Short = False
                glMFI.Nil = True
                rtn = 1-glMFI.ExitPx/glMFI.EntryPx
                pmsg += f"* MFI 숏포지션 청산" 
                pmsg += f"\n진입 @{glMFI.EntryPx:.2f}, 청산@{glMFI.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MFI_SHORT.value},{LS.CLOSE_SHORT.value},{glMFI.ExitPx});"
                execute_statement(sql) 

            if glMFI.Nil == True:
                glMFI.Long = True 
                glMFI.EntryPx = df["close"].iloc[-1]
                glMFI.Nil = False
                pmsg += f"* MFI 롱포지션 개시" 
                pmsg += f"\n진입 @{glMFI.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MFI_LONG.value},{LS.LONG.value},{glMFI.EntryPx});"
                execute_statement(sql) 

        elif mfi<=20 and _B<=0.0:
            msg = f'Symbol: {symbol}\nDatetime: {dt}\nMFI\t: {mfi:,.2f}\n%B\t: {_B:,.2f}'
            msg += f'\nSignal\t: Short'
            if glMFI.Long==True:
                glMFI.ExitPx=df["close"].iloc[-1]
                glMFI.Long = False
                glMFI.Nil = True
                rtn = glMFI.ExitPx/glMFI.EntryPx-1
                pmsg += f"* MFI 롱포지션 청산" 
                pmsg += f"\n진입 @{glMFI.EntryPx:.2f}, 청산@{glMFI.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MFI_LONG.value},{LS.CLOSE_LONG.value},{glMFI.ExitPx});"
                execute_statement(sql) 

            if glMFI.Nil == True:
                glMFI.Short = True 
                glMFI.EntryPx = df["close"].iloc[-1]
                glMFI.Nil = False
                pmsg += f"* MFI 숏포지션 개시" 
                pmsg += f"\n진입 @{glMFI.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MFI_SHORT.value},{LS.SHORT.value},{glMFI.EntryPx});"
                execute_statement(sql)
        else:
            # 포지션 보유중, 평가
            if glMFI.Nil == False:
                msg += f"\n* 페이퍼 트레이딩(MFI) *"                
                if glMFI.Long == True:
                    rtn = (currentPx-glMFI.EntryPx)/glMFI.EntryPx                 
                    msg += f"\n* 포지션 : 롱(LONG)"                 
                elif glMFI.Short == True:
                    rtn = (glMFI.EntryPx-currentPx)/glMFI.EntryPx
                    msg += f"\n* 포지션 : 숏(SHORT)" 
                rtn = rtn * 10                    
                msg += f"\n* 진입가격: {glMFI.EntryPx:.2f}"                
                msg += f"\n* 현재가격: {currentPx:.2f}"                
                msg += f"\n* 평가수익률(%): {rtn:.2f}"                

        if len(msg)!=0: 
            chart_mfi(df)                      
            msg += f"\n*발신간격: {intervals['MFI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN, __chat_id, msg)
            # logger.info(msg)

        if len(pmsg)!=0:
            pmsg += f"\n*발신간격: {intervals['MFI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, pmsg)    

    def doFiboRetrace(df):
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doFibo()')
        timeframe = '15m'  
        calcBol(df)
        calcFiboRetrace(df)
        logger.info('doFiboRetrance')

    def doSUPRES(df):
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doSupRes()')
        timeframe = '15m'  
        calcBol(df)
        ub=df['upperBand'].iloc[-1]
        lb=df['lowerBand'].iloc[-1]
        pxclose=df['close'].iloc[-1]
        pxopen=df['open'].iloc[-1]
        if not ((lb<pxopen<ub) and (lb<pxclose<ub)):
            calcSupRes(df[-61:])
            logger.info('doSupRes')

    def doCCI(df):
        rtn:float = 0.0
        msg = pmsg = ''
        timeframe = '15m'
        currentPx:float = df['close'].iloc[-1]  
        df = calcCCI(df)
        cci_1 = df['cci'].iloc[-1]
        cci_2 = df['cci'].iloc[-2]
        upward = cci_1>0.0 and cci_2<0.0
        dnward = cci_1<0.0 and cci_2>0.0        
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doCCI()')
        if upward:            
            msg = f'Symbol: {symbol}\nDatetime: {dt}\nClose\t: {currentPx:,.2f}\nCCI-1\t: {cci_1:,.2f}\nCCI-2\t: {cci_2:,.2f}'
            msg += f'\n상향돌파\t: {upward}'
            if glCCI.Short==True:
                glCCI.ExitPx=df["close"].iloc[-1]
                glCCI.Short = False
                glCCI.Nil = True
                rtn = 1-glCCI.ExitPx/glCCI.EntryPx
                pmsg += f"* CCI 숏포지션 청산" 
                pmsg += f"\n진입 @{glCCI.EntryPx:.2f}, 청산@{glCCI.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.CCI_SHORT.value},{LS.CLOSE_SHORT.value},{glCCI.ExitPx});"
                execute_statement(sql) 

            if glCCI.Nil == True:
                glCCI.Long = True 
                glCCI.EntryPx = df["close"].iloc[-1]
                glCCI.Nil = False
                pmsg += f"* CCI 롱포지션 개시" 
                pmsg += f"\n진입 @{glCCI.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.CCI_LONG.value},{LS.LONG.value},{glCCI.EntryPx});"
                execute_statement(sql) 

        elif dnward:                
            msg = f'Symbol: {symbol}\nDatetime: {dt}\nClose\t: {currentPx:,.2f}\nCCI-1\t: {cci_1:,.2f}\nCCI-2\t: {cci_2:,.2f}'
            msg += f'\n하향돌파\t: {dnward}'
            if glCCI.Long==True:
                glCCI.ExitPx=df["close"].iloc[-1]
                glCCI.Long = False
                glCCI.Nil = True
                rtn = glCCI.ExitPx/glCCI.EntryPx-1
                pmsg += f"* CCI 롱포지션 청산" 
                pmsg += f"\n진입 @{glCCI.EntryPx:.2f}, 청산@{glCCI.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.CCI_LONG.value},{LS.CLOSE_LONG.value},{glCCI.ExitPx});"
                execute_statement(sql) 

            if glCCI.Nil == True:
                glCCI.Short = True 
                glCCI.EntryPx = df["close"].iloc[-1]
                glCCI.Nil = False
                pmsg += f"* CCI 숏포지션 개시" 
                pmsg += f"\n진입 @{glCCI.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.CCI_SHORT.value},{LS.SHORT.value},{glCCI.EntryPx});"
                execute_statement(sql)
        else:
            if glCCI.Nil == False:
                # 포지션 보유중, 평가
                msg += f"\n* 페이퍼 트레이딩(CCI) *"                
                if glCCI.Long == True:
                    rtn = (currentPx-glCCI.EntryPx)/glCCI.EntryPx                 
                    msg += f"\n* 포지션 : 롱(LONG)"                 
                elif glCCI.Short == True:
                    rtn = (glCCI.EntryPx-currentPx)/glCCI.EntryPx
                    msg += f"\n* 포지션 : 숏(SHORT)"    
                rtn = rtn * 10                                 
                msg += f"\n* 진입가격: {glCCI.EntryPx:.2f}"                
                msg += f"\n* 현재가격: {currentPx:.2f}"                
                msg += f"\n* 평가수익률(%): {rtn:.2f}"

        if len(msg)!=0:                        
            msg += f"\n*발신간격: {intervals['CCI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, msg)
        if len(pmsg)!=0:
            pmsg += f"\n*발신간격: {intervals['CCI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, pmsg)            
            # logger.info(msg)

    def doMA(df):
        rtn:float = 0.0
        golden_cross = dead_cross = False
        msg = pmsg = ''
        timeframe = '15m'       
        df = calcMA(df)
        df = calcBol(df)
        currentPx = df['close'].iloc[-1]
        ma5 = df["ma5"].iloc[-1] 
        ma10 = df["ma10"].iloc[-1]
        ma20 = df["ma20"].iloc[-1]        
        ma60 = df["ma60"].iloc[-1]        
        ma120 = df["ma120"].iloc[-1]        
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doMA()')         
        if currentPx<ma5<ma10<ma20<ma60<ma120:            
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\n(0<5<10<20<60<120)\nClose\t: {currentPx:,.2f}\nMA5\t: {ma5:,.2f}\nMA10\t: {ma10:,.2f}\nMA20\t: {ma20:,.2f}\nMA60\t: {ma60:,.2f}\nMA120\t: {ma120:,.2f}'        
            dead_cross=True 
        elif currentPx<ma5<ma10<ma20<ma60:            
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\n(0<5<10<20<60)\nClose\t: {currentPx:,.2f}\nMA5\t: {ma5:,.2f}\nMA10\t: {ma10:,.2f}\nMA20\t: {ma20:,.2f}\nMA60\t: {ma60:,.2f}'        
            dead_cross=True 

        if currentPx>ma5>ma10>ma20>ma60>ma120:            
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\n(0>5>10>20>60>120)\nClose\t: {currentPx:,.2f}\nMA5\t: {ma5:,.2f}\nMA10\t: {ma10:,.2f}\nMA20\t: {ma20:,.2f}\nMA60\t: {ma60:,.2f}\nMA120\t: {ma120:,.2f}'
            golden_cross=True
        elif currentPx>ma5>ma10>ma20>ma60:            
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\n(0>5>10>20>60)\nClose\t: {currentPx:,.2f}\nMA5\t: {ma5:,.2f}\nMA10\t: {ma10:,.2f}\nMA20\t: {ma20:,.2f}\nMA60\t: {ma60:,.2f}'
            golden_cross=True
        
        if golden_cross==True:
            if glMA.Short==True:
                glMA.ExitPx=df["close"].iloc[-1]
                glMA.Short = False
                glMA.Nil = True
                rtn = 1-glMA.ExitPx/glMA.EntryPx
                pmsg += f"* MA 숏포지션 청산" 
                pmsg += f"\n진입 @{glMA.EntryPx:.2f}, 청산@{glMA.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MA_DEAD_CROSS.value},{LS.CLOSE_SHORT.value},{glMA.ExitPx});"
                execute_statement(sql) 

            if glMA.Nil == True:
                glMA.Long = True 
                glMA.EntryPx = df["close"].iloc[-1]
                glMA.Nil = False
                pmsg += f"* MA 롱포지션 개시" 
                pmsg += f"\n진입 @{glMA.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MA_GOLDEN_CROSS.value},{LS.LONG.value},{glMA.EntryPx});"
                execute_statement(sql)
        elif dead_cross==True:
            if glMA.Long==True:
                glMA.ExitPx=df["close"].iloc[-1]
                glMA.Long = False
                glMA.Nil = True
                rtn = glMA.ExitPx/glMA.EntryPx-1
                pmsg += f"* MA 롱포지션 청산" 
                pmsg += f"\n진입 @{glMA.EntryPx:.2f}, 청산@{glMA.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MA_GOLDEN_CROSS.value},{LS.CLOSE_LONG.value},{glCCI.ExitPx});"
                execute_statement(sql) 

            if glMA.Nil == True:
                glMA.Short = True 
                glMA.EntryPx = df["close"].iloc[-1]
                glMA.Nil = False
                pmsg += f"* MA 숏포지션 개시" 
                pmsg += f"\n진입 @{glMA.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MA_DEAD_CROSS.value},{LS.SHORT.value},{glMA.EntryPx});"
                execute_statement(sql)
        else:
            if glMA.Nil == False:
                # 포지션 보유중, 평가
                msg += f"\n* 페이퍼 트레이딩(MA) *"                
                if glMA.Long == True:
                    rtn = (currentPx-glMA.EntryPx)/glMA.EntryPx                 
                    msg += f"\n* 포지션 : 롱(LONG)"                 
                elif glMA.Short == True:
                    rtn = (glMA.EntryPx-currentPx)/glMA.EntryPx
                    msg += f"\n* 포지션 : 숏(SHORT)"  
                rtn = rtn * 10                   
                msg += f"\n* 진입가격: {glMA.EntryPx:.2f}"                
                msg += f"\n* 현재가격: {currentPx:.2f}"                
                msg += f"\n* 평가수익률(%): {rtn:.2f}"

        if len(msg)!=0:
            x = df['date'][-10:]
            ys = [df['close'][-10:],df['ma5'][-10:],df['ma10'][-10:],df['ma20'][-10:],df['ma60'][-10:],df['ma120'][-10:],df['upperBand'][-10:],df['lowerBand'][-10:]]
            lbls =['Close','MA5','MA10','MA20','MA60','MA120','Upper band', 'Lower band']
            chart_ma(x,ys,lbls,'linechart.jpg','Moving Average')
            msg += f"\n*발신간격: {intervals['MA']}m\n*수신간격: {timeframe}" 
            send_msg(__TOKEN,__chat_id, msg)
        if len(pmsg)!=0:
            pmsg += f"\n*발신간격: {intervals['MA']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, pmsg)    
            # logger.info(msg)

    def doMACDRSI(df):
        rtn:float = 0.0
        msg = pmsg = ''
        # 15분봉 구하여 MACD/RSI 계산
        timeframe = '15m'
        currentPx = df['close'].iloc[-1]
        df = calcMACD(df)
        # df = calcRSI(calcMACD(df))
        macdShort = df["MACD_short"].iloc[-1]
        macdLong = df["MACD_long"].iloc[-1]
        macd = df["MACD"].iloc[-1]
        macdSgnl = df["MACD_signal"].iloc[-1]
        macdOsci = df["MACD_oscillator"].iloc[-1]
        macdSign = df["MACD_sign"].iloc[-1]
        # rsi = df["RSI"].iloc[-1]
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print(f'{dt} doMACDRSI()')
        # if df["RSI_signal"].iloc[-2]>df["RSI"].iloc[-2] and df["RSI_signal"].iloc[-1]<df["RSI"].iloc[-1]: # Golden cross 
        #     msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\nRSI Golden Cross\nRSI Signal \t: {df["RSI_signal"].iloc[-1]:,.2f}\nRSI: {rsi:,.2f}'
        # if df["RSI_signal"].iloc[-2]<df["RSI"].iloc[-2] and df["RSI_signal"].iloc[-1]>df["RSI"].iloc[-1]: # Dead cross 
        #     msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\nRSI Dead Cross\nRSI Signal \t: {df["RSI_signal"].iloc[-1]:,.2f}\nRSI: {rsi:,.2f}'
        if df["MACD_signal"].iloc[-2]>df["MACD"].iloc[-2] and df["MACD_signal"].iloc[-1]<df["MACD"].iloc[-1]:
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\nMACD Golden Cross\nMACD Short\t: {macdShort:,.2f}\nMACD Long\t: {macdLong:,.2f}\nMACD\t: {macd:,.2f}\nMACD Signal\t: {macdSgnl:,.2f}\nMACD Oscillator\t: {macdOsci:,.2f}\nMACD sign\t: {macdSign}'
            if glMACD.Short==True:
                glMACD.ExitPx=df["close"].iloc[-1]
                glMACD.Short = False
                glMACD.Nil = True
                rtn = 1-glMACD.ExitPx/glMACD.EntryPx
                pmsg += f"* MACD 숏포지션 청산" 
                pmsg += f"\n진입 @{glMACD.EntryPx:.2f}, 청산@{glMACD.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MACD_DEAD_CROSS.value},{LS.CLOSE_SHORT.value},{glMACD.ExitPx});"
                execute_statement(sql) 

            if glMACD.Nil == True:
                glMACD.Long = True 
                glMACD.EntryPx = df["close"].iloc[-1]
                glMACD.Nil = False
                pmsg += f"\n\n* MACD 롱포지션 개시" 
                pmsg += f"\n진입 @{glMACD.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MACD_GOLDEN_CROSS.value},{LS.LONG.value},{glMACD.EntryPx});"
                execute_statement(sql) 
        
        elif df["MACD_signal"].iloc[-2]<df["MACD"].iloc[-2] and df["MACD_signal"].iloc[-1]>df["MACD"].iloc[-1]:
            msg = msg + f'Symbol: {symbol}\nDatetime: {dt}\nMACD Dead Cross\nMACD Short\t: {macdShort:,.2f}\nMACD Long\t: {macdLong:,.2f}\nMACD\t: {macd:,.2f}\nMACD Signal\t: {macdSgnl:,.2f}\nMACD Oscillator\t: {macdOsci:,.2f}\nMACD sign\t: {macdSign}'
            if glMACD.Long==True:
                glMACD.ExitPx=df["close"].iloc[-1]
                glMACD.Long = False
                glMACD.Nil = True 
                rtn = glMACD.ExitPx/glMACD.EntryPx-1
                pmsg += f"* MACD 롱포지션 청산" 
                pmsg += f"\n진입 @{glMACD.EntryPx:.2f}, 청산@{glMACD.ExitPx:.2f}"            
                pmsg += f"\n수익률(%): {rtn:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MACD_GOLDEN_CROSS.value},{LS.CLOSE_LONG.value},{glMACD.ExitPx});"
                execute_statement(sql)

            if glMACD.Nil == True:
                glMACD.Short = True 
                glMACD.EntryPx = df["close"].iloc[-1]
                glMACD.Nil = False
                pmsg += f"\n\n* MACD 숏포지션 개시" 
                pmsg += f"\n진입 @{glMACD.EntryPx:.2f}"
                sql = f"INSERT INTO tblTrans (dtTrans,indicator,tran,px) VALUES('{dt}',{ID.MACD_DEAD_CROSS.value},{LS.SHORT.value},{glMACD.EntryPx});"
                execute_statement(sql)  
        else:
            if glMACD.Nil == False:
                # 포지션 보유중, 평가
                msg += f"\n* 페이퍼 트레이딩(MACD) *"                
                if glMACD.Long == True:
                    rtn = (currentPx-glMACD.EntryPx)/glMACD.EntryPx                 
                    msg += f"\n* 포지션 : 롱(LONG)"                 
                elif glMACD.Short == True:
                    rtn = (glMACD.EntryPx-currentPx)/glMACD.EntryPx
                    msg += f"\n* 포지션 : 숏(SHORT)"  
                rtn = rtn * 10                   
                msg += f"\n* 진입가격: {glMACD.EntryPx:.2f}"                
                msg += f"\n* 현재가격: {currentPx:.2f}"                
                msg += f"\n* 평가수익률(%): {rtn:.2f}"

        if len(msg)!=0:
            msg += f"\n*발신간격: {intervals['MACDRSI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, msg)

        if len(pmsg)!=0:
            pmsg += f"\n*발신간격: {intervals['MACDRSI']}m\n*수신간격: {timeframe}"
            send_msg(__TOKEN,__chat_id, pmsg)    
            # logger.info(msg)

    intervalOHLCV = intervals['OHLCV'] * 60.0 # Sixty seconds
    ohlcv = task.LoopingCall(doOHLCV)
    ohlcv.start(intervalOHLCV) # call every sixty seconds
    reactor.run()
    
if __name__=='__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs','mybitget.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file']
        }
    })    
    logger = logging.getLogger('logger-1')
    logger.debug('Debug level!')
    logger.info('Bitgetboy get started!')

    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())    
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(bitget_ohlcv())

    if sys.version_info<(3,10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        loop.run_until_complete(bitget_ohlcv())
