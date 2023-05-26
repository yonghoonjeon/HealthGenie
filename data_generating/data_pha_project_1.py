import psycopg2
import datetime 
import random
import time 
import csv 
import pandas as pd
import my_db_setting 
'''
insert into pha_project (project_id,
	is_achieved ,
	p_name ,
    cur_weight,
    goal_weight,
	goal_bmi ,
    goal_type,
    create_time,
	start_time,
	end_time ,
	user_id)
values 
;

'''


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    stime =time.mktime(time.strptime(start, time_format))
    etime =time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop)



list_project_name = ['you can do it', 'my first project', 'my second project',
                     'my 1st project','my 2nd project', 'when will my life begine',
                     'outrageous','move my doby', 'body building contest','Diet is on',
                     'lose some pounds', 'endless diet','back in the 90s',
                     'fit girs', 'endless game', 'game is on', 'chicken breask will hate me',
                     'project that will be accomplished', 'when will my semester end',
                     'beautiful days', 'life is good',' my third project','I love Micheal Jackson',
                     'chicken day', 'for summer vacation', 'maintin my body weight', 'fat avoiding',
                     'what will be the result', 'life is a game full of quests', 'data scientist project',
                     'coding example', 'first diet ever', 'for my game', 'what will be my limit',
                     'for the endless game','ends will come', 'gain muscles','muscle building',
                     '5 kg project',' 10kg project', 'my_project', 'my goal', 'goal of 2023', 'goal of this year',
                     'my first goal of the year', 'best year ever', 'for my performace',
                     '2 weeks project', '1 month project', '1 year project', '2 year project',
                     'muscles', 'no fat or carbs projects', 'vegan project','vegetarian project',
                     'toward bmi 23', 'toward to my lowest weight', 'get 10 kg muscle obtaining',
                     'Dont be upset', 'you are a lifetime', 'lifetime game changer',
                     'you are the most beautiful creature','when my diet will be end','lose weight!',
                     'lose some weight', 'can I lose my weight', 'It is time to lose weight',
                      'my life will complete by you','not sober but can not think straight','notebook',
                       'diet diary', 'health diary', 'tracking my diet', 'tracking my health life',
                    'when will my life begin', 'all I record my life', 'recording my health life',
                    'diet tracking', 'meal tracking', 'phantom of the fat', 'off my face',
                    'watermelon is so cool', 'my project is on', 'was it ever on?','I can do it',
                    'Yes I can', 'shortest diet', 'loves game', 'loves losing weight']


############################ connect to the postgres #############

conn = my_db_setting.my_db_setting()

cur = conn.cursor()

query = f""" 
        select user_id, height, weight, date_joined
        from pha_user
        where is_superuser = false
		order by user_id asc;
        """
cur.execute(query)
data = cur.fetchall()

# list_min_w = [50, 65, 35, 55, 50, 56, 56, 40, 50, 70,60]
# list_max_w = [75, 85, 55, 80, 70, 75, 80, 60, 75, 100, 80] 
# height = [180, 178, 156, 174, 167, 173, 163, 145, 160, 177, 150]
# list_joined_time = [datetime.datetime(2022, 4, 25, 20,0,0), datetime.datetime(2022, 1, 1, 20, 0,0), datetime.datetime(2022,2,2,20,0,0), datetime.datetime(2022, 1, 2, 20,0,0), datetime.datetime(2022, 1,3,20,0,0), datetime.datetime(2022, 3, 1, 20, 0,0), datetime.datetime(2022, 1, 15, 20, 0,0),
#                     datetime.datetime(2022, 1, 3, 20,0,0), datetime.datetime(2022, 1, 25, 21, 0,0), datetime.datetime(2022, 1, 30, 21, 0,0), datetime.datetime(2022, 1, 4, 21, 0,0), 
#                     ]
# list_end_time = [datetime.datetime(2022, 12, 30, 23, 59,59) for user in range(2, 13)]
list_joined_time = []
list_min_w = []
list_max_w = []
list_height = []
list_user_id = []
for row in data:
    list_joined_time.append(row[3])
    list_min_w.append(row[2]-10)
    list_max_w.append(row[2]+10)
    list_height.append(row[1])
    list_user_id.append(row[0])


# project duration in month 
set_duration = [1, 3, 4, 5, 6]

query_list = []

##################parameters #########################################
project_id = 1

# 5 projects per each person 
for idx, user_id in enumerate(list_user_id):
    for j in range(0, 5):
        #p_name 
        p_idx = random.randrange(0, len(list_project_name))
        p_name = list_project_name[p_idx]
        
        # goal_weight, goal_type 
        goal_weight = random.uniform(list_min_w[idx], list_max_w[idx])
    

        if j < 3:
            cur_weight = goal_weight - random.uniform(1, 10)
            goal_type = 'diet'
        else: 
            cur_weight = goal_weight + random.uniform(1, 5)
            goal_type = 'putting on weight'
        
        # goal_bmi 
        goal_bmi = goal_weight / ((list_height[idx] *0.01)**2)

        # randomly pick start_time 
        start = str(list_joined_time[idx])
        end = str(datetime.datetime.today())
        
        random_date_ = random_date(start[0:19], end[0:19], random.random())
        start_time = datetime.datetime.strptime(random_date_, '%Y-%m-%d %H:%M:%S')

        # end_time 
        end_idx = random.randrange(0, len(set_duration))
        month_to_add = set_duration[end_idx]
        end_time = start_time + datetime.timedelta(days = 365/12 * month_to_add)
        end_time = end_time.replace(hour = 23, minute = 59, second = 59)

        #creating time 
        creating_time = start_time

        # Create a tuple with the values for the SQL query
        # assumption: user1은 admin user인 자기자신이며 user_id 2부터 실제 사용자임. 
        query_list.append((project_id, False, p_name, cur_weight, goal_weight, goal_bmi, goal_type, str(creating_time), str(start_time), str(end_time), user_id))
        project_id += 1 
        

#print(query_list)
# with open('pha_project_1.csv', mode='w', newline='') as file:
#     writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
#     writer.writerow(query_list)

for result_query in query_list:
    insert_query = f"""
                    insert into pha_project (project_id,
                    is_achieved ,
                    p_name ,
                    cur_weight,
                    goal_weight,
                    goal_bmi ,
                    goal_type,
                    create_time,
                    start_time,
                    end_time ,
                    user_id)
                values 
                {result_query};"""
    cur.execute(insert_query)
    conn.commit()