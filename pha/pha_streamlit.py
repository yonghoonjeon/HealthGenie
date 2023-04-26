import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from PIL import Image, ImageDraw, ImageFont
import httpx
import pypistats
import requests
import streamlit as st
import yaml
import psycopg2
from bs4 import BeautifulSoup
from markdownlit import mdlit
from stqdm import stqdm
import cv2
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
# from streamlit_dimensions import st_dimensions
from streamlit_pills import pills
import base64
# 세라 추가
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# from streamlit_profiler import Profiler

# profiler = Profiler()


# 페이지 기본 설정
# st.set_page_config("Health Genie", "🧞‍♂️", layout="wide")
st.set_page_config("Health Genie", layout="wide")
st.markdown("# Health Genie 🧞‍♂️")
NUM_COLS = 3

# st.header("Health Genie 🧞‍♂️")


def icon(emoji: str): # icon 함수는 문자열 형식의 이모지를 인자로 받아, Notion 페이지 아이콘과 같은 큰 크기의 이모지를 스크린에 표시
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

# st.write 함수는 HTML 스타일 시트를 지정하는 문자열을 인자로 받아, Streamlit 애플리케이션에서 특정 HTML 엘리먼트의 스타일을 변경
st.write(
    '<style>button[title="View fullscreen"], h4 a {display: none !important} [data-testid="stImage"] img {border: 1px solid #D6D6D9; border-radius: 3px; height: 200px; object-fit: cover; width: 100%} .block-container img:hover {}</style>',
    unsafe_allow_html=True,
)
# with container:
# icon("🧞‍♂️")

description_text = """
**Data-based personalized health guidance service.**
"""

description = st.empty()
description.write(description_text.format("all"))
col1, col2 = st.columns([2, 1])

# daye 수정 
uploaded_file = col1.file_uploader("Please upload a picture of the food you ate today.", type=['jpg', 'png', 'jpeg'])

row1_space, row1, row2_space, row2, row3_space, row3, row4_space = st.columns(
    (0.1, 2, 0.1, 2, 0.1, 2, 0.1)
)

food_class = "burrito"
probability = "1.0"

if uploaded_file is not None:

    with row1:
        # Display the result of foodAPI on a Streamlit web page
        st.subheader("Food Classification Result")

        #src_image = load_image(uploaded_file)
        image = Image.open(uploaded_file)	
        
        st.image(uploaded_file, caption='Input Image', use_column_width=True)
        #st.write(os.listdir())
        # im = imgGen2(uploaded_file)	
        # st.image(im, caption='ASCII art', use_column_width=True) 

        # daye 수정 
        image = np.array(image)

        # we can also modify image like by yolov5 here 

        #uploaded_img = cv2.imread(img_array)
        image_path = './image.png'
        #need to store image first to change it into url address 
        cv2.imwrite(image_path, image)

        # for one image (you need to change this if you want to put a list)

        # Open the PNG image file as binary
        with open(image_path, "rb") as image_file:
            # Read the binary data from the image file
            image_data = image_file.read()

            # Encode the binary image data as base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Construct the URL for the encoded image data
            image_url = f"data:image/png;base64,{image_base64}"


        # API key for Spoonacular API
        api_key = "d9b5f98d641f40748fb64aa423495b87"

        # API url
        input_url = 'https://api.spoonacular.com/food/images/classify'

        # classify it using the Spoonacular API
    
        # Define the API endpoint and query parameters
        params = {'apiKey': api_key, 'imageUrl': image_url}

        # Send a GET request to the API endpoint and store the response
        response = requests.get(input_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the data from the response
            data = response.json()
            # Do something with the data (e.g. display it in a Streamlit app)
            
            #Get the class of the food item with the highest probability 
            food_class = data['category']

            # Get the probability of the predicted class 
            probability = data['probability']
            
        
        else:
            # If the request was not successful, display an error message
            st.error(f"Request error: {response.status_code}")

        description_text = "The image is classified as {} with a probability of {}" 
        description = st.empty()
        description.write(description_text.format(food_class, probability))
    
    with row2:
        st.subheader("Today's Calorie Analysis")
        
        #connection_info = "host=147.47.200.145 dbname=pha user=dayelee password=0847 port=5432"

        # PostgreSQL 연결
        conn = psycopg2.connect(
            host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
            database = 'pha_test',
            user = 'user',
            password = '--'
        )

        # 칼로리 분석 정보 가져오기
        # we need to change here to get real-time data from the request result 
        query = "select f_name, calories, protein, fat, carbs from pha_food where f_name = 'burrito'; "
        cur = conn.cursor()
        cur.execute(query)
        cal_info = cur.fetchall()

        # Convert data to pandas dataframe
        df = pd.DataFrame(data=cal_info, columns=['food name', 'calories', 'protein', 'fat', 'carbs'])
        #st.dataframe(df)
        calories = int(df['calories'].iloc[0])
        protein = int(df['protein'].iloc[0])
        fat = int(df['fat'].iloc[0])
        carbs = int(df['carbs'].iloc[0])

        st.markdown(
            "For this meal, you consumed **{} kcal from carbs, {} kcal from protein, and {} kcal from fat. Total calories are {} kcal.**".format(
                carbs, protein, fat, calories
            )
        )

        fig = make_subplots(rows=1, cols=1)

        fig.add_trace(go.Bar(x=["calories", "Carbs", "Protein", "Fat"], y=[calories, carbs, protein, fat], width=0.5, marker=dict(color=['#7DB7FE', '#1f77b4', '#1f77b4', '#1f77b4'])))
        # fig.add_trace(go.Bar(x=["calories", "Carbs", "Protein", "Fat"], y=[calories, carbs, protein, fat], width=0.5, marker=dict(color=['#1f77b4', '#7DB7FE', '#7DB7FE', '#7DB7FE'])))
        
        fig.update_layout(title='📊 Calorie Analysis')

        # st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig)

    with row2:
        st.subheader("Diet Recommendations")


        query = "select pha_food.f_name as food_name from (select pha_meal.meals_id, pha_meal.food_id_id from pha_meal join (select * from pha_project join pha_user on pha_project.user_id = pha_user.us_id where pha_project.is_achieved = true) as temp on temp.user_id = pha_meal.user_id where temp.goal_bmi = 23) as curr join pha_food on pha_food.food_id = curr.food_id_id where curr.food_id_id = pha_food.food_id limit 3;" # 쿼리문 수정
        cur = conn.cursor()
        cur.execute(query)
        #recommendation_info = cur.fetchone()[0] # SQL DB에서 실행된 쿼리 결과 중 첫번째 행을 가져오는 메서드, 이 메서드는 가져온 결과를 튜플로 반환 / data = cur.fetchall()
        recommendation_info = cur.fetchall()

        # Convert data to pandas dataframe
        df = pd.DataFrame(data = recommendation_info, columns=['food_name'])

        try:
            st.markdown(
                "Today's recommended meal is {}, {}. {}.".format(
                    df['food_name'].iloc[0],df['food_name'].iloc[1], df['food_name'].iloc[2]
                )
            )
        except IndexError:
            st.warning("이번에는 추천할 식단이 없습니다 🥲")


    with row2: 
        # 소정 파트 추가
        st.subheader("My Goal")

        # PostgreSQL 연결
        conn = psycopg2.connect(
            host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
            database = 'pha_test',
            user = 'user',
            password = '--'
        )

        # (나중에 구현할 내용) 스키마 수정 후 몸무게를 추적해서 '몸무게 변화량'을 선 그래프로 나타낼 수 있도록 해야 함
        # (나중에 구현할 내용) 접속하고 있는 사용자의 user_id를 자동으로 user 변수에 저장할 수 있도록 해야 함 
        # user = ##
        # query = f'select p_name, goal_weight from pha_project where user_id = \'{user}\''

        # 아래는 예시로 user_id = 11 인 경우에 대해 쿼리를 작성함
        # 몸무게 정보 가져오기 / 몸무게 비교
        query = "select p_name, goal_weight from pha_project where user_id = '11'; "
        
        cur = conn.cursor()
        cur.execute(query)
        goal_weight_info = cur.fetchall()

        st.markdown("Select the project you'd like to compare your current weight to your goal weight.")

        # Convert data to pandas dataframe
        df = pd.DataFrame(data=goal_weight_info, columns=['p_name', 'goal_weight'])

        # st.selectbox()를 사용하여 하나의 p_name을 선택
        selected_project = st.selectbox("[Your project list]", options=df['p_name'].unique())

        # 선택된 p_name에 해당하는 goal_weight를 goal_weight라는 변수에 저장
        goal_weight = df.loc[df['p_name'] == selected_project, 'goal_weight'].values[0]
        # st.write(f"{selected_project}: {goal_weight}")

        query = "select weight from pha_user where us_id = '11'"
        cur = conn.cursor()
        cur.execute(query)
        current_weight_info = cur.fetchall()
        df = pd.DataFrame(data=current_weight_info, columns=['weight'])
        current_weight = int(df['weight'].iloc[0])

        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(x=["goal_weight", "current_weight"], y=[goal_weight, current_weight], width=0.5, marker=dict(color=['#7DB7FE', '#1f77b4', '#1f77b4', '#1f77b4'])))
        fig.update_layout(title='📊 Weight comparison')

        # st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig)  

        # 몸무게 비교 결과에 대한 간략한 report
        if goal_weight < current_weight:
            weight_diff = current_weight - goal_weight
            st.write(f"Your current weight is ({weight_diff}) kg higher than your goal weight. Let's try a little harder!")
        elif goal_weight > current_weight:
            weight_diff = goal_weight - current_weight
            st.markdown(f"Your current weight is ({weight_diff}) kg lower than your goal weight.")
            # 체중 감소에 대한 문구 더 추가하기

        # 나중에 구현할 내용 : 몸무게 변화 추세 변화에 대한 간략한 설명  
    
    #     query = "select max(칼로리) from nutrients" # 쿼리문 수정
    #     cur = conn.cursor()
    #     cur.execute(query)
    #     goal_info = cur.fetchone()[0] # SQL DB에서 실행된 쿼리 결과 중 첫번째 행을 가져오는 메서드, 이 메서드는 가져온 결과를 튜플로 반환 / data = cur.fetchall()

    #     # Convert data to pandas dataframe
    #     df = pd.DataFrame(goal_info, columns=['title', 'author', 'read_at_year'])

    #     # plots a bar chart of the dataframe df by book.publication year by count in plotly. columns are publication year and count
    #     year_author_df.columns = ["Percentage"]
    #     year_author_df.reset_index(inplace=True)
    #     year_author_df = year_author_df[year_author_df["read_at_year"] != ""]
    #     year_author_df["read_at_year"] = pd.to_datetime(year_author_df["read_at_year"])
    
    #     # plot line plot in plotly of year_author_df with x axis as read_at_year, y axis is percentage, color is author gender
    #     fig = px.line(
    #     year_author_df,
    #     x="read_at_year",
    #     y="Percentage",
    #     color="author_gender",
    #     title="Percent of Books by Gender Over Time",
    #     )
    #     fig.update_xaxes(title_text="Year Read")
    #     st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    #     st.markdown(
    #         "Looks like the average publication date is around **{}**, with your oldest book being **{}** and your youngest being **{}**.".format(
    #             avg_book_year, oldest_book, youngest_book
    #         )
    #     )
    #     st.markdown(
    #         "Note that the publication date on Goodreads is the **last** publication date, so the data is altered for any book that has been republished by a publisher."
    #     )


