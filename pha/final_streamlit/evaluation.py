from surprise import SVD, Reader, Dataset
from surprise.model_selection import cross_validate
import pandas as pd 
import my_db_setting 
from surprise.model_selection import train_test_split

# Connect to the PostgreSQL database
conn = my_db_setting.my_db_setting()
cur = conn.cursor()

# for every user, for 14 days estimate a rating matrix of each user 
rating_query = f"""
                select temp.food_id_id, temp.user_id, temp.rating, temp.meal_time 
                from (
                select food_id_id, user_id, rating, meal_time, meals_id 
                from pha_meal 
                ORDER BY food_id_id, user_id, meal_time
                ) as temp 
                where temp.meal_time BETWEEN ( DATE(NOW()) - INTERVAL '14' DAY) AND DATE(NOW());
                """

cur.execute(rating_query)
result = cur.fetchall()

reader = Reader(rating_scale=(1, 5))
rating = pd.DataFrame(result)
rating.columns = ['food_id_id', 'user_id', 'rating', 'meal_time']
data = Dataset.load_from_df(rating[['user_id', 'food_id_id', 'rating']], reader)


# Split the dataset into training and testing sets
trainset, testset = train_test_split(data, test_size=.25)

# Train the model using SVD algorithm
algo = SVD()
algo.fit(trainset)

# Run 5-fold cross-validation and print results.
cross_validate(algo, testset, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# # accuracy
#from surprise import accuracy
# testset = trainset.build_testset()
# predictions = algo.test(testset)

# accuracy.rmse(predictions)
