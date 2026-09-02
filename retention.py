import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from lifelines import KaplanMeierFitter, CoxPHFitter
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

st.set_page_config(page_title="会员留存分析看板", layout="wide")

from matplotlib import font_manager

font_path = "NotoSansSC-VariableFont_wght.ttf"

font_manager.fontManager.addfont(font_path)

font_name = font_manager.FontProperties(
    fname=font_path
).get_name()

plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

@st.cache_data
def load_data():
    """加载原始数据"""
    df = pd.read_csv("江里捞会员.csv", encoding="utf8")
    return df

@st.cache_data
def preprocess_data(df):
    """数据预处理，返回用于建模的数据框"""
    df = df.copy()
    df["已停付会费"] = df["已停付会费"].map({"是": 1, "否": 0})
    df["性别"] = df["性别"].map({"女": 0, "男": 1})
    binary_features = [
        "家庭套餐优惠", "儿童餐优惠", "特色菜套餐", "酒水套餐",
        "饮料套餐", "甜品套餐", "生日套餐A", "生日套餐B"
    ]
    for col in binary_features:
        df[col] = df[col] == "是"
    df["总消费"] = pd.to_numeric(df["总消费"], errors="coerce").fillna(0)
    df_model = pd.get_dummies(
        df,
        drop_first=True,
        columns=["会员卡类型", "会费支付方式"]
    )
    return df, df_model

def plot_km_curve(df, feature=None, ax=None):
    """绘制Kaplan-Meier曲线，若指定feature则分组绘制"""
    kmf = KaplanMeierFitter()
    if feature is None:
        kmf.fit(df["入会月数"], event_observed=df["已停付会费"], label="整体留存")
        kmf.plot(ax=ax, ci_alpha=0)
    else:
        for cat in df[feature].unique():
            idx = df[feature] == cat
            kmf.fit(
                df.loc[idx, "入会月数"],
                event_observed=df.loc[idx, "已停付会费"],
                label=str(cat)
            )
            kmf.plot(ax=ax, label=str(cat), ci_alpha=0)

def main():
    st.title("📊会员留存分析看板")
    st.markdown("基于Kaplan‑Meier生存分析与Cox比例风险模型，探索用户留存影响因素。")

    with st.spinner("加载数据..."):
        df_raw, df_model = preprocess_data(load_data())
    st.success("数据加载完成！")

    st.sidebar.header("显示选项")
    show_overview = st.sidebar.checkbox("数据概览", True)
    show_km = st.sidebar.checkbox("整体留存曲线", True)
    show_cat_km = st.sidebar.checkbox("分类留存曲线", True)
    show_cox = st.sidebar.checkbox("Cox回归结果", True)
    show_lr = st.sidebar.checkbox("逻辑回归预测", True)

    if show_overview:
        st.subheader("📋数据概览")
        col1, col2 = st.columns(2)
        with col1:
            st.write("前5行数据：")
            st.dataframe(df_raw.head())
        with col2:
            st.write("数据统计：")
            st.dataframe(df_raw.describe(include="all").T)

    if show_km:
        st.subheader("📈 整体留存曲线")
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_km_curve(df_raw, ax=ax)
        ax.set_title("Kaplan‑Meier留存曲线 — 所有用户")
        ax.set_xlabel("入会月数")
        ax.set_ylabel("留存率")
        st.pyplot(fig)

    if show_cat_km:
        st.subheader("📊分类留存曲线")
        cat_features = ["会费支付方式", "会员卡类型", "性别"]
        selected_cat = st.selectbox("选择分类变量", cat_features)
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_km_curve(df_raw, feature=selected_cat, ax=ax)
        ax.set_title(f"不同 {selected_cat} 的留存曲线")
        ax.set_xlabel("入会月数")
        ax.set_ylabel("留存率")
        st.pyplot(fig)

    if show_cox:
        st.subheader("📉Cox比例风险模型")
        with st.spinner("拟合Cox模型..."):
            cph = CoxPHFitter()
            X = df_model.drop(columns=["用户码", "已停付会费"], errors="ignore")
            y = df_model["已停付会费"]
            duration_col = "入会月数"
            event_col = "已停付会费"
            feature_cols = [c for c in df_model.columns if c not in ["用户码", duration_col, event_col]]
            cph.fit(df_model, duration_col=duration_col, event_col=event_col, formula=" + ".join(feature_cols))
        st.write("模型摘要：")
        st.text(cph.print_summary())
        summary_df = cph.summary
        st.dataframe(summary_df)
        fig, ax = plt.subplots(figsize=(12, 7))
        cph.plot(ax=ax)
        st.pyplot(fig)

    if show_lr:
        st.subheader("🤖逻辑回归预测（流失概率）")
        with st.spinner("训练逻辑回归模型..."):
            X = df_model.drop(columns=["用户码", "已停付会费"], errors="ignore")
            y = df_model["已停付会费"]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            lr = LogisticRegression(max_iter=1000)
            lr.fit(X_train, y_train)
            acc = lr.score(X_test, y_test)
            y_pred = lr.predict(X_test)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("测试集准确率", f"{acc:.2%}")
        with col2:
            st.write("测试集第一个样本预测结果：", "流失" if y_pred[0] == 1 else "未流失")
        st.write("特征系数（正数表示增加流失风险）：")
        coef_df = pd.DataFrame({
            "特征": X.columns,
            "系数": lr.coef_[0]
        }).sort_values("系数", ascending=False)
        st.dataframe(coef_df)
        fig, ax = plt.subplots(figsize=(10, 6))
        coef_df_sorted = coef_df.sort_values("系数")
        ax.barh(coef_df_sorted["特征"], coef_df_sorted["系数"])
        ax.set_xlabel("系数")
        ax.set_title("逻辑回归特征系数")
        st.pyplot(fig)

if __name__ == "__main__":
    main()