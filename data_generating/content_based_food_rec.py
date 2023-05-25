#reference 

#- https://www.kaggle.com/code/ibtesama/getting-started-with-a-movie-recommendation-system#Collaborative-Filtering
#- https://realpython.com/build-recommendation-engine-collaborative-filtering/#memory-based


from scipy.sparse import csc_matrix
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np
from pandasql import sqldf
# compute Term Frequency - Inverse Document Frequency (TF-IDF) vectors for each food information 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import psycopg2
import csv 
import my_db_setting

def pre_process():
    #pha_user = pd.read_csv('./project_data/pha_user.csv')
    
    conn = my_db_setting.my_db_setting()
    cur = conn.cursor()
    food_query = f""" 
                select *
                from pha_food
                order by food_id;
                """
    cur.execute(food_query)
    food_data = cur.fetchall()
    #pha_food = pd.DataFrame(food_data, columns = ['food_id','f_name','calories','protein','fat', 'carbs','ref_serving_size','cuisine','ingredients','allergen','dietary_restriction','flavor_profile','food_category'])
    # define the path the file name for the CSV file 
    csv_filename = 'pha_food_from_DB.csv'

    # Write the data to the CSV file 
    with open(csv_filename, 'w', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([desc[0] for desc in cur.description])  # Write header
        writer.writerows(food_data)  # Write rows
    

    pha_food = pd.read_csv('./pha_food_from_DB.csv')
    
    # define a TF-IDF Vectorizer Object. Remove all english stop words such 'the' ,' a'
    tfidf =  TfidfVectorizer(stop_words = 'english')

    # combine all foods information into a new column: ingredient, cuisine, flavor, food_category
    pha_food['concat_col'] = pha_food['ingredients'] + ',' + pha_food['flavor_profile'] + ',' + pha_food['food_category'] + pha_food['cuisine']
    #print(pha_food.head(2))
    # Construct the required TF-IDF matrix by fitting and transforming the data 
    tfidf_matrix = tfidf.fit_transform(pha_food['concat_col'])  

    # 256 different words were used to describe the 49 foods 
    #print(tfidf_matrix.shape)

    # compute a similarity score : Pearson, eucliean, cosine similarity scores 
    # cosine similarity scores 
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # reverse mapping of movie titles and dataframe indices 
    # a mechanism to idenity the index of a movie in our metadata DataFrame, given its title

    indices = pd.Series(pha_food.index, index = pha_food['f_name']).drop_duplicates()
    return cosine_sim, indices, pha_food 

# define recommendation function 
def get_recommendations(f_name):
    
    cosine_sim, indices, pha_food = pre_process()

    # get the index of the food that matches the name 
    idx = indices[f_name]

    # get the pairwise similarity scores of all foods with that food
    sim_scores = list(enumerate(cosine_sim[idx]))

    # sort the foods based on the similarity scores 
    # 잘 모르겠으면 아래거 프린트 해봐라 
    #print("I'm the first one", len(sim_scores), len(sim_scores[0]), sim_scores)
    #print(sim_scores[0][1])
    #sim_scores = sorted(sim_scores[0][1], reverse=True)
    sim_scores.sort(key=lambda x: x[1].any(), reverse=True)

    # Get the scores of the 10 most similar foods
    # sim_scores = sim_scores[1:11]
    
    # we're gonna use all the list 

    food_indices = [i[0] for i in sim_scores]

    # return the top 10 nist sunukar moview 
    return list(pha_food['f_name'].iloc[food_indices])


def return_result(result_list):
    return result_list

'''
if __name__ == '__main__':
    pha_food = pd.read_csv('./project_data/pha_food.csv')
    recommendation_list = []
    for i in range(0, 49):
        result = get_recommendations(pha_food['f_name'].iloc[i])
        recommendation_list.append(result)
    #list up similar 49 food for each food 
    return_result(recommendation_list)
''' 
