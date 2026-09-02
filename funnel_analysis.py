import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(page_title="促销漏斗分析", layout="wide")
st.title("📊促销漏斗分析Dashboard")

# 缓存数据加载函数
@st.cache_data
def load_data():
    df_user = pd.read_csv('00用户表.csv')
    df_homepage = pd.read_csv('01登录页.csv')
    df_search = pd.read_csv('02搜索页.csv')
    df_lucky = pd.read_csv('03幸运轮盘.csv')
    df_payment = pd.read_csv('04付款页.csv')
    df_confirm = pd.read_csv('05确认付款.csv')
    return df_user, df_homepage, df_search, df_lucky, df_payment, df_confirm

@st.cache_data
def merge_data(df_user, df_homepage, df_search, df_lucky, df_payment, df_confirm):
    df_all = df_user.merge(df_homepage, how='outer', on='用户码') \
                    .merge(df_search, how='outer', on='用户码') \
                    .merge(df_lucky, how='outer', on='用户码') \
                    .merge(df_payment, how='outer', on='用户码') \
                    .merge(df_confirm, how='outer', on='用户码')
    return df_all

# 加载数据
try:
    df_user, df_homepage, df_search, df_lucky, df_payment, df_confirm = load_data()
    df_all = merge_data(df_user, df_homepage, df_search, df_lucky, df_payment, df_confirm)
except FileNotFoundError:
    st.error("请确保所有CSV数据文件（00用户表.csv, 01登录页.csv, ...）与app.py放在同一目录下。")
    st.stop()

# 计算各步骤人数
steps = ['促销页', '搜索页', '幸运轮盘', '付款页', '确认付款']
# 各步骤对应的DataFrame和列名
step_dfs = [df_homepage, df_search, df_lucky, df_payment, df_confirm]
counts = [df['用户码'].count() for df in step_dfs]

# 创建漏斗图函数
def create_funnel(y_labels, x_values, title, name=None):
    fig = go.Figure(go.Funnel(
        y=y_labels,
        x=x_values,
        name=name
    ))
    fig.update_layout(title=title, height=500)
    return fig

# 侧边栏选择查看维度
view_option = st.sidebar.radio(
    "选择查看维度",
    ("总体", "按性别", "按客户端")
)

# 总体漏斗
if view_option == "总体":
    fig = create_funnel(steps, counts, "总体促销漏斗")
    st.plotly_chart(fig, use_container_width=True)

    # 显示转化率
    st.subheader("各步骤转化率")
    total = counts[0]
    conversion = [count/total for count in counts]
    df_conv = pd.DataFrame({
        "步骤": steps,
        "人数": counts,
        "转化率": [f"{c*100:.2f}%" for c in conversion]
    })
    st.dataframe(df_conv, use_container_width=True)

# 按性别细分
elif view_option == "按性别":
    st.subheader("按性别细分漏斗")
    # 计算男女各步骤人数
    # 步骤1 促销页
    step1_male = ((df_all['性别'] == '男') & (df_all['步骤1'] == '促销页')).sum()
    step1_female = ((df_all['性别'] == '女') & (df_all['步骤1'] == '促销页')).sum()
    step2_male = ((df_all['性别'] == '男') & (df_all['步骤2'] == '搜索页')).sum()
    step2_female = ((df_all['性别'] == '女') & (df_all['步骤2'] == '搜索页')).sum()
    step3_male = ((df_all['性别'] == '男') & (df_all['步骤3'] == '幸运轮盘')).sum()
    step3_female = ((df_all['性别'] == '女') & (df_all['步骤3'] == '幸运轮盘')).sum()
    step4_male = ((df_all['性别'] == '男') & (df_all['步骤4'] == '付款页')).sum()
    step4_female = ((df_all['性别'] == '女') & (df_all['步骤4'] == '付款页')).sum()
    step5_male = ((df_all['性别'] == '男') & (df_all['步骤5'] == '确认付款')).sum()
    step5_female = ((df_all['性别'] == '女') & (df_all['步骤5'] == '确认付款')).sum()

    male_counts = [step1_male, step2_male, step3_male, step4_male, step5_male]
    female_counts = [step1_female, step2_female, step3_female, step4_female, step5_female]

    trace_male = go.Funnel(y=steps, x=male_counts, name='男')
    trace_female = go.Funnel(y=steps, x=female_counts, name='女')
    fig = go.Figure([trace_male, trace_female])
    fig.update_layout(title="促销漏斗: 性别细分", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # 也可显示转化率对比
    st.subheader("各性别转化率对比")
    male_conv = [m/male_counts[0] if male_counts[0]>0 else 0 for m in male_counts]
    female_conv = [f/female_counts[0] if female_counts[0]>0 else 0 for f in female_counts]
    df_gender = pd.DataFrame({
        "步骤": steps,
        "男性人数": male_counts,
        "女性人数": female_counts,
        "男性转化率": [f"{c*100:.2f}%" for c in male_conv],
        "女性转化率": [f"{c*100:.2f}%" for c in female_conv]
    })
    st.dataframe(df_gender, use_container_width=True)

# 按客户端细分
elif view_option == "按客户端":
    st.subheader("按客户端细分漏斗")
    # 电脑和手机
    step1_computer = ((df_all['客户端'] == '电脑') & (df_all['步骤1'] == '促销页')).sum()
    step1_phone = ((df_all['客户端'] == '手机') & (df_all['步骤1'] == '促销页')).sum()
    step2_computer = ((df_all['客户端'] == '电脑') & (df_all['步骤2'] == '搜索页')).sum()
    step2_phone = ((df_all['客户端'] == '手机') & (df_all['步骤2'] == '搜索页')).sum()
    step3_computer = ((df_all['客户端'] == '电脑') & (df_all['步骤3'] == '幸运轮盘')).sum()
    step3_phone = ((df_all['客户端'] == '手机') & (df_all['步骤3'] == '幸运轮盘')).sum()
    step4_computer = ((df_all['客户端'] == '电脑') & (df_all['步骤4'] == '付款页')).sum()
    step4_phone = ((df_all['客户端'] == '手机') & (df_all['步骤4'] == '付款页')).sum()
    step5_computer = ((df_all['客户端'] == '电脑') & (df_all['步骤5'] == '确认付款')).sum()
    step5_phone = ((df_all['客户端'] == '手机') & (df_all['步骤5'] == '确认付款')).sum()

    comp_counts = [step1_computer, step2_computer, step3_computer, step4_computer, step5_computer]
    phone_counts = [step1_phone, step2_phone, step3_phone, step4_phone, step5_phone]

    trace_comp = go.Funnel(y=steps, x=comp_counts, name='电脑')
    trace_phone = go.Funnel(y=steps, x=phone_counts, name='手机')
    fig = go.Figure([trace_comp, trace_phone])
    fig.update_layout(title="促销漏斗: 客户端细分", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # 转化率对比
    st.subheader("各客户端转化率对比")
    comp_conv = [c/comp_counts[0] if comp_counts[0]>0 else 0 for c in comp_counts]
    phone_conv = [p/phone_counts[0] if phone_counts[0]>0 else 0 for p in phone_counts]
    df_client = pd.DataFrame({
        "步骤": steps,
        "电脑人数": comp_counts,
        "手机人数": phone_counts,
        "电脑转化率": [f"{c*100:.2f}%" for c in comp_conv],
        "手机转化率": [f"{c*100:.2f}%" for c in phone_conv]
    })
    st.dataframe(df_client, use_container_width=True)