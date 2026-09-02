import streamlit as st

home_page = st.Page(
    page="pages/home.py",
    title="🏠主页",
    icon=":material/home:"
)

user_profile_page = st.Page(
    page="pages/user_profile.py",
    title="👤用户画像",
    icon=":material/person:"
)

rfm_page = st.Page(
    page="pages/rfm_analysis.py",
    title="📈RFM分析",
    icon=":material/leaderboard:"
)

ltv_page = st.Page(
    page="pages/ltv_analysis.py",
    title="💰预测LTV",
    icon=":material/attach_money:"
)

channel_page = st.Page(
    page="pages/channel_analysis.py",
    title="📊渠道分析",
    icon=":material/analytics:"
)

funnel_page = st.Page(
    page="pages/funnel_analysis.py",
    title="🔽漏斗分析",
    icon=":material/funnel:"
)

retention_page = st.Page(
    page="pages/retention.py",
    title="🔄留存曲线",
    icon=":material/update:"
)

recommend_page = st.Page(
    page="pages/recommendation.py",
    title="🎯推荐系统",
    icon=":material/recommend:"
)

pg = st.navigation(
    {
        "项目概览": [home_page],
        "用户行为分析": [channel_page, funnel_page, retention_page],
        "价值与推荐": [ltv_page, rfm_page, recommendation_page],
        "用户画像": [user_profile_page]
    }
)

# ---------- 3. 运行当前选中的页面 ----------
pg.run()