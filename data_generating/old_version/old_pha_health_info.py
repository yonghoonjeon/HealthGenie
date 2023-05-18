import random
import psycopg2
import csv
import datetime 

'''
create table pha_health_info(
	health_info int primary key,
	user_id int,
	project_id int,
	allergy_name varchar(50),
	activity_level varchar(20),
	diet_restriction varchar(25),
	update_time timestamptz,
	foreign key (user_id) references pha_user(us_id),
	foreign key (project_id) references pha_project(project_id)
);

insert into pha_health_info (health_info, user_id, project_id, allergy_name, activity_level, update_time, diet_restriction)
values 
;

'''

list_allergy_name = ['None','gluten', 'soybeans', 'eggs','dairy','tree nuts','peanuts','fish','shellfish']
list_activity_level =['sedentary','moderate', 'active']
list_diet_restriction = ['None','vegeterian','vegan','halal','kosher','gluten_intolerance']

#list_user_id = list(range(2, 13))

conn = psycopg2.connect(
    host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
    database = 'postgres',
    user = 'postgres',
    password = '0847'
)
cur = conn.cursor()
cur.execute("select us_id from pha_user where is_superuser = false;")
users_result = cur.fetchall()
cur.close()

query_list = []
project_id = 1
health_info = 1

for user_id in users_result:

    # user_id 
    i = user_id[0]

    # 최대 두 개 allergy가질 수 있음을 가정 
    set_cur_allergy = set()
    set_cur_diet_restriction = set()
    list_cur_allergy = []
    list_cur_diet_restriction = []

    for k in range(0, 2):
        # allergy name 
        allergy_idx = random.randrange(0, len(list_allergy_name))
        allergy_name = list_allergy_name[allergy_idx]
        set_cur_allergy.add(allergy_name)
        
    if 'None' in set_cur_allergy:

        allergy_name = 'None'
        activity_level = ''
        # 5 project per each person
        for j in range(0, 5):
            # activity level
            if j == 0:
                activity_idx = random.randrange(0, len(list_activity_level))
                activity_level = list_activity_level[activity_idx]
            elif j != 0:
                while True:
                    new_activity_idx = random.randrange(0, len(list_activity_level))
                    if new_activity_idx != activity_idx:
                        activity_idx = new_activity_idx
                        break
                activity_level = list_activity_level[activity_idx]
            
            # update_time = after project start time 
            conn = psycopg2.connect(
                host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
                database = 'postgres',
                user = 'postgres',
                password = '0847'
            )
            cur = conn.cursor()
            cur.execute("select creating_time from pha_project where project_id = %s;", (project_id,))
            update_time = cur.fetchall()
            cur.close()
            if update_time:
                update_time = update_time[0][0].strftime('%Y-%m-%d %H:%M:%S')
                #update_time = datetime.datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
            else:
                print(project_id)

            #diet resctrction 
            # 최대 2개의 diet restrcition을 가질 수 있음 
            for k in range(0,2):
                diet_idx = random.randrange(0, len(list_diet_restriction))
                diet_restriction = list_diet_restriction[diet_idx]
                set_cur_diet_restriction.add(diet_restriction)
            if 'None' in set_cur_diet_restriction:
                list_cur_diet_restriction = ['None']
                for restriction in range(len(list_cur_diet_restriction)):
                    query_list.append((health_info, i, project_id, allergy_name, activity_level, update_time, list_cur_diet_restriction[restriction]))
                    health_info += 1 
            else:
                list_cur_diet_restriction = list(set_cur_diet_restriction)
                for restriction in range(len(list_cur_diet_restriction)):
                    query_list.append((health_info, i, project_id, allergy_name, activity_level, update_time, list_cur_diet_restriction[restriction]))
                    health_info += 1 

            project_id += 1
             
    else:
        list_cur_allergy = list(set_cur_allergy)
        for allergy_name in list_cur_allergy:
            # 5 project per each person
            for j in range(0, 5):
                # activity level
                if j == 0:
                    activity_idx = random.randrange(0, len(list_activity_level))
                    activity_level = list_activity_level[activity_idx]
                elif j != 0:
                    while True:
                        new_activity_idx = random.randrange(0, len(list_activity_level))
                        if new_activity_idx != activity_idx:
                            activity_idx = new_activity_idx
                            break
                    activity_level = list_activity_level[activity_idx]

                # update_time = after project start time 
                conn = psycopg2.connect(
                    host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
                    database = 'postgres',
                    user = 'postgres',
                    password = '0847'
                )
                cur = conn.cursor()
                cur.execute("select creating_time from pha_project where project_id = %s;", (project_id,))
                update_time = cur.fetchall()
                cur.close()
                if update_time:
                    update_time = update_time[0][0].strftime('%Y-%m-%d %H:%M:%S')
                    #update_time = datetime.datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                else:
                    print(project_id)
                # diet resctrction 
                # 최대 2개의 diet restrcition을 가질 수 있음 
                for k in range(0,2):
                    diet_idx = random.randrange(0, len(list_diet_restriction))
                    diet_restriction = list_diet_restriction[diet_idx]
                    set_cur_diet_restriction.add(diet_restriction)
                if 'None' in set_cur_diet_restriction:
                    list_cur_diet_restriction = ['None']
                    for restriction in range(len(list_cur_diet_restriction)):
                        query_list.append((health_info, i, project_id, allergy_name, activity_level, update_time, list_cur_diet_restriction[restriction]))
                        health_info += 1
                else:
                    list_cur_diet_restriction = list(set_cur_diet_restriction)
                    for restriction in range(len(list_cur_diet_restriction)):
                        query_list.append((health_info, i, project_id, allergy_name, activity_level, update_time, list_cur_diet_restriction[restriction]))
                        health_info += 1 

                
                project_id += 1

#print(query_list)
with open('health_info_data_generated.csv', mode='w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
    writer.writerow(query_list)
