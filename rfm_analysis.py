import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
import os

# ===================== 字体设置（使用相对路径） =====================
FONT_PATH = "NotoSansSC-VariableFont_wght.ttf"  # 确保此文件在仓库根目录

# 加载字体
fm.fontManager.addfont(FONT_PATH)
font_prop = fm.FontProperties(fname=FONT_PATH)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False
# ================================================================

# 页面配置
st.set_page_config(page_title="RFM 客户价值分析", layout="wide")

@st.cache_data
def load_and_preprocess(file_path="电商历史订单.csv"):
    df = pd.read_csv(file_path, encoding='utf8')
    df = df[df['数量'] > 0].copy()
    df['总价'] = df['数量'] * df['单价']
    df['消费日期'] = pd.to_datetime(df['消费日期'])
    df['年'] = df['消费日期'].dt.year
    df['月'] = df['消费日期'].dt.month
    return df

@st.cache_data
def compute_rfm(df):
    recent_buy = df.groupby('用户码')['消费日期'].max().reset_index()
    recent_buy.columns = ['用户码', '最近日期']
    latest_date = df['消费日期'].max()
    recent_buy['R值'] = (latest_date - recent_buy['最近日期']).dt.days

    frequency = df.groupby('用户码').size().reset_index(name='F值')
    monetary = df.groupby('用户码')['总价'].sum().reset_index(name='M值')

    rfm = pd.merge(recent_buy[['用户码', 'R值']], frequency, on='用户码')
    rfm = pd.merge(rfm, monetary, on='用户码')
    return rfm

@st.cache_data
def cluster_rfm(rfm):
    # R值聚类（k=3）
    rfm_r = rfm[['用户码', 'R值']].copy()
    kmeans_r = KMeans(n_clusters=3, random_state=42, n_init=10)
    rfm_r['R值层级'] = kmeans_r.fit_predict(rfm_r[['R值']])
    cluster_means_r = rfm_r.groupby('R值层级')['R值'].mean().sort_values(ascending=False)
    rfm_r['R值层级'] = rfm_r['R值层级'].map({cluster_means_r.index[0]: 0, cluster_means_r.index[1]: 1, cluster_means_r.index[2]: 2})
    rfm['R值层级'] = rfm_r['R值层级']

    # F值聚类（k=4）
    rfm_f = rfm[['用户码', 'F值']].copy()
    kmeans_f = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm_f['F值层级'] = kmeans_f.fit_predict(rfm_f[['F值']])
    cluster_means_f = rfm_f.groupby('F值层级')['F值'].mean().sort_values(ascending=True)
    rfm_f['F值层级'] = rfm_f['F值层级'].map({cluster_means_f.index[0]: 0, cluster_means_f.index[1]: 1, cluster_means_f.index[2]: 2, cluster_means_f.index[3]: 3})
    rfm['F值层级'] = rfm_f['F值层级']

    # M值聚类（k=4）
    rfm_m = rfm[['用户码', 'M值']].copy()
    kmeans_m = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm_m['M值层级'] = kmeans_m.fit_predict(rfm_m[['M值']])
    cluster_means_m = rfm_m.groupby('M值层级')['M值'].mean().sort_values(ascending=True)
    rfm_m['M值层级'] = rfm_m['M值层级'].map({cluster_means_m.index[0]: 0, cluster_means_m.index[1]: 1, cluster_means_m.index[2]: 2, cluster_means_m.index[3]: 3})
    rfm['M值层级'] = rfm_m['M值层级']

    rfm['总分'] = rfm['R值层级'] + rfm['F值层级'] + rfm['M值层级']
    rfm['总体价值'] = pd.cut(rfm['总分'], bins=[-1, 2, 4, 8], labels=['低价值', '中价值', '高价值'])
    return rfm

def main():
    st.title("📊 RFM 客户价值分析")
    st.markdown("基于历史订单数据，通过 R（近度）、F（频度）、M（额度）三个维度进行客户分群。")

    with st.spinner("正在加载数据..."):
        df = load_and_preprocess()
        rfm = compute_rfm(df)
        rfm = cluster_rfm(rfm)

    st.sidebar.header("数据概览")
    st.sidebar.write(f"总订单数: {len(df)}")
    st.sidebar.write(f"唯一用户数: {rfm['用户码'].nunique()}")
    st.sidebar.write(f"日期范围: {df['消费日期'].min().date()} 至 {df['消费日期'].max().date()}")

    with st.expander("查看原始数据（前100行）"):
        st.dataframe(df.head(100))

    st.subheader("📈 月销售额趋势")
    monthly_sales = df.groupby(['年', '月'])['总价'].sum().reset_index()
    monthly_sales['年月'] = monthly_sales['年'].astype(str) + '-' + monthly_sales['月'].astype(str).str.zfill(2)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(monthly_sales['年月'], monthly_sales['总价'], color='skyblue')
    ax.set_xlabel("年月")
    ax.set_ylabel("总销售额")
    ax.set_title("每月销售额")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("🏙️ 各地销售额")
    city_sales = df.groupby('城市')['总价'].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(city_sales.index, city_sales.values, color='lightgreen')
    ax2.set_xlabel("城市")
    ax2.set_ylabel("总销售额")
    ax2.set_title("各地销售额")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.subheader("📊 RFM 层级分布")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**R值层级分布**")
        st.bar_chart(rfm['R值层级'].value_counts().sort_index())
    with col2:
        st.write("**F值层级分布**")
        st.bar_chart(rfm['F值层级'].value_counts().sort_index())
    with col3:
        st.write("**M值层级分布**")
        st.bar_chart(rfm['M值层级'].value_counts().sort_index())

    st.subheader("🏷️ 客户价值分布")
    value_counts = rfm['总体价值'].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', colors=['gold', 'silver', 'lightcoral'])
    ax3.set_title("客户价值占比")
    st.pyplot(fig3)

    st.subheader("🔍 F值与M值关系（颜色表示价值）")
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    for val in ['高价值', '中价值', '低价值']:
        subset = rfm[rfm['总体价值'] == val]
        ax4.scatter(subset['F值'], subset['M值'], label=val, alpha=0.6, s=30)
    ax4.set_xlabel("F值（消费频次）")
    ax4.set_ylabel("M值（消费金额）")
    ax4.legend()
    st.pyplot(fig4)

    st.subheader("🌐 3D 散点图（R-F-M）")
    fig5 = plt.figure(figsize=(10, 8))
    ax5 = fig5.add_subplot(111, projection='3d')
    for val, color, marker in [('高价值', 'gold', '*'), ('中价值', 'silver', 'o'), ('低价值', 'lightcoral', '^')]:
        subset = rfm[rfm['总体价值'] == val]
        ax5.scatter(subset['R值'], subset['F值'], subset['M值'], c=color, marker=marker, label=val, s=20)
    ax5.set_xlabel('R值')
    ax5.set_ylabel('F值')
    ax5.set_zlabel('M值')
    ax5.legend()
    st.pyplot(fig5)

    st.subheader("⭐ VIP 用户（总分最高）")
    top_users = rfm[rfm['总分'] == rfm['总分'].max()]
    if not top_users.empty:
        st.write(f"共有 {len(top_users)} 位用户达到最高分 {rfm['总分'].max()}")
        st.dataframe(top_users[['用户码', 'R值', 'F值', 'M值', '总分', '总体价值']])
    else:
        st.write("未找到高分用户")

    with st.expander("查看完整RFM表"):
        st.dataframe(rfm)

if __name__ == "__main__":
    main()