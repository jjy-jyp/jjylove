import streamlit as st
from snownlp import SnowNLP

st.title("中文情感&分词工具")

# 输入框，支持反复输入
content = st.text_input("请输入文本，持续输入即可多次分析：")

if content:
    s = SnowNLP(content)
    score = s.sentiments

    # 判断情绪
    if score > 0.6:
        emotion = "😊 正面"
    elif score < 0.4:
        emotion = "😠 负面"
    else:
        emotion = "😐 中性"

    words = s.words

    st.divider()
    st.write(f"**情感倾向**：{emotion}  分值：{score:.2f}")
    st.write(f"**分词结果**：{words}")

