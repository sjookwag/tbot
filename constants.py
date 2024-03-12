# from dataclasses import dataclass 
from enum import Enum
# import os

class LS(Enum):
    NIL = 0
    LONG  = 1
    SHORT  = 2
    CLOSE_LONG = -1
    CLOSE_SHORT = -2

class ID(Enum):
    THREE_WHITE_SOLDIERS = 0
    THREE_BLACK_CROWS = 1
    BULLISH_ENGULFING = 2
    BEARISH_ENGULFING = 3
    MACD_GOLDEN_CROSS = 4
    MACD_DEAD_CROSS = 5
    MFI_LONG = 6
    MFI_SHORT = 7
    MA_GOLDEN_CROSS = 8
    MA_DEAD_CROSS = 9
    CCI_UPWARD = 10
    CCI_DOWNWARD = 11


path_to_file = 'tbot.db'

__TOKEN = '5893898822:AAFFEcx2yPUk6BqPVzq_MXVoANswazBvtsg'
__chat_id = ['-1001593352488', '-1001969539888']
intervals = {'OHLCV':15,'CCI':15,'MA':15,'MACDRSI':15,'SUPRES':15,'FIBO':15,'MFI':15,'THREE':15,'PATTERNS':15}
pattern_hnames = {
    'Doji':'도지',        
    'Gravestone':'비석형 도지:\n상단에서 발생 시 하락으로 추세 변환이 될 수 있다고 보는 캔들',
    'Dragonfly':'잠자리형 도지:\n바닥권에서 발생 시 상승추세전환의 가능성이 높은 캔들', 
    'LongLeg':'긴꼬리 십자형 도지', 
    'Hammer':'해머형:\n하락추세 중에 형성되는 상승반전 패턴', 
    'Inv_Hammer':'역해머형:\n하락추세 중에 형성되는 상승반전 패턴', 
    'Spinning':'스피닝:\n상승 추세에서 발생하면, 매수세가 줄며 하락 추세로의 반전 암시\n하락 추세에서 발생하면, 매도세가 줄며 상승 추세로의 반전 암시',
    'Bull_Marubozu':'강세 마루보즈:\n매수세가 상당히 강력함을 의미하기 때문에 상승 반전 혹은 상승 지속 캔들로 인식', 
    'Bear_Marubouzu':'약세 마루보즈:\n매도세가 상당히 강력함을 의미하기 때문에 하락 반전 혹은 하락 지속 캔들로 인식', 
    'BullEngulf':'상승 장악형:\n음봉 뒤에 양봉이 나오는 형태로, 처음 나온 음봉을 감싸는 형태로 길게 양봉이 형성이 되는 것으로 상승 추세 전환 가능성이 있는 패턴. 하락 추세에서 상승 장악형이 형성이 되면 상승 추세로 전환될 가능성이 높고, 두 번째 양봉이 많은 거래량과 함께 강력한 매수세를 보일 수록 신뢰도 높음', 
    'BearEngulf':'하락 장악형:\n보통은 상승 추세에서 많이 발견되는 패턴으로 첫 번째 양봉 이후에 두 번째 음봉이 양봉 몸통을 전부 감싸고 있는 형태. 통상 상승 추세에서 하락 추세로 전환시킬 가능성이 높은 패턴으로 첫 번째 양봉이 짧으면 짧을수록, 그리고 두 번째 음봉이 길면 길게 형성이 될수록 하락 반전 가능성은 높아짐. 대개의 패턴에서 그러하듯이 두 번째 음봉에서 거래량이 많이 발생할 수록 더욱 신뢰도가 높음',
    'SBullEngulf':'상승 장악형(S):\n음봉 뒤에 양봉이 나오는 형태로, 처음 나온 음봉을 감싸는 형태로 길게 양봉이 형성이 되는 것으로 상승 추세 전환 가능성이 있는 패턴. 하락 추세에서 상승 장악형이 형성이 되면 상승 추세로 전환될 가능성이 높고, 두 번째 양봉이 많은 거래량과 함께 강력한 매수세를 보일 수록 신뢰도 높음',  
    'SBearEngulf':'하강 장악형(S):\n보통은 상승 추세에서 많이 발견되는 패턴으로 첫 번째 양봉 이후에 두 번째 음봉이 양봉 몸통을 전부 감싸고 있는 형태. 통상 상승 추세에서 하락 추세로 전환시킬 가능성이 높은 패턴으로 첫 번째 양봉이 짧으면 짧을수록, 그리고 두 번째 음봉이 길면 길게 형성이 될수록 하락 반전 가능성은 높아짐. 대개의 패턴에서 그러하듯이 두 번째 음봉에서 거래량이 많이 발생할 수록 더욱 신뢰도가 높음',
    'BullHarami':'상승형 하라미(Bull Harami):\n먼저 긴 빨간색 캔들이 관찰되고 그 뒤에는 이전 캔들의 몸통에 완전히 들어맞는 작은 녹색 캔들이 관찰. 매도 모멘텀이 둔화되고 있으며 곧 중단될 수 있음을 나타냄', 
    'BearHarami':'하락형 하라미(Bear Harami):\n긴 녹색 캔들 뒤에는 작은 빨간색 캔들 몸통이 선행 캔들 몸통에 완전히 둘러싸여 있는 것이 특징. 일반적으로 상승 추세의 끝과 시장 심리의 잠재적 변화를 나타냄.', 
    'DarkCloud':'흑운형:\n흑운형은 전일 장대 양봉이 등장한 이후에 장대 음봉이 발생한 상황을 말하는 것으로 상승추세의 끝자락에서 발생하는 것이 일반적. 보통의 경우에는 전일 장대 양봉의 몸통 길이에서 절반 이상 하락을 하게 되는 경우를 말하는데 이러한 형태는 차익매물이 발생하여 더이상 상승 추세를 이어나가기 힘든 상황',
    'Piercing':'관통형:\n관통형은 음봉 이후에 양봉이 나타나면서 첫 번째의 음봉을 두 번째 양봉이 몸통을 절반 이상 회복하는 형태. 이러한 관통형은 통상 하락 추세의 마지막 부분에서 발생할 확률이 높은데 반드시 두 번째 양봉의 종가가 첫 번째 음봉의 몸통 절반 이상을 넘어서야 의미가 있음. 만약 절반을 미치지 못한다면 하락 지속될 가능성이 높으나, 양봉의 종가가 높게 형성이 될 수록 신뢰도가 높아지는 형태.'
    }
pattern_names = ['Doji', 'Gravestone',
    'Dragonfly', 'LongLeg', 'Hammer', 'Inv_Hammer', 'Spinning',
    'Bull_Marubozu', 'Bear_Marubouzu', 'BullEngulf', 'BearEngulf',
    'SBullEngulf', 'SBearEngulf', 'BullHarami', 'BearHarami', 'DarkCloud',
    'Piercing']
# symbol = 'ETHUSDT_UMCBL'
symbol = 'ETH/USDT:USDT'