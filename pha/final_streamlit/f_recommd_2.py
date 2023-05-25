import psycopg2
from datetime import datetime, timedelta 
import argparse
import content_based_user_rec
import pandas as pd 
import pandas as pd
from surprise import SVD, Reader
from surprise import Dataset
from surprise.model_selection import train_test_split

import my_db_setting

#reference 
#https://www.kaggle.com/code/ibtesama/getting-started-with-a-movie-recommendation-system#Collaborative-Filtering
#https://realpython.com/build-recommendation-engine-collaborative-filtering/#memory-based

class FoodRecommendation:
    def __init__(self, user_id, project_id, n_recommd_food):
        self.user_id = user_id
        self.project_id = project_id
        self.n_recommd_food = n_recommd_food
    
    # get project information from user_id and project id
    # goal_type도 뽑아야 함  
    def get_user_goal_type(self):
        conn = my_db_setting.my_db_setting()

        cur = conn.cursor()
        cur.execute("SELECT pha_user.user_name, pha_project.user_id, pha_project.p_name, start_time, end_time, goal_bmi FROM pha_user JOIN pha_project ON pha_user.us_id = pha_project.user_id WHERE pha_project.user_id = %s and pha_project.project_id = %s and pha_project.is_achieved = false;", (self.user_id, self.project_id))
        result = cur.fetchall()
        cur.close()
        if result:
            return result[0]
        else:
            return "Wrong user_id or project_id"
    
    #############we are going to get get similar "users"
    ############# and use both information to recommend food lists.
    
    # content based similar users 
    # return list ordering by similar scores 
    # checklist : goal_bmi, goal_type, activity_level
    def get_similar_users(self):
        conn = my_db_setting.my_db_setting()
        user_query = f"""
                    select *
                    from pha_user
                    where is_superuser = false 
                    order by user_id;
                    """
        cur = conn.cursor()
        cur.execute(user_query)
        user_data = cur.fetchall()

        #pha_user= pd.read_csv('pha_user.csv')
        #pha_user = pha_user[pha_user['is_superuser'] != True]
        
        pha_user = pd.DataFrame(user_data, columns =['password','last_login','is_superuser','user_id','user_name','email','is_staff','is_active','date_joined','sex','age','height','weight'])

        recommendation_dic = dict()
        n_user = len(list(pha_user['user_id']))
        for i in range(0, n_user):
            cur_user = pha_user['user_id'].iloc[i]
            # cur_user는 int 
            result = content_based_user_rec.get_recommendations(cur_user)
            recommendation_dic[cur_user] = result

        
        result = recommendation_dic[self.user_id]
        return result

    

    
    # rating table = food_id, user_id, rating, meal_time (latest update time)
    # need to get the project_id and user_id 
    def get_rating_table(self, similar_user_list, project_id, user_id):
        similar_user_tuple = tuple(similar_user_list)
        conn = my_db_setting.my_db_setting()
        cur = conn.cursor()
        
        #rating_query = f"""
        #                         select temp.food_id_id, temp.user_id, temp.rating, temp.meal_time 
        # from (
        # 	select food_id_id, user_id, rating, meal_time, meals_id 
        # 	from pha_meal 
        # 	where user_id IN {similar_user_tuple} ORDER BY food_id_id, user_id, meal_time) as temp 
        # where temp.meal_time <= (select end_time from pha_project where project_id = {project_id} and user_id = {user_id}) 
        # and temp.meal_time >= (select start_time from pha_project where project_id = {project_id} and user_id = {user_id})
        # AND temp.meal_time = (select MAX(meal_time) 
        # 					  FROM pha_meal 
        # 					  WHERE food_id_id = temp.food_id_id AND user_id = temp.user_id);
        #                         """
        #cur.execute(rating_query, (similar_user_tuple, project_id,user_id,project_id,user_id,))

        
        # rating_query = f"""
        #                 select temp.food_id_id, temp.user_id, temp.rating, temp.meal_time 
        #                 from (
        #                 select food_id_id, user_id, rating, meal_time, meals_id 
        #                 from pha_meal 
        #                 where user_id IN {similar_user_tuple} ORDER BY food_id_id, user_id, meal_time) as temp 
        #                 where temp.meal_time <= (select end_time from pha_project where project_id = {project_id} and user_id = {user_id}) 
        #                 and temp.meal_time >= (select start_time from pha_project where project_id = {project_id} and user_id = {user_id})
        #                 AND temp.meal_time = (select MAX(meal_time) 
        #                                     FROM pha_meal 
        #                                     WHERE food_id_id = temp.food_id_id AND user_id = temp.user_id);
        #                 """

        # meal이 너무 많아서 최근 일주일치 것만 가져오도록 해야겠음 (나중에 svd할때 속도 너무 느려짐)
        rating_query = f"""
                select temp.food_id_id, temp.user_id, temp.rating, temp.meal_time 
                from (
                select food_id_id, user_id, rating, meal_time, meals_id 
                from pha_meal 
                where user_id IN {similar_user_tuple} ORDER BY food_id_id, user_id, meal_time) as temp 
                where temp.meal_time BETWEEN ((select end_time from pha_project where project_id = 4 and user_id =1) - INTERVAL '7' DAY)
								AND (select end_time from pha_project where project_id = 4 and user_id =1);
                """
        cur.execute(rating_query)
        result = cur.fetchall()
        cur.close()
        return result
    
    def filtering_allergy_diet_restriction(self, result):
        
        result = [int(i) for i in result]    
        result = tuple(result)
        conn = my_db_setting.my_db_setting()
        cur = conn.cursor()
        # query = "SELECT temp.food_id, temp.allergens, temp.dietary_restriction from (SELECT * FROM pha_food WHERE food_id IN %s) as temp WHERE (SELECT pha_health_info.allergy_name FROM pha_health_info WHERE user_id = %s AND update_time = (SELECT MAX(update_time) FROM pha_health_info WHERE user_id = %s)) NOT IN (SELECT unnest(string_to_array(pha_food.allergens, ',')) from pha_food WHERE food_id IN %s) AND (SELECT pha_health_info.diet_restriction FROM pha_health_info WHERE user_id = %s AND update_time = (SELECT MAX(update_time) FROM pha_health_info WHERE user_id = %s)) NOT IN (SELECT unnest(string_to_array(pha_food.dietary_restriction, ',')) from pha_food WHERE food_id IN %s);"
        query = f"""
                SELECT temp.food_id, temp.allergen, temp.dietary_restriction 
                from  
                (SELECT * FROM pha_food WHERE food_id IN {result}) as temp 
                WHERE (SELECT pha_healthinfo.allergy_name 
                    FROM pha_healthinfo 
                    WHERE user_id_id = {self.user_id}
                    AND update_time = (SELECT MAX(update_time) 
                        FROM pha_healthinfo WHERE user_id_id = {self.user_id})) NOT IN (SELECT unnest(string_to_array(pha_food.allergen, ',')) 
                    from pha_food WHERE food_id IN {result}) AND 
                    (SELECT pha_healthinfo.dietary_restriction 
                    FROM pha_healthinfo 
                    WHERE user_id_id = {self.user_id} AND update_time = (SELECT MAX(update_time) FROM pha_healthinfo WHERE user_id_id = {self.user_id})) NOT IN (SELECT unnest(string_to_array(pha_food.dietary_restriction, ',')) 
                    from pha_food WHERE food_id IN {result});
                """
        cur.execute(query)
        #cur.execute(query, (result, self.user_id, self.user_id,result, self.user_id, self.user_id, result,))
        result = cur.fetchall()
        cur.close()
        return result 


    

    def svd_algorithm(self, food_rating):
        # Load the dataset
        # data = Dataset.load_builtin('ml-100k')
        reader = Reader(rating_scale=(1, 5))
        rating = pd.DataFrame(food_rating)
        rating.columns = ['food_id_id', 'user_id', 'rating', 'meal_time']
        data = Dataset.load_from_df(rating[['user_id', 'food_id_id', 'rating']], reader)


        # Split the dataset into training and testing sets
        trainset, testset = train_test_split(data, test_size=.25)

        # Train the model using SVD algorithm
        algo = SVD()
        algo.fit(trainset)

        # Get the list of all unique user ids
        user_ids = data.df['user_id'].unique()

        # Create a dictionary to store the top recommended items for each user
        top_recs = {}

        # For each user id, get the list of items that have not been rated by the user
        for user_id in user_ids:
            # Get the list of all items
            items = data.df['food_id_id'].unique()
            # Get the list of items that have been rated by the user
            rated_items = data.df[data.df['user_id'] == user_id]['food_id_id'].unique()
            # Get the list of items that have not been rated by the user
            unrated_items = list(set(items) - set(rated_items))
            # Get the predicted ratings for the unrated items
            predicted_ratings = [algo.predict(user_id, item_id).est for item_id in unrated_items]
            # Combine the list of unrated items with their predicted ratings
            unrated_items_with_ratings = zip(unrated_items, predicted_ratings)
            # Sort the items by their predicted ratings
            sorted_items = sorted(unrated_items_with_ratings, key=lambda x: x[1], reverse=True)
            # Get the top recommended items for the user
            top_items = [item_id for item_id, rating in sorted_items[:5]]
            # Add the top recommended items to the dictionary
            top_recs[user_id] = top_items
        return top_recs
    
    def run(self):
        # 5 similar users 
        # content based similar users (TF-IDF matrix, cosine similarity)
        # return list ordering by similar scores 
        # checklist : goal_bmi, goal_type, activity_level
        similar_user_list = self.get_similar_users()[0:5]
        similar_user_list.append(self.user_id)

        # bring ratings for each food of similar users including current user 
        food_rating = self.get_rating_table(similar_user_list, self.project_id, self.user_id)
        #print(food_rating[0])    
        result = self.svd_algorithm(food_rating) # dictionary 
        result = result[self.user_id]
        result = self.filtering_allergy_diet_restriction(result)
        result_food_list = []
        for food in result:
            result_food_list.append(food[0])

        conn = my_db_setting.my_db_setting()


        cur = conn.cursor()
        result_food_tuple = tuple(result_food_list)
        query = f""" select f_name
                    from pha_food
                    where food_id IN {result_food_tuple};"""
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        
        return result 


'''
you may have an empty list as a result if the food_list do not meet the constraints of 4 in readme.md
python f_recommd_2.py --user_id 4 --project_id 12
'''

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description = "Generate food recommendations for a user.")
#     parser.add_argument('--user_id', type = int, required=True, help = 'User id')
#     parser.add_argument('--project_id', type = int, required = True, help = 'project id of the current user_id')
#     parser.add_argument('--n_recommd_meal', type = int, default = 1, required=False, help = 'The number of meals that user wants to get recommended')

#     args = parser.parse_args()

#     My_class = FoodRecommendation(args.user_id, args.project_id, args.n_recommd_meal)

#     result = My_class.run()
    
#     result_food_list = []
#     for food in result:
#         result_food_list.append(food[0])

#     conn = my_db_setting.my_db_setting()



#     cur = conn.cursor()
#     result_food_tuple = tuple(result_food_list)
#     query = f""" select f_name
#                 from pha_food
#                 where food_id IN {result_food_tuple};"""
#     cur.execute(query)
#     result = cur.fetchall()
#     cur.close()

#     print(result)