import random 
import datetime 
import csv
import pandas as pd 
import content_based_food_rec
import psycopg2

'''
create table new_pha_meal(
	meal_id int,
	meal_time timestamptz,
	food_id int,
	user_id int,
	serving_size float,
	rating int,
	primary key (meal_id, meal_time, food_id, user_id),
	foreign key (user_id) references pha_user(us_id),
	foreign key (food_id) references pha_food(food_id)
)

insert into pha_meal (meals_id, meal_time, serving_size, rating, food_id_id, user_id)
values 

'''


# def str_time_prop(start, end, time_format, prop):
#     """Get a time at a proportion of a range of two formatted times.

#     start and end should be strings specifying times formatted in the
#     given format (strftime-style), giving an interval [start, end].
#     prop specifies how a proportion of the interval to be taken after
#     start.  The returned time will be in the specified format.
#     """

#     stime =time.mktime(time.strptime('2022-'+start, time_format))
#     etime =time.mktime(time.strptime('2022-'+end, time_format))

#     ptime = stime + prop * (etime - stime)

#     return time.strftime(time_format, time.localtime(ptime))


# def random_date(start, end, prop):
#     return str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop)


# def generate_dates(start_date):
#     dates = []
#     current_date = start_date # string

#     # Generate dates for one year
#     for _ in range(365 + 30*7):
#         #cur_time = current_date.strptime('%Y-%m-%d %H:%M:%S')
#         if _ == 0:
#             cur_time = datetime.datetime.strptime(current_date[0:19], '%Y-%m-%d %H:%M:%S') # datetime 
#         # at _ > 1, current_date is already datetime 
#         #else: 
#         #    cur_time = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S') 
        
#         n_meal = random.randint(1, 3) # assumes that every one eat 1~3 meals per day 
#         for j in range(n_meal): 
#             if j == 0:
#                 rhour = random.randrange(7, 14)
#             elif j == 1:
#                 rhour = random.randrange(17, 20)
#             else:
#                 rhour = random.randrange(20, 24)
#             rminute = random.randrange(0, 60)
#             rsec = random.randrange(0, 60)
        

#             result = cur_time.replace(hour=rhour, minute=rminute, second=rsec) # datetime 
#             dates.append(result.strftime('%Y-%m-%d %H:%M:%S')) # string in result_list 
#         current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
#         current_date += datetime.timedelta(days=1) 

#     return dates


meal_type = ['breakfast', 'lunch','dinner','snack']

def generate_dates(start_date):
    dates = []
    current_date = start_date

    # Generate dates for one year
    for _ in range(365 + 30*7):
        if isinstance(current_date, str):  # Check if current_date is a string
            cur_time = datetime.datetime.strptime(current_date[0:19], '%Y-%m-%d %H:%M:%S')
        else:
            cur_time = current_date
        
        n_meal = random.randint(1, 3)  # Assumes that everyone eats 1-3 meals per day
        for j in range(n_meal):
            if j == 0:
                rhour = random.randrange(7, 14)
            elif j == 1:
                rhour = random.randrange(17, 20)
            else:
                rhour = random.randrange(20, 24)
            rminute = random.randrange(0, 60)
            rsec = random.randrange(0, 60)

            result = cur_time.replace(hour=rhour, minute=rminute, second=rsec)
            dates.append(result.strftime('%Y-%m-%d %H:%M:%S'))
        
        if isinstance(current_date, str):  # Check if current_date is a string
            current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S.%f%z')
        current_date += datetime.timedelta(days=1)

    return dates

conn = psycopg2.connect(
    host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
    database = 'pha',
    user = 'postgres',
    password = '0847'
)
cur = conn.cursor()

cur.execute("select user_id, date_joined from pha_user where is_superuser = false order by user_id asc;")
data = cur.fetchall()



list_user_id = []
list_joined_time = []

for each_idx, each in enumerate(data):
    list_user_id.append(each[0])
    list_joined_time.append(each[1])
   

########## setting ##########################


start_meal_id = 1

list_serving_size = [25, 50, 100, 250, 200, 250, 300, 400, 500]


######################################################## 

food_query = "select * from pha_food order by food_id"
cur.execute(food_query)
food_data = cur.fetchall()


cur.close()
conn.close()

list_food_id = []
list_food_name = []
for data in food_data:
    list_food_id.append(data[0])
    list_food_name.append(data[1])



df_food = pd.DataFrame(food_data, columns = ['food_id','f_name','calories','protein','fat', 'carbs','ref_serving_size','cuisine','ingredients','allergen','dietary_restriction','flavor_profile','food_category'])

#list up similar 120 foods for each food 
recommendation_list = []
for i in range(0, len(list_food_name)):
    # food name은 string 
    result = content_based_food_rec.get_recommendations(list_food_name[i])
    recommendation_list.append(result)


#food_recommendation_result = content_based_food_rec.return_result(recommendation_list)


len_food = len(list_food_id)



query_list = []
meal_id = 1 
food_idx = 0
new_food_idx = 0

for user_id, joined_time in zip(list_user_id, list_joined_time):
    query_list = []
    #rate가 중요함. 
    start = str(joined_time)
    list_dates = generate_dates(start)
    
    for date in list_dates:
        # serving size 
        size_idx = random.randrange(0, len(list_serving_size))
        serving_size = list_serving_size[size_idx]

        #rating 
        #rated food per each user based on the content-based recommendation to avoid too much randomness 
        # assume that there are 3 foods in average per meal 
        store_food_idx = [] # reset 
        for k in range(3):
            if k == 0:
                new_food_idx = random.randint(0, len_food-1)
            else:
                while new_food_idx in store_food_idx:
                    new_food_idx = random.randint(0, len_food-1)
            food_idx = new_food_idx
            store_food_idx.append(food_idx) # no same food in the meal 
            
        # food_id  
        # randomly pick index for picking one row in recommendation_list 
        random_rec_idx = random.randint(0, len_food-1 )
        food_list = recommendation_list[random_rec_idx] # foods list 
        if len(food_list) == len_food:
            for food_idx in store_food_idx: # how_may_food_in_a_meal
                food_name = food_list[food_idx]
                filtered_df = df_food[df_food['f_name'] == food_name]
                food_id = filtered_df['food_id'].iloc[0]
                
                #food_list = food_recommendation_result[food_id-1]
                # 0 = didn't rate 
                if 1 <= food_list.index(food_name) < len_food/5:
                    rating_list = [0, 4, 5]
                    rating_idx = random.randrange(0, 3)
                    rating = rating_list[rating_idx]
                elif len_food/5 <= food_list.index(food_name) < len_food*2/5:
                    rating_list = [0, 3, 4]
                    rating_idx = random.randrange(0, 3)
                    rating = rating_list[rating_idx] 
                elif len_food*2/5 <= food_list.index(food_name) < len_food * 4/5:
                    rating_list = [0, 2, 3]
                    rating_idx = random.randrange(0, 3)
                    rating = rating_list[rating_idx]
                else:
                    rating_list = [0, 1, 2]
                    rating_idx = random.randrange(0, 3)
                    rating = rating_list[rating_idx]

                # Create a tuple with the values for the SQL query
                query_list.append((meal_id, meal_type, str(date), serving_size, rating, food_id, user_id))
                meal_id += 1
        else:
            if user_id != 1:
                print("there is something wrong the list of recommendation list: maybe lacking some food elements in recommendation list")
                print(len(food_list), len_food)
                print(food_list)
    #print(query_list)
    with open( str(user_id) + '_meal_data_generated.csv', mode='w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
        writer.writerow(query_list)