import streamlit as st

st.title("제곱근 계산기")

num = st.number_input("숫자를 입력하세요")
sqrt = num ** 0.5

st.write("제곱근:", sqrt)
