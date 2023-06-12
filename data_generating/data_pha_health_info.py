import random
import psycopg2
import csv
import datetime 
import my_db_setting
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

insert into pha_healthinfo (health_info, allergy_name, activity_level, update_time, dietary_restriction, project_id_id, user_id_id)
values 
;

'''

list_allergy_name = ['None','gluten', 'soybeans', 'eggs','dairy','tree nuts','peanuts','fish','shellfish']
list_activity_level =['sedentary','moderate', 'active']
list_diet_restriction = ['None','vegeterian','vegan','halal','kosher','gluten_intolerance','lactose_intolerance']

#list_user_id = list(range(2, 13))

conn = my_db_setting.my_db_setting()
cur = conn.cursor()

project_query = f"""

                select project_id, temp.user_id
from 
(select is_superuser, user_id
from pha_user) as temp
join pha_project on pha_project.user_id = temp.user_id 
where temp.is_superuser = false
order by temp.user_id, project_id
;
                """

cur.execute(project_query)
users_result = cur.fetchall()

list_project_id = []
list_user_id = []
for data in users_result:
    list_project_id.append(data[0])
    list_user_id.append(data[1])


health_info = 10
query_list= []
for project_id, user_id in zip(list_project_id, list_user_id):
    #allergy_name 
    allergy_idx = random.randrange(0, len(list_allergy_name)-1)
    allergy_name = list_allergy_name[allergy_idx]

    # activity_level 
    activity_idx = random.randrange(0, len(list_activity_level)-1)
    activity_level = list_activity_level[activity_idx]

    # update_time 
    # update_time = after project start time 
    cur.execute("select pha_project.create_time from pha_project where project_id = %s;", (project_id,))
    update_time = cur.fetchall()
    
    if update_time:
        update_time = update_time[0][0].strftime('%Y-%m-%d %H:%M:%S')
        #update_time = datetime.datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
    else:
        print(project_id)

    # restriction 
    restriction_idx = random.randrange(0, len(list_diet_restriction))
    restriction = list_diet_restriction[restriction_idx]

    query_list.append((health_info, allergy_name, activity_level, update_time, restriction, project_id, user_id))
    health_info += 1  


# with open('health_info_data_generated.csv', mode='w', newline='') as file:
#     writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
#     writer.writerow(query_list)

for result_query in query_list:
    insert_query = f"""
    insert into pha_healthinfo (health_info, allergy_name, activity_level, update_time, dietary_restriction, project_id_id, user_id_id)
    values {result_query}
    ;
    """
    cur.execute(insert_query)
    conn.commit()
