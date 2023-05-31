# streamlit hello
import streamlit as st
from streamlit_option_menu import option_menu

# data visualization
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import my_db_setting

# date
import datetime
import time 

# food recommendation
from f_recommd_2 import FoodRecommendation
import argparse

# recommended calories calculate 
from recomd_calories import calculate_recommended_calories

# display an image for the recommendation food 
from googlesearch import search
import requests
from PIL import Image
import io 

# 실행 코드 예시 streamlit run final_streamlit.py -- --user_id 4 --project_id 12


####################################################argument ##################################################

parser = argparse.ArgumentParser(description = "Generate food recommendations for a user.")
parser.add_argument('--user_id', type = int, required=True, help = 'User id')
parser.add_argument('--project_id', type = int, required = True, help = 'project id of the current user_id')
parser.add_argument('--n_recommd_meal', type = int, default = 1, required=False, help = 'The number of meals that user wants to get recommended')

args = parser.parse_args()

################################################## PostgreSQL ##################################################

# PostgreSQL 연결
conn = my_db_setting.my_db_setting()

class my_Streamlit:
    def __init__(self, user_id, project_id):
        self.user_id = user_id 
        self.project_id = project_id 
    def Project_info(self):
        ##################################################Project Info ##################################################

        # 오늘 날짜 받아오기
        today = datetime.datetime.now()

        query = f"""select user_name, p_name, start_time, end_time, goal_weight, cur_weight, goal_bmi, goal_type
                    from
                    (SELECT user_id,p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_bmi, goal_type
                    FROM pha_project
                    WHERE user_id = {args.user_id} and project_id ={args.project_id}) as temp
                    join pha_user on temp.user_id =pha_user.user_id;"""
                            
        cur = conn.cursor()
        cur.execute(query)
        project_info = cur.fetchall()

        # Convert data to pandas dataframe
        df_project_info = pd.DataFrame(data= project_info, columns=['user_name', 'p_name', 'start_time', 'end_time', 'goal_weight', 'cur_weight', 'goal_bmi', 'goal_type'])

        start_time = df_project_info['start_time'].values[0]
        end_time = df_project_info['end_time'].values[0]

        # start_time = project_info[0][2]
        # end_time = project_info[0][3]


        start_time =time.mktime(time.strptime(start_time[:-3], '%Y-%m-%d %H:%M:%S'))
        end_time =time.mktime(time.strptime(end_time[:-3], '%Y-%m-%d %H:%M:%S'))

        # 종료된 project인지 진행 중인 project인지 판단 
        start_time = datetime.datetime.fromtimestamp(start_time)
        end_time = datetime.datetime.fromtimestamp(end_time)

        if end_time <= datetime.datetime.today():
            self.project_status = 'ended'
        else:
            self.project_status = 'ing'
        
    def Weight_tracking(self):

        ################################################## Weight Tracking ##################################################
        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
        # period_selectbox
            weight_period = st.radio(
                '**Select the period**',
                ('Day','Week', 'Month', 'Year', 'Total'), 
                index=1
            )
        
        with col2:
            # period별 쿼리
            if self.project_status == 'ing':
                if weight_period == 'day':
                    query = f"""
                            select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id} and DATE(update_time) <= DATE(NOW())
                            ORDER BY update_time desc
                            limit 1;
                            
                            """
                elif weight_period == 'week':
                    query = f"""SELECT update_time, cur_weight, user_id
                                FROM pha_tracking
                                WHERE user_id = {args.user_id}
                                AND DATE(update_time) BETWEEN 
                                    CASE 
                                    WHEN DATE(NOW()) - INTERVAL '7' DAY <= (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id}) THEN (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id})
                                    ELSE DATE(NOW()) - INTERVAL '7' DAY
                                    END
                                AND DATE(NOW())
                                ORDER BY update_time ASC;
                            """
                elif weight_period == 'month':
                    query = f"""SELECT update_time, cur_weight, user_id
                                FROM pha_tracking
                                WHERE user_id = {args.user_id}
                                AND DATE(update_time) BETWEEN 
                                    CASE 
                                    WHEN DATE(NOW()) - INTERVAL '1' month <= (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id}) THEN (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id})
                                    ELSE DATE(NOW()) - INTERVAL '1' month
                                    END
                                AND DATE(NOW())
                                ORDER BY update_time ASC;
                            """
                elif weight_period == 'year':
                    query = f"""SELECT update_time, cur_weight, user_id
                                FROM pha_tracking
                                WHERE user_id = {args.user_id}
                                AND DATE(update_time) BETWEEN 
                                    CASE 
                                    WHEN DATE(NOW()) - INTERVAL '1' year <= (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id}) THEN (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id})
                                    ELSE DATE(NOW()) - INTERVAL '1' year
                                    END
                                AND DATE(NOW())
                                ORDER BY update_time ASC;
                            """
                else: # weight_period == 'total'
                    query = f"""select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id} and DATE(update_time) between (SELECT start_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id})
                            and (SELECT end_time FROM pha_project WHERE user_id = {args.user_id} AND project_id = {args.project_id})
                            order by update_time asc;
                            """
            else: # self.project_status = 'ended'
                if weight_period == 'Day':
                    # query = f"""SELECT update_time, pha_project.cur_weight, goal_weight
                    #             from pha_project 
                    #             join pha_user ON pha_user.user_id= pha_project.user_id
                    #             JOIN pha_tracking ON pha_user.user_id= pha_tracking.user_id
                    #             where pha_user.user_id= '{args.user_id}' and project_id = '{args.project_id}' and DATE(update_time) = end_time)
                    #             order by update_time asc;
                    #         """
                    query = f"""
                            select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id} and DATE(update_time) <= DATE((SELECT end_time::text
                            FROM pha_project
                            WHERE user_id = {args.user_id} and project_id = {args.project_id}))
                            ORDER BY update_time desc
                            limit 1;
                        """


                elif weight_period == 'Week':
                    query = f"""select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id}  and DATE(update_time) BETWEEN 
                                                    CASE 
                                                    WHEN DATE((SELECT end_time
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}) - INTERVAL '7' day) < DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id})) THEN DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}))
                                                    ELSE 
                                                    DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id ={args.project_id})) - INTERVAL '7' day 
                                                    END 
                                                    AND DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id ={args.user_id} and project_id = {args.project_id}))
                                    
                                order by update_time asc;
                            """
                elif weight_period == 'Month':
                    query = f"""select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id}  and DATE(update_time) BETWEEN 
                                                    CASE 
                                                    WHEN DATE((SELECT end_time
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}) - INTERVAL '1' month) < DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id})) THEN DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}))
                                                    ELSE 
                                                    DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id ={args.project_id})) - INTERVAL '1' month 
                                                    END 
                                                    AND DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id ={args.user_id} and project_id = {args.project_id}))
                                    
                                order by update_time asc;
                            """
                elif weight_period == 'Year':
                    query = f"""select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id}  and DATE(update_time) BETWEEN 
                                                    CASE 
                                                    WHEN DATE((SELECT end_time
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}) - INTERVAL '1' year) < DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id})) THEN DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}))
                                                    ELSE 
                                                    DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id ={args.project_id})) - INTERVAL '1' year 
                                                    END 
                                                    AND DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id ={args.user_id} and project_id = {args.project_id}))
                                    
                                order by update_time asc;
                            """
                else: # weight_period == 'total'
                    query = f"""select update_time, cur_weight, user_id
                            from pha_tracking
                            where user_id = {args.user_id} and DATE(update_time) BETWEEN DATE((SELECT start_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id})) AND DATE((SELECT end_time::text
                                                    FROM pha_project
                                                    WHERE user_id = {args.user_id} and project_id = {args.project_id}))
                            order by update_time asc;
                            """

            # # 데이터베이스에서 데이터 추출
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()

            weight_tracking = pd.DataFrame(data, columns=['update_time', 'cur_weight', 'user_id'])

            n = len(weight_tracking['cur_weight'])

                
            # # 데이터 시각화    
            if weight_period == "Day":
                fig = px.bar(weight_tracking, x= 'update_time', y= 'cur_weight')
                fig.update_layout(title='📈 Weight Tracking per ' + weight_period.capitalize())
                fig.update_xaxes(title_text='Update Time')
                fig.update_yaxes(title_text='Your Weight')
                st.plotly_chart(fig)
            else:
                fig = px.line(weight_tracking, x= 'update_time', y= 'cur_weight')
                fig.update_layout(title='📈 Weight Tracking per ' + weight_period.capitalize())
                fig.update_xaxes(title_text='Update Time')
                fig.update_yaxes(title_text='Your Weight')

                st.plotly_chart(fig)

        st.divider()
        # last_weight = round(weight_tracking['cur_weight'].iloc[-1], 2)
        # #goal_weight = round(weight_tracking['goal_weight'].iloc[0], 2)
        # goal_w_query = f"""
        #                 select goal_weight
        #                 from pha_project 
        #                 where user_id = {args.user_id} and project_id = {args.project_id}
        #                 """
        # cur.execute(goal_w_query)
        # goal_weight= cur.fetchall()[0][0]
        # # 수정
        # change_weight = round(last_weight - goal_weight, 2)
        # weight_value = f"{last_weight} kg"
        # st.metric(label="Current weight compared to goal weight", value= weight_value , delta= change_weight)
    
        

        ################################################## Calorie Tracking ##################################################
    def Cal_tracking(self):
        st.divider()

        col1, col2, col3, col4, col5 = st.columns(5)
        # (1) project 기간동안 섭취한 누적 칼로리
        with col1:
            calorie_period = st.radio(
                '**Select the period**',
                ('Day','Week', 'Month', 'Year', 'Total'), 
                index=1
            )

            # period별 쿼리
            if self.project_status == 'ended':
                if calorie_period == 'Day':
                    # not apply DATE() function to the meal_time for only 'Day' calorie_period 
                    query = f"""SELECT meal_type, food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                                FROM 
                                    (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                                    FROM pha_project
                                    WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                                JOIN pha_meal ON pha_meal.user_id = temp.user_id 
                                WHERE DATE(pha_meal.meal_time) = DATE(end_time)) AS food_table 
                                JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                                order by food_table.meal_time asc ;"""
                                    
                elif calorie_period == 'Week':
                    query = f"""SELECT meal_type, food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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

                elif calorie_period == 'Month':
                    query = f"""SELECT meal_type, food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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

                elif calorie_period == 'Year':
                    # if the start time is before the one year ago, you may get the results starting from start_time 
                    query = f"""SELECT meal_type,  food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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
                    query = f"""SELECT meal_type, food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                                FROM 
                                    (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                                    FROM pha_project
                                    WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                                JOIN pha_meal ON pha_meal.user_id = temp.user_id
                                WHERE DATE(pha_meal.meal_time) BETWEEN DATE(temp.start_time) AND DATE(temp.end_time)) AS food_table 
                                JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                                order by meal_time asc;
                                """

            else: # self.project_status == 'ing'
                # not apply DATE() function to the meal_time for only 'Day' calorie_period 
                if calorie_period == 'Day':
                    query = f"""SELECT meal_type, food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, food_table.update_time as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type, temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
                                FROM 
                                    (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                                    FROM pha_project
                                    WHERE user_id = {args.user_id} AND project_id ={args.project_id}) AS temp 
                                JOIN pha_meal ON pha_meal.user_id = temp.user_id
                                WHERE DATE(pha_meal.meal_time) = DATE(NOW())) AS food_table 
                                JOIN pha_food ON pha_food.food_id = food_table.food_id_id
                                order by meal_time asc;"""

                elif calorie_period == 'Week':
                    query = f"""SELECT meal_type,food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type,temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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

                elif calorie_period == 'Month':
                    query = f"""SELECT meal_type,food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type,temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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
                        
                elif calorie_period == 'Year':
                    query = f"""SELECT meal_type,food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type,temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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
                    query = f"""SELECT meal_type,food_table.meals_id, food_table.food_id_id, calories, protein, fat, carbs,ref_serving_size, DATE(food_table.update_time) as meal_time, food_table.end_time, food_table.start_time
                                FROM 
                                (SELECT meal_type,temp.user_id, meals_id, meal_time, food_id_id, pha_meal.meal_time AS update_time, end_time, start_time
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
            df_calories_intake = pd.DataFrame(data, columns=['meal_type','meal_id', 'food_id', 'calories', 'protein', 'fat', 'carbs', 'serving_size', 'meal_time', 'end_time', 'start_time'])


            # considering serving size that user 
            new_calories_intake = df_calories_intake[['calories', 'fat','protein','carbs','meal_time', 'serving_size', 'meal_type']].copy()

            new_calories_intake['result_calories'] = new_calories_intake['calories'] * (new_calories_intake['serving_size'] / 100)
            new_calories_intake['restult_fat'] = new_calories_intake['fat'] * (new_calories_intake['serving_size']/100)
            new_calories_intake['result_protein'] = new_calories_intake['protein'] * (new_calories_intake['serving_size']/100)
            new_calories_intake['result_carbs'] = new_calories_intake['carbs'] * (new_calories_intake['serving_size']/100)

        # bar graph 그리기
        with col2:
            fig = px.bar(new_calories_intake, x='meal_time', y='result_calories', color='meal_type')
            fig.update_layout(title='📊 Calorie Tracking per ' + calorie_period.capitalize())
            fig.update_xaxes(title_text='Meal Time')
            fig.update_yaxes(title_text='Calories Consumed')
            st.plotly_chart(fig)
        st.divider()

        # (2) 오늘 섭취한 누적 칼로리
        # 칼로리 분석 정보 가져오기

        query = f"""SELECT food.meals_id, meal_time, pha_food.food_id, f_name, food.serving_size, pha_food.carbs, pha_food.protein, pha_food.fat, pha_food.calories
                    FROM
                        (SELECT temp.user_id, meals_id, meal_time, food_id_id, serving_size
                        FROM 
                            (SELECT user_id, p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_type
                            FROM pha_project
                            WHERE user_id = {args.user_id} and project_id = {args.project_id}) as temp 
                            JOIN pha_meal ON pha_meal.user_id = temp.user_id 
                            WHERE DATE(pha_meal.meal_time) = DATE(NOW())) as food 
                    JOIN pha_food on pha_food.food_id = food.food_id_id;"""

        cur = conn.cursor()
        cur.execute(query)
        today_cal_info = cur.fetchall()

        # Convert data to pandas dataframe
        df = pd.DataFrame(data=today_cal_info, columns=['meal_id', 'meal_time', 'food_id', 'f_name','serving_size', 'carbs', 'protein', 'fat', 'calories'])

        # 데이터 추출
        # if the user does not recorde the food of the day 
        if len(df) == 0: 
            carbs = 0
            protein = 0
            fat = 0 
            calories = 0
            # 확인 
            st.markdown("**No calories consumed today.**")
        else: 
            # 오늘 칼로리 계산 
            new_today_intake = df[['calories', 'fat','protein','carbs','meal_time', 'serving_size']].copy()

            new_today_intake['result_calories'] = new_today_intake['calories'] * (new_today_intake['serving_size'] / 100)
            new_today_intake['result_fat'] = new_today_intake['fat'] * (new_today_intake['serving_size']/100)
            new_today_intake['result_protein'] = new_today_intake['protein'] * (new_today_intake['serving_size']/100)
            new_today_intake['result_carbs'] = new_today_intake['carbs'] * (new_today_intake['serving_size']/100)

            column_sums = new_today_intake[['result_calories', 
                                            'result_fat','result_protein', 'result_carbs']].sum()

            # 하루 권장 칼로리 섭취량 계산
            # reference https://www.fao.org/3/y5686e/y5686e07.htm#bm07.1

            query = f"""SELECT age, goal_weight, height, pha_healthinfo.project_id_id, activity_level, pha_healthinfo.update_time , goal_type
                        FROM
                            (SELECT pha_user.age, pha_project.user_id, pha_user.user_name, height, goal_weight, goal_type, pha_project.project_id
                            FROM pha_user
                            JOIN pha_project on pha_user.user_id = pha_project.user_id) as temp 
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
            rec_tot_calories = round(recommend[0], 2)
            rec_carbs = round(recommend[1], 2)
            rec_proteins = round(recommend[2], 2)
            rec_fats = round(recommend[3], 2)
            
            # st.markdown(
            #     "**Recommended total calories: {} kcal, carbs : {} , proteins: {}, fats : {}**".format(
            #         round_rec_tot_calories, round_rec_carbs, round_rec_proteins, round_rec_fats
            #     ))

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
            layout = go.Layout(title='🥗 Nutrient Intake', xaxis_title='Nutrient', yaxis_title='Amount')

            # plotly 그래프 출력
            fig = go.Figure(data=data, layout=layout)
            st.plotly_chart(fig)

            round_carbs = round(carbs, 2)
            round_protein = round(protein, 2)
            round_fat = round(fat, 2)
            round_calories = round(calories, 2)

            # 컬럼 생성
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Recommended Intake")
                st.success("Total calories: {} kcal".format(rec_tot_calories))
                st.info("Carbs : {}".format(rec_carbs))
                st.info("Proteins: {}".format(rec_proteins))
                st.info("Fats : {}".format(rec_fats))

            with col2:
                st.subheader("Meal Consumption")
                st.success("Total calories: {} kcal".format(round_calories))
                st.info("Calories from carbs: {} kcal".format(round_carbs))
                st.info("Calories from proteins: {} kcal".format(round_protein))
                st.info("Calories from fats: {} kcal".format(round_fat))

        st.divider()

        # last_intake = new_calories_intake['result_calories'].iloc[-1]
        # round_intake = round(last_intake, 2)
        # # 수정
        # delta_intake = round(round_intake - rec_tot_calories, 2)
        # calorie_val = f"{round_intake} kcal"
        # st.metric(label="Calories consumed today compared to recommended intake", value= calorie_val, delta= delta_intake)
    
    def get_image_url(self, query): 
        url = None 
        for result in search(query, num_results=1):
            url = result 
            break
        return url 
    
    def Meal_recommendation(self):
        ################################################## Meal Recommendation ##################################################
        st.divider()
    
        #col1, col2 = st.columns([1, 2])
        #with col1:
            # 실행 버튼
            #if st.button('Get food recommendations'):
                # you may have an empty list as a result if the food_list do not meet the constraints of 4 in readme.md
                # python f_recommd_2.py --user_id 4 --project_id 12

        # FoodRecommendation.run() 실행
        My_class = FoodRecommendation(args.user_id, args.project_id, args.n_recommd_meal)
        result = My_class.run()
        
        #with col2:
        # 결과 출력
        statements = f"""**You have a total of '{len(result)}' food recommendations for today.**"""
        st.info(statements)

        # 결과를 데이터프레임으로 변환
        data = {"Recommended Food": [i[0] for i in result]}
        df = pd.DataFrame(data)
        df.index = df.index + 1

        #create coupang link 
        list_coupang_link = []
        for i in result:
            food_name = i[0]
            # Replace space with a hyphen
            food_name_url = food_name.replace(" ", "-")
            url = f"""https://www.coupang.com/np/search?component=&q={food_name}&channel=user"""
            st.markdown(f"[{food_name}]({url}/{food_name_url})")
            list_coupang_link.append(url)

        #df['coupang_link'] = list_coupang_link

        #Create a hyperlink column
        #df['Linked Food Name'] = df['Recommended Food'].apply(lambda row: row["coupang_link"])

        # Display DataFrame with hyperlinked column
        #st.write(df[['Recommended Food','Linked Food Name']], unsafe_allow_html=True)
        #st.dataframe(df.style.format({'Linked Food Name': st.markdown}), unsafe_allow_html=True)
        #link 
        # for food_name in result:
        #     image_url = self.get_image_url(f"{food_name[0]} image")

        #     if image_url:
        #         try:
        #             response = requests.get(image_url)
        #             if response.status_code == 200:
        #                 image_data = response.content
        #                 pil_image = Image.open(io.BytesIO(image_data))
        #                 st.image(pil_image, caption=food_name[0], use_column_width=True)
        #             else:
        #                 st.write("Failed to retrieve the image.")
        #         except requests.exceptions.RequestException as e:
        #             st.write(f"Error occurred: {e}")
        #     else:
        #         st.write("No image found for the given food name.")
        # url = f"""https://www.coupang.com/np/search?component=&q=양상추&channel=user"""
        # st.markdown(f"[{result[0][0]}]({url})")

        # 데이터프레임 출력
        #st.table(df)
    
    
        ################################################## Summary ##################################################
    def Summary(self):
        
        st.divider()

        query = f"""select user_name, p_name, start_time, end_time, goal_weight, cur_weight, goal_bmi, goal_type
                    from
                    (SELECT user_id,p_name, start_time::text, end_time::text, goal_weight, cur_weight, goal_bmi, goal_type
                    FROM pha_project
                    WHERE user_id = {args.user_id} and project_id ={args.project_id}) as temp
                    join pha_user on temp.user_id =pha_user.user_id;"""
            
        cur = conn.cursor()
        cur.execute(query)
        project_info = cur.fetchall()
        
        summary_user = project_info[0][0]
        summary_project_name = project_info[0][1]
        summary_start_time = project_info[0][2]
        summary_end_time = project_info[0][3]
        summary_goal_weight = round(project_info[0][4], 2)
        summary_goal_bmi = project_info[0][6]
        summary_goal_type = project_info[0][7]

        # st.write('User : ', summary_user)
        # st.write('Project Name : ', summary_project_name)
        # st.write('Goal Weight : ', summary_goal_weight)
        # st.write('Goal BMI : ', summary_goal_bmi)
        # st.write('Start Time : ', summary_start_time)
        # st.write('End Time : ', summary_end_time)

        # st.markdown("### User Summary")

        # Create 2 columns
        col1, col2 = st.columns(2)

        # Using the columns
        with col1:
            st.subheader("Project Details")
            st.markdown("**User:** {}".format(summary_user))
            st.markdown("**Project Name:** {}".format(summary_project_name))
            st.markdown("**Goal Weight:** {}".format(summary_goal_weight))
            st.markdown("**Goal BMI:** {}".format(summary_goal_bmi))
            st.markdown("**Goal Type:** {}".format(summary_goal_type))

        with col2:
            st.subheader("Project Timeline")
            st.markdown("**Start Time:** {}".format(summary_start_time))
            st.markdown("**End Time:** {}".format(summary_end_time))


        #Show is_achieved
        cur = conn.cursor()

        today_query = """ 
                    select NOW();
                    """

        cur.execute(today_query)
        today = cur.fetchall()[0][0]

        query= f"""
                select user_id, temp.max_update_time, temp.project_id
        from
        (select project_id, max(update_time) as max_update_time
        from pha_project
        join pha_tracking on pha_tracking.user_id = pha_project.user_id 
        where project_id = {args.project_id} and 
        update_time <= pha_project.end_time
        group by project_id 
        order by project_id) as temp
        join pha_project on pha_project.project_id = temp.project_id
        ;
        """
        cur.execute(query)
        full_data = cur.fetchall()
        max_update_time = full_data[0][1]

        ############is_achieved update 
        ################## 실제 update_weight 기준으로 DB연결해서 해서 is_achieved 상태 update 필요 


        project_query = f"""
                        select end_time, goal_type, goal_weight
                        from pha_project
                        where user_id = {args.user_id} and project_id = {args.project_id};
                        """
        cur.execute(project_query)
        project_info = cur.fetchall()
        end_time = project_info[0][0]
        goal_type = project_info[0][1]
        goal_weight = project_info[0][2]

        weight_query = f"""
                        select cur_weight 
                        from pha_tracking 
                        where user_id = {args.user_id} and update_time = '{max_update_time}';
                        """
        cur.execute(weight_query)
        AT_WEIGHT = cur.fetchall()[0][0]

        # 프로젝트가 끝남 , 감소 목표
        if today >= end_time and goal_type == 'Diet':
            if goal_weight >= AT_WEIGHT:
                update_query = f"""
                    UPDATE pha_project SET is_achieved = True 
                    WHERE pha_project.project_id = {args.project_id} 
                    """
                
            else:
                update_query = f"""
                    UPDATE pha_project SET is_achieved = False 
                    WHERE pha_project.project_id = {args.project_id}
                    """
                    
        # 프로젝트가 끝남, 증량 목표  
        elif today >= end_time and goal_type == 'putting  on  weight':
            if goal_weight <= AT_WEIGHT:
                update_query = f"""
                    UPDATE pha_project SET is_achieved = True
                    WHERE pha_project.project_id = {args.project_id}
                    """
                
            else:
                update_query = f"""
                    UPDATE pha_project SET is_achieved = False 
                    WHERE pha_project.project_id = {args.project_id}
                    """
                
        #프로젝트 'ing'
        else:
            update_query = f"""
                    UPDATE pha_project SET is_achieved = False 
                    WHERE pha_project.project_id = {args.project_id}
                    """

        cur.execute(update_query)
        conn.commit()

        is_achieved_query = f"""
                    select is_achieved 
                    from pha_project
                    where project_id = {args.project_id}
                    """
        cur.execute(is_achieved_query)
        status_cur_is_achieved = cur.fetchall()[0][0]

        # st.write('Project Status : ', status_cur_is_achieved)
        # st.write('<span style="font-size: 20px;"><b>Project Status :</b> {}</span>'.format(status_cur_is_achieved), unsafe_allow_html=True)
        if status_cur_is_achieved == 0:
            status_cur_is_achieved = 'FAIL'
            # st.write('<span style="font-size: 20px; color: red;"><b>Project Status :</b> {}</span>'.format(status_cur_is_achieved), unsafe_allow_html=True)
            status_text = '<span style="font-size: 16px;"><b>Project Status :</b></span> <span style="font-size: 16px; color: red;">{}</span>'.format(status_cur_is_achieved)
            st.write(status_text, unsafe_allow_html=True)

        else:
            status_cur_is_achieved = 'SUCCESS'
            status_text = '<span style="font-size: 16px;"><b>Project Status :</b></span> <span style="font-size: 16px; color: green;">{}</span>'.format(status_cur_is_achieved)
            st.write(status_text, unsafe_allow_html=True)

    def Cur_status(self):
        ################## Current status #################################### 
        st.divider()

        st.subheader("""
                Current weight and today's calories consumption
                """)
        
        col1, col2 = st.columns(2)
    
        with col1:
            if self.project_status == "ing" :
                cur_w_query = f""" 
                        select cur_weight
                        from pha_tracking 
                        where user_id = {args.user_id} AND DATE(update_time) <= DATE(NOW())
                        ORDER BY update_time desc
                        limit 1;
                        """
            else: 
                cur_w_query = f""" 
                        select cur_weight
                        from pha_tracking 
                        where user_id = {args.user_id} AND DATE(update_time) <= DATE((select end_time from pha_project where project_id = {args.project_id}))
                        ORDER BY update_time desc
                        limit 1;
                        """

            # # 데이터베이스에서 데이터 추출
            cur = conn.cursor()
            cur.execute(cur_w_query)
            cur_weight = cur.fetchall()[0][0]

            goal_w_query = f"""
                            select goal_weight 
                            from pha_project
                            where project_id = {args.project_id}
                            """
            
            cur.execute(goal_w_query)
            goal_weight = cur.fetchall()[0][0]
            
            cur_weight = round(cur_weight, 2)
            goal_weight = round(goal_weight, 2)
            
            
            value1 = f"{cur_weight} kg"
            #st.metric(label="Weight", value= cur_weight, delta= change_weight)
            # st.metric(label="Current Weight", value= cur_weight)

            st.metric(label="**Current Weight**", value= value1)
            # st.write(f"""
            #         Current weight and today's calories consumption
            #         """)
            st.info(f"Goal weight {goal_weight}" )


            ############cheer up! 
            start_weight_q = f"""
                            select cur_weight 
                            from pha_project 
                            where project_id = {args.project_id}
                            """
            cur.execute(start_weight_q)
            start_weight = cur.fetchall()[0][0]

            left_weight = cur_weight - goal_weight
            left_weight = round(left_weight, 2)

            change_weight = start_weight - goal_weight
            change_weight = round(change_weight,2) 

            goal_type_q = f"""
                            select goal_type 
                            from pha_project
                            where project_id = {args.project_id};
                            """
            cur.execute(goal_type_q)
            goal_type = cur.fetchall()[0][0]
            if goal_type == "Diet":
                if cur_weight <= goal_weight:
                    st.write(f"Way to go!! You have lost {change_weight} kg and {left_weight} kg is left for a success!! ")
                else: 
                    st.write(f"Work hard!! You have gained {change_weight} kg!! ")
            else: # goal_type = "putting on weight"
                if cur_weight >= goal_weight:
                    left_weight = -left_weight
                    st.wirte(f"Way to go!! You have gained {change_weight} kg and {left_weight} kg is left for a success")
                else:
                    change_weight = -change_weight
                    st.write(f"Work hard!!You have lost {-change_weight} kg ")

            

        #Calorie
        with col2:
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
            
                
            ## 오늘 칼로리 계산 
            new_today_intake = df[['calories', 'fat','protein','carbs','meal_time', 'serving_size']].copy()

            new_today_intake['result_calories'] = new_today_intake['calories'] * (new_today_intake['serving_size'] / 100)
            new_today_intake['result_fat'] = new_today_intake['fat'] * (new_today_intake['serving_size']/100)
            new_today_intake['result_protein'] = new_today_intake['protein'] * (new_today_intake['serving_size']/100)
            new_today_intake['result_carbs'] = new_today_intake['carbs'] * (new_today_intake['serving_size']/100)

            column_sums = new_today_intake[['result_calories', 'result_fat','result_protein', 'result_carbs']].sum()

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
            rec_tot_calories = round(recommend[0], 2)
            rec_carbs = round(recommend[1], 2)
            rec_proteins = round(recommend[2], 2)
            rec_fats = round(recommend[3], 2)

            
            
            carbs = column_sums['result_carbs']
            protein = column_sums['result_protein']
            fat = column_sums['result_fat']
            calories = column_sums['result_calories']

            round_carbs = round(carbs, 2)
            round_protein = round(protein, 2)
            round_fat = round(fat, 2)
            round_calories = round(calories, 2)

            value2 = f"{round_calories} kcal"
            if len(df) == 0: 
                carbs = 0
                protein = 0
                fat = 0 
                calories = 0
                value2 = "0 kcal"
                st.metric(label = "**No calories consumed today.**", value = value2)
                st.info(f"Required calroies {rec_tot_calories}")
            else: 
                #st.metric(label= "Calories", value= round_intake, delta= weight)
                # st.metric(label= "Today's Calories Consumption", value= round_calories)
            
                st.metric(label= "Today's Calories Consumption", value= value2)
                st.info(f"Required calroies {rec_tot_calories}")
            
            if rec_tot_calories <= calories:
                exceed_cal = calories-rec_tot_calories
                st.write(f"You have consumed {exceed_cal} kg for today")
            else:
                remain_cal = rec_tot_calories - calories
                st.write(f"You have {remain_cal} kcal left for today")
                
            

my_object = my_Streamlit(args.user_id, args.project_id)

################################################## Page Title ##################################################

st.set_page_config('HealthGenie', '🧞‍♂️', layout='wide')

# emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
# st.title('HealthGenie 🧞‍♂️')
st.markdown('<h1 style="font-family: Georgia, sans-serif; font-size: 48px; font-weight: bold;">HealthGenie 🧞‍♂️</h1>', unsafe_allow_html=True)


# Subheader 적용
# st.subheader("""
# **Data-based personalized health guidance service**
# """)
st.markdown('<h2 style="font-family: Georgia, monospace; font-size: 28px; ">Data-based personalized health guidance service</h2>', unsafe_allow_html=True)

            
################################################## Sidebar ##################################################

# https://icons.getbootstrap.com/
with st.sidebar:
    choose = option_menu("Your Report", ["Summary", "Current status",  "Weight", "Calorie", "Recommendation"],
                        icons=['chat-right-text', 'clipboard-data', 'speedometer', 'droplet-half', 'hand-thumbs-up'],
                        menu_icon="person-vcard", default_index=0,
                        styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "#FA4C4B", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#BED2F3"},
    }
    )

my_object.Project_info()

if choose == "Summary":
    my_object.Summary()
elif choose == "Current status":
    my_object.Cur_status()
elif choose == "Weight":
    my_object.Weight_tracking()
elif choose == "Calorie":
    my_object.Cal_tracking()
elif choose == "Recommendation":
    my_object.Meal_recommendation()