import streamlit as st

st.set_page_config(page_title="数据看板合集", layout="wide")

st.title("👋你好，我是[姜佩琪]")
st.markdown("""
### 数据分析 & 可视化作品集
欢迎来到我的Streamlit看板合集！这里汇集了我在**用户增长**、**商业智能**和**机器学习应用**方面的多个实践项目。

我擅长：
- **Python / Pandas / NumPy**数据处理
- **Plotly / Altair / Matplotlib**可视化
- **Streamlit**快速构建数据应用
""")

st.divider()
st.subheader("📌项目列表")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **📊渠道分析**  
    多渠道流量归因与转化效率分析，帮助优化预算分配。

    **🔽漏斗分析**  
    用户转化漏斗各阶段流失洞察，定位关键优化环节。

    **💰预测LTV**  
    用户生命周期价值预测，辅助长期盈利策略制定。

    **🎯推荐系统**  
    基于协同过滤的个性化推荐系统演示。
    """)

with col2:
    st.markdown("""
    **🔄留存曲线**  
    用户留存曲线与同期群分析（Cohort Analysis）。

    **📈RFM分析**  
    基于Recency, Frequency, Monetary的用户分层。

    **👤用户画像**  
    用户画像聚合展示，包含人口统计与行为标签。
    """)

st.divider()
st.caption("📧联系我：jzys2003@outlook.com | 🔗 [GitHub](https://github.com/AAAJiannng) | [LinkedIn](www.linkedin.com/in/peiqi-jiang-8181572b9)")