import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# =========================
# 1. 页面设置
# =========================

st.set_page_config(
    page_title="用户画像分析",
    page_icon="📊",
    layout="wide"
)

# 中文字体
from matplotlib import font_manager

font_path = "NotoSansSC-VariableFont_wght.ttf"

font_manager.fontManager.addfont(font_path)

font_name = font_manager.FontProperties(
    fname=font_path
).get_name()

plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


# =========================
# 2. 读取数据
# =========================

df_user = pd.read_csv(
    "爆款产品.csv",
    encoding="utf8"
)


# =========================
# 3. 页面标题
# =========================

st.title("用户画像分析")
st.caption("基于用户特征与购买行为的数据分析")


# =========================
# 4. Sidebar 筛选器
# =========================

st.sidebar.header("筛选条件")

# 性别
gender_options = ["全部"] + sorted(
    df_user["性别"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "性别",
    gender_options
)

# 状态
status_options = ["全部"] + sorted(
    df_user["状态"].dropna().unique().tolist()
)

selected_status = st.sidebar.selectbox(
    "用户状态",
    status_options
)

# 产品
product_options = ["全部"] + sorted(
    df_user["近期购买产品"].dropna().unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "近期购买产品",
    product_options
)


# =========================
# 5. 根据筛选条件过滤数据
# =========================

df_filtered = df_user.copy()

if selected_gender != "全部":
    df_filtered = df_filtered[
        df_filtered["性别"] == selected_gender
    ]

if selected_status != "全部":
    df_filtered = df_filtered[
        df_filtered["状态"] == selected_status
    ]

if selected_product != "全部":
    df_filtered = df_filtered[
        df_filtered["近期购买产品"] == selected_product
    ]


# =========================
# 6. KPI
# =========================

st.subheader("用户数据概览")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "总用户数",
    len(df_filtered)
)

col2.metric(
    "平均年龄",
    round(df_filtered["年龄"].mean(), 1)
)

col3.metric(
    "平均下单次数",
    round(df_filtered["下单次数"].mean(), 1)
)

col4.metric(
    "平均年消费",
    round(df_filtered["年消费"].mean(), 2)
)


# =========================
# 7. Customer Demographics
# =========================

st.subheader("用户基本特征")

col1, col2 = st.columns(2)


# 年龄分布
with col1:

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.histplot(
        df_filtered["年龄"],
        kde=True,
        ax=ax
    )

    ax.set_title("年龄分布")
    ax.set_xlabel("年龄")
    ax.set_ylabel("用户数量")

    st.pyplot(fig)


# 性别分布
with col2:

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.countplot(
        x="性别",
        data=df_filtered,
        ax=ax
    )

    ax.set_title("性别分布")
    ax.set_xlabel("性别")
    ax.set_ylabel("用户数量")

    st.pyplot(fig)


# =========================
# 8. Purchase Behavior
# =========================

st.subheader("购买行为")

col1, col2 = st.columns(2)


# 产品偏好
with col1:

    product_counts = (
        df_filtered["近期购买产品"]
        .value_counts()
    )

    st.bar_chart(product_counts)


# 下单次数
with col2:

    order_counts = (
        df_filtered["下单次数"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(order_counts)


# =========================
# 9. Product × Gender
# =========================

st.subheader("不同性别的产品偏好")

fig, ax = plt.subplots(figsize=(10, 5))

sns.countplot(
    x="近期购买产品",
    hue="性别",
    data=df_filtered,
    ax=ax
)

ax.set_xlabel("近期购买产品")
ax.set_ylabel("用户数量")

plt.xticks(rotation=30)
plt.tight_layout()

st.pyplot(fig)


# =========================
# 10. Customer Status
# =========================

st.subheader("用户状态")

status_table = pd.pivot_table(
    df_filtered,
    values="用户编号",
    index="性别",
    columns="状态",
    aggfunc="count",
    fill_value=0
)

st.dataframe(
    status_table,
    use_container_width=True
)


# =========================
# 11. Selected Product Analysis
# =========================

st.subheader("产品分析")

if selected_product != "全部":

    df_product = df_filtered[
        df_filtered["近期购买产品"] == selected_product
    ]

    col1, col2 = st.columns(2)

    with col1:

        fig, ax = plt.subplots(figsize=(7, 5))

        sns.histplot(
            df_product["年龄"],
            kde=True,
            ax=ax
        )

        ax.set_title(
            f"{selected_product} - 年龄分布"
        )

        ax.set_xlabel("年龄")
        ax.set_ylabel("用户数量")

        st.pyplot(fig)

    with col2:

        fig, ax = plt.subplots(figsize=(7, 5))

        sns.countplot(
            x="年龄",
            hue="性别",
            data=df_product,
            ax=ax
        )

        ax.set_title(
            f"{selected_product} - 不同性别的年龄分布"
        )

        ax.set_xlabel("年龄")
        ax.set_ylabel("用户数量")

        plt.xticks(rotation=30)
        plt.tight_layout()

        st.pyplot(fig)

else:

    st.info(
        "请从左侧筛选栏选择一个产品，以查看详细的产品分析。"
    )