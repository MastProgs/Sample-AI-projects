

# In[]

import requests
url = "https://api.upbit.com/v1/candles/days"
querystring = {"market":"KRW-BTC","count":"200"}

headers = {"Accept": "application/json"}
response = requests.request("GET", url, headers=headers, params=querystring)

import json
jsonObject = json.loads(response.text)

import pandas as pd
data = pd.DataFrame(jsonObject)

cdle_time = []

pr_op = []
pr_end = []
pr_high = []
pr_low = []

tr_vol = []
tr_price = []
ch_rate = []
ch_price = []

pr_mid = []             # 중앙값
pr_op_end_gap = []      # 종가 - 시가
pr_high_low_gap = []    # 최고가 최저가 차이 절대값
b_is_upper = []         # 상승장인지 하락장인지
change_count = []       # 같은 방향 연속 진행된 횟 수

i = 0
for item in jsonObject:
    cdle_time.append(item["candle_date_time_kst"])
    pr_op.append(item["opening_price"])
    pr_end.append(item["trade_price"])
    pr_high.append(item["high_price"])
    pr_low.append(item["low_price"])
    tr_vol.append(item["candle_acc_trade_volume"])
    tr_price.append(item["candle_acc_trade_price"])
    ch_rate.append(item["change_rate"] * 100)
    ch_price.append(item["change_price"])

    pr_mid.append(((item["trade_price"] + item["opening_price"]) / 2))
    pr_op_end_gap.append(item["trade_price"] - item["opening_price"])
    pr_high_low_gap.append(item["high_price"] - item["low_price"])

# 날짜순으로 재정렬
cdle_time.reverse()
pr_op.reverse()
pr_end.reverse()
pr_high.reverse()
pr_low.reverse()
tr_vol.reverse()
tr_price.reverse()
ch_rate.reverse()
ch_price.reverse()
pr_mid.reverse()
pr_op_end_gap.reverse()
pr_high_low_gap.reverse()

i = 0
for j in range(0, len(pr_end)):
    if (pr_end[j] - pr_op[j] > 0):
        b_is_upper.append(1)
        if(i >= 0):
            i += 1
        else:            
            i = 1
        change_count.append(i)
    else:
        b_is_upper.append(-1)
        if(i <= 0):
            i += -1
        else:            
            i = -1
        change_count.append(i)

# 데이터 가공 여기까지 완료 ----------------------------------------------------

import matplotlib.pyplot as plt
import seaborn as sns;

data["same_direction_count"] = change_count
data["updown"] = b_is_upper
data["price_open_end_gap"] = pr_op_end_gap
data["price_high_low_gap"] = pr_high_low_gap
sns.pairplot(data, vars=["candle_acc_trade_price", "candle_acc_trade_volume", "price_high_low_gap", "price_open_end_gap", "change_rate", "updown", "same_direction_count"])
plt.show()

# 날짜별 가격
plt.figure(figsize=(40, 10))
plt.plot(cdle_time, pr_mid)
plt.xticks(rotation=90)
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Mid Price")
plt.show()

# 날짜별 가격 변동 퍼센트
plt.figure(figsize=(40, 10))
plt.plot(cdle_time, ch_rate)
plt.xticks(rotation=90)
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Change Rate")
plt.show()

# 날짜별 같은 방향 지속성
plt.figure(figsize=(40, 10))
plt.bar(cdle_time, change_count)
plt.xticks(rotation=90)
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Same Direction Count")
plt.show()

# 가격 퍼센트 대비 거래량의 상관관계
plt.figure(figsize=(20, 10))
plt.scatter(ch_rate, tr_vol)
plt.grid(True)
plt.xlabel("Percent")
plt.ylabel("Trade Volume")
plt.show()

# 하락장이 연이어 될 수록 거래량이 급격히 줄어든다 (same_direction_count <> candle_acc_trade_volume)
plt.figure(figsize=(20, 10))
plt.scatter(change_count, tr_vol)
plt.grid(True)
plt.xlabel("Change Count")
plt.ylabel("Trade Volume")
plt.show()

# 하지만 하락장이 연이어 될 수록 거래 대금은 급격히 늘어난다 (same_direction_count <> candle_acc_trade_price)
plt.figure(figsize=(20, 10))
plt.scatter(change_count, tr_price)
plt.grid(True)
plt.xlabel("Change Count")
plt.ylabel("Trade Price")
plt.show()

# 거래량, 거래대금과 마찬가지로 비슷한 그래프, 하락장이 연이을 수록 변동폭이 극대화 (same_direction_count <> price_high_low_gap)
plt.figure(figsize=(20, 10))
plt.scatter(change_count, pr_high_low_gap)
plt.grid(True)
plt.xlabel("Change Count")
plt.ylabel("High Low gap")
plt.show()

# 거래량, 거래대금과 변동폭은 상관관계 (price_high_low_gap <> candle_acc_trade_volume)
plt.figure(figsize=(20, 10))
plt.scatter(pr_high_low_gap, tr_vol)
plt.grid(True)
plt.xlabel("High Low gap")
plt.ylabel("Trade Volume")
plt.show()

# 상승장은 첫 상승이 가장 큰 상승을 보이지만, 하락장은 첫 하락장을 기점으로 점점 더 큰 하락을 불러옴 (same_direction_count <> price_open_end_gap / change_rate)
plt.figure(figsize=(20, 10))
plt.scatter(change_count, ch_rate)
plt.grid(True)
plt.xlabel("Change Count")
plt.ylabel("Change Rate")
plt.show()

rate_aver = 0
for rate in ch_rate:
    if rate < 0:
        rate_aver = rate * -1 + rate_aver
    else:
        rate_aver = rate + rate_aver

rate_aver = rate_aver / len(ch_rate)

print(rate_aver) # 평균 상승 하락 변동 퍼센트 3%


# %%
