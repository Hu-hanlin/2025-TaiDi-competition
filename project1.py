import pandas as pd
import os
from tqdm import tqdm


# 定义met分类函数：
# def classify_met(met):
#     if met < 1.0:             # MET 值<1 为睡眠。
#         return 'sleep'
#     elif 1.0 <= met < 1.6:    # 1.0≤MET 值<1.6 之间为静态行为。
#         return 'static'
#     elif 1.6 <= met < 3.0:    # 1.6≤MET 值<3.0 为低强度。
#         return 'low'
#     elif 3.0 <= met < 6.0:    # 3. 0 ≤MET 值<6.0 为中等强度。
#         return 'moderate'
#     elif met >= 6.0:          # MET 值≥6.0 为高强度。
#         return 'high'


# 定义处理单个志愿者的函数
def process_volunteer():
    # 读取csv文件
    df = pd.read_csv("附件1/P001.csv", sep=r'[,;]', engine="python", quotechar='"', on_bad_lines='skip')
    df.rename(columns={'Unnamed: 1': 'MET值'}, inplace=True)
    print("原始列名：", df.columns)


process_volunteer()

