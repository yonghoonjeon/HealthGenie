import content_based_food_rec
import datetime 
import random 
import pandas as pd 
import my_db_setting

'''

create table pha_meal (
	meals_id int primary key, 
	meal_time timestamptz,
	meal_type varchar(100),
	serving_size int, 
	rating int, 
	food_id_id int, 
	user_id int,
	foreign key (user_id) references pha_user(user_id),
	foreign key (food_id_id) references pha_food(food_id)
)

insert into pha_meal (meals_id, meal_time, meal_type, serving_size, rating, food_id_id, user_id) 
values 
;
'''


#################util function #########################

def generate_dates(start_date):
    dates = []
    current_date = start_date

    # Generate dates for one year
    for _ in range(365 + 7*30):
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
            #current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S.%f%z')
            current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S%z')
        current_date += datetime.timedelta(days=1)

    return dates

############# setting ##############################
meal_type_list = ['breakfast', 'lunch','dinner','snack']
list_serving_size = [25, 50, 100, 250, 200, 250, 300, 400, 500]

conn = my_db_setting.my_db_setting()
cur = conn.cursor()

cur.execute("select user_id, date_joined from pha_user where is_superuser = false order by user_id asc;")
data = cur.fetchall()



list_user_id = []
list_joined_time = []

for each_idx, each in enumerate(data):
    list_user_id.append(each[0])
    list_joined_time.append(each[1])


food_query = "select * from pha_food order by food_id"
cur.execute(food_query)
food_data = cur.fetchall()

df_food = pd.DataFrame(food_data, columns = ['food_id','f_name','calories','protein','fat', 'carbs','ref_serving_size','cuisine','ingredients','allergen','dietary_restriction','flavor_profile','food_category'])


list_food_id = []
list_food_name = []
for data in food_data:
    list_food_id.append(data[0])
    list_food_name.append(data[1])

#list up similar 90 foods for each food 
recommendation_list = []
for i in range(0, len(list_food_name)):
    # food name은 string 
    result = content_based_food_rec.get_recommendations(list_food_name[i])
    #print(i, len(result))
    # food_idx 0 , 23은 이상하게 result길이가 2인데, 이거 a.any() 때문인듯,,,?
    # 0 ['hot-dog', 'apple']
    # 23 ['hot-dog', 'apple']
    # 데이터가 너무 비슷해서 recommendation list가 좀 비슷하긴 함...
    recommendation_list.append(result)

len_food = len(list_food_id)
##########################################

query_list = []
meal_id = 1
for user_id, joined_time in zip(list_user_id, list_joined_time):
    start = str(joined_time)
    list_dates = generate_dates(start)

    for date_idx, date in enumerate(list_dates): # date, hour, minute, second 
        #meal_type 
        meal_type_idx = random.randint(0, 3)
        meal_type = meal_type_list[meal_type_idx]

        # food_id, rating 
        store_food_idx = [] # reset 
        how_many_food_in_a_meal = random.randint(0, 4)
        for k in range(how_many_food_in_a_meal):
            if k == 0:
                new_food_idx = random.randint(0, len_food-1)
            else:
                while new_food_idx in store_food_idx: 
                    new_food_idx = random.randint(0, len_food-1)
            food_idx = new_food_idx 
            store_food_idx.append(food_idx) # no same food in the meal 
        
        # food_id 
        # randomly pick index for picking one row in recommendation_list 
        random_rec_idx = random.randint(0, len_food-1)
        food_list = recommendation_list[random_rec_idx]
        if len(food_list) == len_food:
            for food_idx in store_food_idx: # how_many_food_in_a_meal 
                food_name = food_list[food_idx]
                filtered_df = df_food[df_food['f_name'] == food_name]
                food_id = filtered_df['food_id'].iloc[0]

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
                

                # serving size 
                size_idx = random.randrange(0, len(list_serving_size))
                serving_size = list_serving_size[size_idx]

                ################query_append 
                query_list.append((meal_id, str(date), meal_type, serving_size, rating, food_id, user_id))
                meal_id += 1
                # if date_idx < len(list_dates):
                #    query_list.append(',')
        else: # food_idx = 0, 23 
            #meal_id, meal_time, meal_type, user_id는 그대로 
            food_id = 23 
            rating = 3 
            serving_size = 100 
            query_list.append((meal_id, str(date), meal_type, serving_size, rating, food_id, user_id))
            meal_id += 1
            
            # if date_idx < len(list_dates):
            #    query_list.append(',')
for result_query in query_list:
    insert_query = f"""
    insert into pha_meal (meals_id, meal_time, meal_type, serving_size, rating, food_id_id, user_id)
    values {result_query}
    ;
    """
    cur.execute(insert_query)
    conn.commit()
