# streamlit hello
import streamlit as st

# connect
import requests
import psycopg2

# data visualization
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import my_db_setting

# date
import datetime
import time 

# food recommendation
from f_recommd_2 import FoodRecommendation
import argparse

# recommended calories calculate 
from recomd_calories import calculate_recommended_calories



#실행 코드 예시 streamlit run final_streamlit.py -- --user_id 4 --project_id 12


####################################################argument ##################

parser = argparse.ArgumentParser(description = "Generate food recommendations for a user.")
parser.add_argument('--user_id', type = int, required=True, help = 'User id')
parser.add_argument('--project_id', type = int, required = True, help = 'project id of the current user_id')
parser.add_argument('--n_recommd_meal', type = int, default = 1, required=False, help = 'The number of meals that user wants to get recommended')

args = parser.parse_args()


################################################## PostgreSQL ##################################################
# PostgreSQL 연결
conn = my_db_setting.my_db_setting()

################################################## Page Title ##################################################
st.set_page_config('Health Genie', '🧞‍♂️', layout='wide')
# 타이틀 적용 예시
# 특수 이모티콘 삽입 예시
# emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.title('Health Genie :genie:')

# Subheader 적용
st.subheader("""
**Data-based personalized health guidance service.**
""")

################################################## Select Project ##################################################
# 오늘 날짜 받아오기
today = datetime.datetime.now()

# 현재 몸무게 보여주기 #####################

# 프로젝트 선택하기
query = f"""SELECT p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
            FROM pha_project
            WHERE user_id = '{args.user_id}' and project_id = '{args.project_id}'"""
        
cur = conn.cursor()
cur.execute(query)
project_info = cur.fetchall()

# Convert data to pandas dataframe
df_project_info = pd.DataFrame(data= project_info, columns=['p_name', 'start_time', 'end_time', 'goal_weight', 'cur_weight', 'goal_type'])


start_time = df_project_info['start_time'].values[0]
end_time = df_project_info['end_time'].values[0]
#start_time = str(start_time)
#end_time = str(end_time)


start_time =time.mktime(time.strptime(start_time[:-3], '%Y-%m-%d %H:%M:%S'))
end_time =time.mktime(time.strptime(end_time[:-3], '%Y-%m-%d %H:%M:%S'))

# 이미 완료된 project인지 진행 중인 project인지 판단 
start_time = datetime.datetime.fromtimestamp(start_time)
end_time = datetime.datetime.fromtimestamp(end_time)

if end_time <= datetime.datetime.today():
    project_status = 'ended'
else:
    project_status = 'ing'

################################################## Weight Tracking ##################################################
##### 목록 제목 달기 #####
# weight tracking
# period_selectbox
weight_period = st.radio(
    'Select the period you want to weight track',
    ('day','week', 'month', 'year', 'total'), 
    index=3
)
# 가장 최근 몸무게 보여주기

# period별 쿼리 -> 쿼리 수정하기
# pha_weight_tracking 데이터가 좀 이상한 것 같음 아래 쿼리 돌리면 cur_weight이랑 goal_weight이 전부 같게 나옴 
if weight_period == 'day':
    # query = f"""SELECT update_time, pha_project.cur_weight, goal_weight
    #             from pha_project 
    #             join pha_user ON pha_user.user_id= pha_project.user_id
    #             JOIN pha_tracking ON pha_user.user_id= pha_tracking.user_id
    #             where pha_user.user_id= '{args.user_id}' and project_id = '{args.project_id}' and DATE(update_time) = DATE(NOW())
    #             order by update_time asc;
    #         """
    query = f"""
            select update_time, cur_weight, user_id
            from pha_tracking
            where user_id = {args.user_id} and DATE(update_time) = DATE(NOW())
            ORDER BY update_time asc;
            
            """
elif weight_period == 'week':
    query = f"""select update_time, cur_weight, user_id
            from pha_tracking
            where user_id = {args.user_id} and DATE(update_time) BETWEEN DATE(NOW()) - INTERVAL '7' DAY AND DATE(NOW())
                order by update_time asc;
            """
elif weight_period == 'month':
    query = f"""select update_time, cur_weight, user_id
            from pha_tracking
            where user_id = {args.user_id} and DATE(update_time) BETWEEN DATE(NOW()) - INTERVAL '30' DAY AND DATE(NOW())
                order by update_time asc;
            """
elif weight_period == 'year':
    query = f"""select update_time, cur_weight, user_id
            from pha_tracking
            where user_id = {args.user_id} and DATE(update_time) BETWEEN DATE(NOW()) - INTERVAL '365' DAY AND DATE(NOW())
                order by update_time asc;
            """
else: # weight_period == 'total'
    query = f"""select update_time, cur_weight, user_id
            from pha_tracking
            where user_id = {args.user_id}
                order by update_time asc;
            """

# # 데이터베이스에서 데이터 추출
cur = conn.cursor()
cur.execute(query)
data = cur.fetchall()

weight_tracking = pd.DataFrame(data, columns=['update_time', 'cur_weight','goal_weight'])

n = len(weight_tracking['cur_weight'])

    
# # 데이터 시각화
fig = go.Figure(data=go.Scatter(x=weight_tracking['update_time'], y=weight_tracking['cur_weight'], mode='lines'))
fig.update_layout(title='Weight Tracking per ' + weight_period.capitalize())
st.plotly_chart(fig)

################################################## Calorie Tracking ##################################################
##### 목록 제목 달기 #####
# calorie tracking

# (1) 오늘 섭취한 누적 칼로리 -> 도넛 그래프
# 칼로리 분석 정보 가져오기
# we need to change here to get real-time data from the request result
# example : '2022-04-19', user_id = 4, project_id = 12 

############################데이터 셋도 아예 2023년 7월것까지 다 만들어야 할 것 같음. 
query = f"""select food.meals_id, meal_time, pha_food.food_id, f_name, food.serving_size, pha_food.carbs, pha_food.protein, pha_food.fat, pha_food.calories
from 
(SELECT temp.user_id, meals_id, meal_time, food_id_id, serving_size
            FROM 
                (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                FROM pha_project
                WHERE user_id = {args.user_id} and project_id = {args.project_id}) as temp 
            JOIN pha_meal ON pha_meal.user_id = temp.user_id 
            WHERE DATE(pha_meal.meal_time) = DATE(NOW())) as food 
join pha_food on pha_food.food_id = food.food_id_id;"""

cur = conn.cursor()
cur.execute(query)
today_cal_info = cur.fetchall()

# 데이터프레임 생성
# Convert data to pandas dataframe
df = pd.DataFrame(data=today_cal_info, columns=['meal_id', 'meal_time', 'food_id', 'f_name','serving_size', 'carbs', 'protein', 'fat', 'calories'])

# 데이터 추출
# if the user does not recorde the food of the day 
if len(df) == 0: 
    carbs = 0
    protein = 0
    fat = 0 
    calories = 0
    st.markdown(
    "For this meal, you consumed **{} kcal from carbs, {} kcal from protein, and {} kcal from fat. Total calories are {} kcal.**".format(
        carbs, protein, fat, calories
    )
)
else: 
    
    ## 오늘 칼로리 계산 
    new_today_intake = df[['calories', 'fat','protein','carbs','meal_time', 'serving_size']].copy()

    new_today_intake['result_calories'] = new_today_intake['calories'] * (new_today_intake['serving_size'] / 100)
    new_today_intake['result_fat'] = new_today_intake['fat'] * (new_today_intake['serving_size']/100)
    new_today_intake['result_protein'] = new_today_intake['protein'] * (new_today_intake['serving_size']/100)
    new_today_intake['result_carbs'] = new_today_intake['carbs'] * (new_today_intake['serving_size']/100)

    column_sums = new_today_intake[['result_calories', 
                                    'result_fat','result_protein', 'result_carbs']].sum()

    # 하루 권장 칼로리 섭취량 계산
    # reference https://www.fao.org/3/y5686e/y5686e07.htm#bm07.1

    query = f"""  select age, goal_weight, height, pha_healthinfo.project_id_id, activity_level, pha_healthinfo.update_time , goal_type
    from 
    (select pha_user.age, pha_project.user_id, pha_user.user_name, height, goal_weight, goal_type, pha_project.project_id
    from pha_user
    join pha_project on pha_user.user_id = pha_project.user_id) as temp 
    join pha_healthinfo on temp.user_id = pha_healthinfo.user_id_id
    where pha_healthinfo.project_id_id = {args.project_id}
    order by update_time DESC
    limit 1;"""

    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()

    age = data[0][0]
    goal_weight = data[0][1]
    height = data[0][2]
    activity_level = data[0][4]
    goal_type = data[0][6]


    recommend = calculate_recommended_calories(age, goal_weight, height, activity_level, goal_type)
    rec_tot_calories = recommend[0]
    rec_carbs = recommend[1]
    rec_proteins = recommend[2]
    rec_fats = recommend[3]
    st.markdown(
        "**Recommended total calories: {} kcal, carbs : {} , proteins: {}, fats : {}**".format(
            rec_tot_calories, rec_carbs, rec_proteins, rec_fats
        ))

    
    carbs = column_sums['result_carbs']
    protein = column_sums['result_protein']
    fat = column_sums['result_fat']
    calories = column_sums['result_calories']
    # 데이터 summary 
    data = {
        'nutrient': ['total_calorie', 'carbs', 'protein', 'fat'],
        'required': [rec_tot_calories, rec_carbs, rec_proteins, rec_fats],
        'consumed': [calories, carbs, protein, fat]
    }

    # plotly 그래프 객체 생성
    trace1 = go.Scatter(x=data['nutrient'], y=data['required'], fill='tozeroy', name='Required',
                        line=dict(color='orange'))
    trace2 = go.Scatter(x=data['nutrient'], y=data['consumed'], fill='tozeroy', name='Consumed',
                        line=dict(color='lightskyblue'))
    data = [trace1, trace2]
    layout = go.Layout(title='Nutrient Intake', xaxis_title='Nutrient', yaxis_title='Amount')

    # plotly 그래프 출력
    fig = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig)


    # text 설명
    st.markdown(
        "For this meal, you consumed **{} kcal from carbs, {} kcal from protein, and {} kcal from fat. Total calories are {} kcal.**".format(
            carbs, protein, fat, calories
        )
    )



# (2) project 기간동안 섭취한 누적 칼로리 -> 라인 그래프
calorie_period = st.radio(
    'Select the period you want to calorie track',
    ('day','week', 'month', 'year', 'total'), 
    index=3
)

# period별 쿼리
if project_status == 'ended':
    if calorie_period == 'day':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id 
                    WHERE DATE(pha_meal.meal_time) = DATE(end_time)) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""
        
    elif calorie_period == 'week':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (DATE(temp.end_time) - INTERVAL '7 days') THEN DATE(temp.start_time)
                            ELSE (DATE(temp.end_time) - INTERVAL '7 days')
                        END
                        AND DATE(temp.end_time)) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""

    elif calorie_period == 'month':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (DATE(temp.end_time) - INTERVAL '1 month') THEN DATE(temp.start_time)
                            ELSE (DATE(temp.end_time) - INTERVAL '1 month')
                        END
                        AND DATE(temp.end_time)) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""

    elif calorie_period == 'year':
        # if the start time is before the one year ago, you may get the results starting from start_time 
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (DATE(temp.end_time) - INTERVAL '1 year') THEN DATE(temp.start_time)
                            ELSE (DATE(temp.end_time) - INTERVAL '1 year')
                        END
                        AND DATE(temp.end_time)) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""
            
    else: # calorie_period == 'total'
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
					WHERE DATE(pha_meal.meal_time) BETWEEN DATE(temp.start_time) AND DATE(temp.end_time)) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;
                    """

else: # project_status == 'ing'
    if calorie_period == 'day':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE DATE(pha_meal.meal_time) = DATE(NOW())) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""

    elif calorie_period == 'week':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE 
                        DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (CURRENT_DATE - INTERVAL '7 days') THEN DATE(temp.start_time)
                            ELSE (CURRENT_DATE - INTERVAL '7 days')
                        END
                        AND DATE(NOW())) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""

    elif calorie_period == 'month':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE 
                        DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (CURRENT_DATE - INTERVAL '1 month') THEN DATE(temp.start_time)
                            ELSE (CURRENT_DATE - INTERVAL '1 month')
                        END
                        AND DATE(NOW())) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""
            
    elif calorie_period == 'year':
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
                    WHERE 
                        DATE(pha_meal.meal_time) BETWEEN 
                        CASE
                            WHEN DATE(temp.start_time) > (CURRENT_DATE - INTERVAL '1 year') THEN DATE(temp.start_time)
                            ELSE (CURRENT_DATE - INTERVAL '1 year')
                        END
                        AND DATE(NOW())) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""
            
    else: # calorie_period == 'total'
        query = f"""SELECT food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                    FROM 
                    (SELECT temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                    FROM 
                        (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                        FROM pha_project
                        WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                    JOIN pha_meal ON pha_meal.user_id = temp.user_id
					WHERE DATE(pha_meal.meal_time) BETWEEN DATE(temp.start_time) AND CURRENT_DATE) AS food_table 
                    JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                    order by meal_time asc;"""
                    
        
# 데이터베이스에서 데이터 추출
cur = conn.cursor()
cur.execute(query)
data = cur.fetchall()
df_calories_intake = pd.DataFrame(data, columns=['meal_id', 'food_id', 'calories', 'protein', 'fat', 'carbs', 'serving_size', 'meal_time', 'end_time', 'start_time'])


# considering serving size that user 

#new_calories_intake = pd.DataFrame(data[['calories', 'fat','protein','carbs','meal_time']], columns = ['caloreis', 'fat','protein','carbs','meal_time'])
new_calories_intake = df_calories_intake[['calories', 'fat','protein','carbs','meal_time', 'serving_size']].copy()

new_calories_intake['result_calories'] = new_calories_intake['calories'] * (new_calories_intake['serving_size'] / 100)
new_calories_intake['restult_fat'] = new_calories_intake['fat'] * (new_calories_intake['serving_size']/100)
new_calories_intake['result_protein'] = new_calories_intake['protein'] * (new_calories_intake['serving_size']/100)
new_calories_intake['result_carbs'] = new_calories_intake['carbs'] * (new_calories_intake['serving_size']/100)

# line graph 그리기

fig = px.line(new_calories_intake, x='meal_time', y='result_calories', title=':chart_with_upwards_trend: Calories per Day')
st.plotly_chart(fig)


################################################## Meal Recommendation ##################################################
##### 목록 제목 달기 #####0
# meal recommendation


# 실행 버튼
if st.button('Get food recommendations'):
    
    #you may have an empty list as a result if the food_list do not meet the constraints of 4 in readme.md
    #python f_recommd_2.py --user_id 4 --project_id 12
    

    # FoodRecommendation.run() 실행
    My_class = FoodRecommendation(args.user_id, args.project_id, args.n_recommd_meal)
    result = My_class.run()

    # 결과 출력

    statements = f"""You have total '{len(result)}' recommendations for today. The food names are """
    for  idx, i in enumerate(result):
        statements += str(i[0])
        if idx == len(result)-1:
            break
        else:
            statements += " and "
    st.write(statements)
