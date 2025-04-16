import pandas as pd
import os
import re
from tqdm import tqdm  # 可选，用于显示进度


# 定义MET分类函数
def classify_met(met):
    if met < 1:
        return 'sleep'
    elif 1.0 <= met < 1.6:
        return 'static'
    elif 1.6 <= met < 3.0:
        return 'low'
    elif 3.0 <= met < 6.0:
        return 'moderate'
    else:
        return 'high'


# 处理单个志愿者文件
def process_volunteer(file_path):
    # 读取CSV文件，设置low_memory=False一次性读取整个文件，统一推断数据类型，避免分块导致的DtypeWarning。
    df = pd.read_csv(file_path, sep=r'[,;]', engine="python", quotechar='"', on_bad_lines='skip')  # 正则表达式匹配逗号或分号

    # 检查列名是否存在
    if 'time' not in df.columns:
        print(f"文件 {file_path} 中不存在 'time' 列。")
        return None

        # 将time列转换为数值类型
    df['time'] = pd.to_numeric(df['time'], errors='coerce')

    # 移除time列为NaN的行
    df = df.dropna(subset=['time'])
    # 重命名空标签列
    df.rename(columns={'Unnamed: 1': 'MET值'}, inplace=True)

    # 提取MET值列中的数字部分
    df['MET值'] = df['MET值'].apply(
        lambda x: float(re.findall(r'\d+\.?\d*', str(x))[0]) if re.findall(r'\d+\.?\d*', str(x)) else pd.NA)

    # 移除MET值列为NaN的行
    df = df.dropna(subset=['MET值'])

    # 检查数据框是否为空
    if df.empty:
        print(f"文件 {file_path} 经过处理后没有有效数据。")
        return {
            'total': 0.0,
            'sleep': 0.0,
            'high': 0.0,
            'moderate': 0.0,
            'low': 0.0,
            'static': 0.0
        }

    # 确保时间戳升序排列
    df.sort_values(by='time', inplace=True)

    # 计算时间差（单位：小时）
    timestamps = df['time'].values
    time_diffs = (timestamps[1:] - timestamps[:-1]) / (1000 * 3600)  # 毫秒转小时
    total_duration = (timestamps[-1] - timestamps[0]) / (1000 * 3600)  # 总时长

    # 初始化各活动时长
    activity_hours = {
        'sleep': 0.0,
        'static': 0.0,
        'low': 0.0,
        'moderate': 0.0,
        'high': 0.0
    }

    # 逐条分类统计（跳过最后一条，因为时间差数量比数据少1）
    for i in range(len(df) - 1):
        met = df.iloc[i]['MET值']
        duration = time_diffs[i]
        category = classify_met(met)
        activity_hours[category] += duration

    # 处理最后一条数据（使用平均间隔）
    if len(df) > 1:
        avg_interval = total_duration / (len(df) - 1)
    else:
        avg_interval = 0
    last_met = df.iloc[-1]['MET值']
    activity_hours[classify_met(last_met)] += avg_interval

    return {
        'total': total_duration,
        'sleep': activity_hours['sleep'],
        'high': activity_hours['high'],
        'moderate': activity_hours['moderate'],
        'low': activity_hours['low'],
        'static': activity_hours['static']
    }


# 主处理流程
def main():
    # 读取所有志愿者文件
    data_dir = "附件1/"
    volunteer_files = [f for f in os.listdir(data_dir) if f.startswith('P') and f.endswith('.csv')]

    results = []
    for file_name in tqdm(volunteer_files, desc="处理进度"):
        volunteer_id = file_name.split('.')[0][1:]  # 提取ID
        file_path = os.path.join(data_dir, file_name)

        # 处理数据
        stats = process_volunteer(file_path)
        if stats is not None:
            # 保存结果
            results.append({
                '志愿者 ID': f'P{volunteer_id}',
                '记录总时长（小时）': round(stats['total'], 4),
                '睡眠总时长（小时）': round(stats['sleep'], 4),
                '高等强度运动总时长（小时）': round(stats['high'], 4),
                '中等强度运动总时长（小时）': round(stats['moderate'], 4),
                '低等强度运动总时长（小时）': round(stats['low'], 4),
                '静态活动总时长（小时）': round(stats['static'], 4)
            })

    # 生成Excel文件
    if results:
        result_df = pd.DataFrame(results)
        result_df.to_excel('result_1.xlsx', index=False)
        print("处理完成，结果已保存至 result_1.xlsx")
    else:
        print("未处理任何有效数据。")


if __name__ == '__main__':
    main()
