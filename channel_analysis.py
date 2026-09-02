import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import matplotlib as mpl
import matplotlib.font_manager as fm
import os

font_path = os.path.join(os.path.dirname(__file__), 'NotoSansSC-VariableFont_wght.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()

# 设置页面布局
st.set_page_config(layout="wide")
st.title("渠道归因分析 - 马尔可夫链模型")

# 加载数据（缓存提高性能）
@st.cache_data
def load_data():
    return pd.read_csv('渠道转化.csv', encoding='utf8')

df_data = load_data()

# ------------------------- 数据预处理 -------------------------
df_data = df_data.sort_values(['用户cookie', '时戳'], ascending=[False, True])
df_data['访问次序'] = df_data.groupby('用户cookie').cumcount() + 1

# ------------------------- 构建用户路径 -------------------------
df_paths = df_data.groupby('用户cookie')['渠道'].agg(lambda x: x.unique().tolist()).reset_index()
df_last_step = df_data.drop_duplicates('用户cookie', keep='last')[['用户cookie', '是否转化']]
df_paths = pd.merge(df_paths, df_last_step, how='left', on='用户cookie')

# 添加开始和结束状态
df_paths['路径'] = np.where(
    df_paths['是否转化'] == 0,
    '开始, ' + df_paths['渠道'].apply(', '.join) + ', 未转化',
    '开始, ' + df_paths['渠道'].apply(', '.join) + ', 成功转化'
)
df_paths['路径'] = df_paths['路径'].str.split(', ')
path_list = df_paths['路径']

# ------------------------- 整体转化指标 -------------------------
total_conversions = sum(path.count('成功转化') for path in path_list)
conversion_rate = total_conversions / len(path_list)
st.metric("整体转化数", total_conversions)
st.metric("基准转化率", f"{conversion_rate:.4f}")

# ------------------------- 转移状态计数 -------------------------
def transition_states(path_list):
    unique_channels = set(x for element in path_list for x in element)
    transition_states = {x + '>' + y: 0 for x in unique_channels for y in unique_channels}
    for possible_state in unique_channels:
        if possible_state not in ['成功转化', '未转化']:
            for user_path in path_list:
                if possible_state in user_path:
                    indices = [i for i, s in enumerate(user_path) if possible_state in s]
                    for col in indices:
                        transition_states[user_path[col] + '>' + user_path[col + 1]] += 1
    return transition_states

trans_states = transition_states(path_list)

# ------------------------- 转移概率 -------------------------
def transition_prob(path_list, trans_dict):
    unique_channels = set(x for element in path_list for x in element)
    trans_prob = defaultdict(dict)
    for state in unique_channels:
        if state not in ['成功转化', '未转化']:
            counter = 0
            index = [i for i, s in enumerate(trans_dict) if state + '>' in s]
            for col in index:
                if trans_dict[list(trans_dict)[col]] > 0:
                    counter += trans_dict[list(trans_dict)[col]]
                    for col in index:
                        if trans_dict[list(trans_dict)[col]] > 0:
                            state_prob = float(trans_dict[list(trans_dict)[col]]) / float(counter)
                            trans_prob[list(trans_dict)[col]] = state_prob
    return trans_prob

trans_prob = transition_prob(path_list, trans_states)

# ------------------------- 转移矩阵 -------------------------
def transition_matrix(path_list, transition_probabilities):
    unique_channels = set(x for element in path_list for x in element)
    unique_channels_list = list(unique_channels)  # 转为列表
    trans_matrix = pd.DataFrame(0.0, index=unique_channels_list, columns=unique_channels_list)
    for state in ['成功转化', '未转化']:
        if state in trans_matrix.index:
            trans_matrix.loc[state, state] = 1.0
    for key, value in transition_probabilities.items():
        origin, destination = key.split('>')
        trans_matrix.at[origin, destination] = value
    return trans_matrix

trans_matrix = transition_matrix(path_list, trans_prob)

# ------------------------- 可视化：转移概率热力图 -------------------------
st.subheader("转移概率热力图")
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(trans_matrix, cmap='Blues', annot=True, fmt='.2f', ax=ax)
st.pyplot(fig)

# ------------------------- 移除效应计算 -------------------------
def removal_effects(df, conversion_rate):
    removal_effects_dict = {}
    channels = [channel for channel in df.columns if channel not in ['开始', '未转化', '成功转化']]
    for channel in channels:
        removal_df = df.drop(channel, axis=1).drop(channel, axis=0).copy()
        for column in removal_df.columns:
            row_sum = np.sum(list(removal_df.loc[column]))
            null_pct = 1.0 - row_sum
            if null_pct != 0:
                removal_df.loc[column, '未转化'] = null_pct
        removal_df.loc['未转化', '未转化'] = 1.0

        to_conv = removal_df[['未转化', '成功转化']].drop(['未转化', '成功转化'], axis=0)
        to_non_conv = removal_df.drop(['未转化', '成功转化'], axis=1).drop(['未转化', '成功转化'], axis=0)
        
        inv_diff = np.linalg.inv(np.identity(len(to_non_conv.columns)) - np.asarray(to_non_conv))
        dot_prod = np.dot(inv_diff, np.asarray(to_conv))
        removal_cvr = pd.DataFrame(dot_prod, index=to_conv.index)[[1]].loc['开始'].values[0]
        removal_effect = 1 - removal_cvr / conversion_rate
        removal_effects_dict[channel] = removal_effect
    return removal_effects_dict

removal_effects_dict = removal_effects(trans_matrix, conversion_rate)

# ------------------------- 可视化：移除效应柱状图 -------------------------
st.subheader("各渠道移除效应系数")
fig2, ax2 = plt.subplots()
ax2.bar(removal_effects_dict.keys(), removal_effects_dict.values())
ax2.set_ylabel("移除效应系数")
st.pyplot(fig2)

st.write("各渠道移除效应系数详情：", removal_effects_dict)

# 备注说明
st.markdown("""
**说明**：
- 转移概率热力图展示了渠道间状态转移的可能性。
- 移除效应系数表示删除该渠道后对转化率的影响程度，数值越高说明该渠道越重要。
""")