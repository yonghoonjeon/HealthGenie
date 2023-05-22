from scipy.sparse import csc_matrix
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np
from pandasql import sqldf
# compute Term Frequency - Inverse Document Frequency (TF-IDF) vectors for each food information 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import psycopg2
import my_db_setting

def pre_process():
    conn = my_db_setting.my_db_setting()
    cur = conn.cursor()

    user_query = f"""
                select *
                from pha_user
                where is_superuser = false;
                """

    cur.execute(user_query)
    users_result = cur.fetchall()

    pha_user = pd.DataFrame(users_result, columns = ['password', 'last_login', 'is_superuser','user_id','user_name','email','is_staff','is_active','date_joined','sex','age','height','weight'])
    #pha_user = pha_user[pha_user['is_superuser'] != True]

    health_info_query = f"""
                        select *
                        from pha_healthinfo;
                        """
    cur.execute(health_info_query)
    health_info_data = cur.fetchall()

    pha_health_info = pd.DataFrame(health_info_data, columns = ['health_info', 'allergy_name', 'activity_level', 'update_time', 'dietary_restriction', 'project_id_id', 'user_id_id'])
    
    project_query = f"""
                    select *
                    from pha_project;
                    """
    
    cur.execute(project_query)
    project_data = cur.fetchall()

    pha_project = pd.DataFrame(project_data, columns = ['project_id','is_achieved' ,'p_name' ,'cur_weight','goal_weight','goal_bmi' ,'goal_type','create_time','start_time','end_time','user_id'])

    # define a TF-IDF Vectorizer Object. Remove all english stop words such 'the' ,' a'
    tfidf =  TfidfVectorizer(stop_words = 'english')

    # combine all foods information into a new column: activity_lvel, goal_bmi, goal_type 
    pha_user['concat_col'] = pha_health_info['activity_level'] + ',' + pha_project['goal_bmi'].astype(str) + ',' + pha_project['goal_type']
    #print(pha_user.head(2))

    # Construct the required TF-IDF matrix by fitting and transforming the data 
    tfidf_matrix = tfidf.fit_transform(pha_user['concat_col'])  

    # 256 different words were used to describe the 49 foods 
    #print(tfidf_matrix.shape)

    # compute a similarity score : Pearson, eucliean, cosine similarity scores 
    # cosine similarity scores 
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # reverse mapping of movie titles and dataframe indices 
    # a mechanism to idenity the index of a movie in our metadata DataFrame, given its title
    indices = pd.Series(pha_user.index, index = pha_user['user_id']).drop_duplicates()
    return cosine_sim, indices, pha_user 

# define recommendation function 
def get_recommendations(user_id):
    
    cosine_sim, indices, pha_user = pre_process()

    # get the index of the food that matches the name 
    idx = indices[user_id]

    # get the pairwise similarity scores of all foods with that food
    sim_scores = list(enumerate(cosine_sim[idx]))

    # sort the foods based on the similarity scores 
    sim_scores = sorted(sim_scores, key= lambda x : x[1], reverse = True)

    # Get the scores of the 10 most similar foods
    user_indices = [i[0] for i in sim_scores]

    # return the top 10 nist sunukar moview 
    return list(pha_user['user_id'].iloc[user_indices])


def return_result(result_list):
    return result_list

'''
if __name__ == '__main__':
    pha_user= pd.read_csv('pha_user.csv')
    pha_user = pha_user[pha_user['is_superuser'] != True]
    recommendation_list = []
    n_user = len(list(pha_user['us_id']))
    for i in range(0, n_user-1):
        result = get_recommendations(pha_user['us_id'].iloc[i])
        recommendation_list.append(result)
    #list up similar users for each user
    print(recommendation_list, len(recommendation_list[0]))
'''