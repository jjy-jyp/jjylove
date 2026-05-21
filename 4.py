import streamlit as st
import snownlp
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -------------------------- 1. 页面基础配置（放在最开头！） --------------------------
st.set_page_config(
    page_title="中文情感&分词分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 2. 初始化会话状态（保存历史记录） --------------------------
if "history" not in st.session_state:
    st.session_state["history"] = []
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

# -------------------------- 3. 美化标题与说明 --------------------------
st.markdown("""
    <div style="text-align: center; padding: 25px; background-color: #f8f9fa; border-radius: 12px; margin-bottom: 30px;">
        <h1 style="color: #1f77b4; margin: 0;">📊 中文情感&分词分析工具</h1>
        <p style="color: #666; font-size: 16px; margin-top: 10px;">基于 SnowNLP 的轻量级中文自然语言处理工具，支持分词、情感分析、关键词提取与词云生成</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------- 4. 侧边栏功能区 --------------------------
with st.sidebar:
    st.header("⚙️ 功能设置")
    
    # 示例文本按钮
    if st.button("试试示例文本"):
        st.session_state["input_text"] = "今天天气真好，和朋友一起去公园散步，心情特别愉快！"
    
    st.divider()
    
    # 批量分析：上传TXT文件
    st.subheader("📁 批量分析（上传文件）")
    uploaded_file = st.file_uploader("上传TXT文件（每行一句）", type="txt")
    
    if uploaded_file is not None:
        text_list = uploaded_file.read().decode("utf-8").splitlines()
        st.success(f"已加载 {len(text_list)} 条文本")
        
        if st.button("开始批量分析"):
            results = []
            with st.spinner("正在批量分析中..."):
                for i, text in enumerate(text_list):
                    if not text.strip():
                        continue
                    s = snownlp.SnowNLP(text)
                    sentiment = s.sentiments
                    sentiment_label = "正面" if sentiment > 0.6 else "负面" if sentiment < 0.4 else "中性"
                    results.append({
                        "序号": i+1,
                        "原文": text,
                        "分词结果": " | ".join(s.words),
                        "情感极性": sentiment_label,
                        "置信度": round(sentiment, 2)
                    })
            
            # 显示批量分析结果
            st.subheader("📋 批量分析结果")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # 下载结果
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 下载分析结果（CSV）",
                data=csv,
                file_name="情感分析结果.csv",
                mime="text/csv"
            )
            
            # 情感分布可视化
            st.subheader("📈 情感分布统计")
            sentiment_counts = df["情感极性"].value_counts()
            st.bar_chart(sentiment_counts, use_container_width=True)

    st.divider()
    
    # 历史记录
    st.header("📚 分析历史")
    if st.session_state["history"]:
        for record in st.session_state["history"]:
            with st.expander(f"{record['时间']}：{record['文本'][:15]}..."):
                st.write(f"情感极性：{record['情感极性']}（置信度：{record['置信度']}）")
                st.write(f"分词结果：{record['分词结果']}")
    else:
        st.info("暂无历史记录，开始分析后会自动保存哦~")

# -------------------------- 5. 主界面：单文本分析 --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("✏️ 单文本分析")
    text = st.text_area(
        "请输入要分析的中文文本：",
        value=st.session_state["input_text"],
        height=150,
        placeholder="例如：今天天气真好，心情也跟着变好了！"
    )
    
    analyze_btn = st.button("开始分析", type="primary", use_container_width=True)

with col2:
    st.subheader("💡 使用说明")
    st.markdown("""
    - 支持输入中文句子/段落，自动分词和情感分析
    - 可上传TXT文件批量处理，结果支持下载
    - 情感极性判断标准：
      - 置信度 > 0.6：正面
      - 置信度 < 0.4：负面
      - 0.4 ~ 0.6：中性
    """)

st.divider()

# -------------------------- 6. 分析结果展示 --------------------------
if analyze_btn and text.strip():
    with st.spinner("正在分析中..."):
        s = snownlp.SnowNLP(text)
        words = s.words
        sentiment = s.sentiments
        keywords = s.keywords(limit=10)  # 提取前10个关键词
        
        # 保存到历史记录
        st.session_state["history"].append({
            "时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "文本": text,
            "情感极性": "正面" if sentiment > 0.6 else "负面" if sentiment < 0.4 else "中性",
            "置信度": round(sentiment, 2),
            "分词结果": " | ".join(words)
        })
        
        # 结果卡片
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            st.markdown("""
                <div style="padding: 20px; background-color: #f0f8ff; border-radius: 10px;">
                    <h4 style="color: #1f77b4;">📝 分词结果</h4>
                    <p style="font-size: 16px; line-height: 1.6;">{}</p>
                </div>
            """.format(" | ".join(words)), unsafe_allow_html=True)
            
            st.markdown("""
                <div style="padding: 20px; background-color: #fff8e1; border-radius: 10px; margin-top: 20px;">
                    <h4 style="color: #ff9800;">🔑 关键词提取</h4>
                    <p style="font-size: 16px; line-height: 1.6;">{}</p>
                </div>
            """.format(" | ".join(keywords)), unsafe_allow_html=True)
        
        with col_result2:
            st.markdown("""
                <div style="padding: 20px; background-color: #f0f9eb; border-radius: 10px;">
                    <h4 style="color: #2e7d32;">💬 情感分析结果</h4>
                    <p style="font-size: 18px; font-weight: bold;">情感极性：{}</p>
                    <p style="font-size: 16px;">置信度：{:.2f}</p>
                </div>
            """.format(
                "正面 😊" if sentiment > 0.6 else "负面 😔" if sentiment < 0.4 else "中性 😐",
                sentiment
            ), unsafe_allow_html=True)
        
        # 词云生成
        if keywords:
            st.subheader("☁️ 关键词词云")
            try:
                # 生成词云（使用内置字体，避免部署时找不到文件）
                wordcloud = WordCloud(
                    font_path="simhei.ttf",  # Streamlit 环境已预装，无需额外上传
                    background_color="white",
                    width=800,
                    height=400,
                    max_words=100
                ).generate(" ".join(keywords))
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, use_container_width=True)
            except:
                st.warning("词云生成失败，可能是字体问题，不影响其他功能使用~")

elif analyze_btn and not text.strip():
    st.warning("⚠️ 请输入文本后再进行分析哦！")
