import psycopg2
import datetime 
import my_db_setting

'''
run this code after insert pha_project_1.csv file into the DB 
'''

'''
한번에 얻는 쿼리 


select *
from pha_tracking 
join 
(
select user_id, temp.max_update_time, temp.project_id
from
(select project_id, max(update_time) as max_update_time
from pha_project
join pha_tracking on pha_tracking.user_id = pha_project.user_id 
where update_time <= pha_project.end_time
group by project_id 
order by project_id) as temp
join pha_project on pha_project.project_id = temp.project_id) as final on pha_tracking.user_id = final.user_id
where pha_tracking.user_id = final.user_id and pha_tracking.update_time = final.max_update_time
;


'''

############################ connect to the postgres #############

conn = my_db_setting.my_db_setting()
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
where update_time <= pha_project.end_time
group by project_id 
order by project_id) as temp
join pha_project on pha_project.project_id = temp.project_id
;
"""
cur.execute(query)
full_data = cur.fetchall()

list_user_id = []
list_max_update_time = []
list_project_id = []
for each_idx, each in enumerate(full_data):
    list_user_id.append(each[0])
    list_max_update_time.append(each[1])
    list_project_id.append(each[2])



############is_achieved update 
################## 실제 update_weight 기준으로 DB연결해서 해서 is_achieved 상태 update 필요 
for user_id, max_update_time, project_id in zip(list_user_id, list_max_update_time, list_project_id):
    project_query = f"""
                    select end_time, goal_type, goal_weight
                    from pha_project
                    where user_id = {user_id} and project_id = {project_id};
                    """
    cur.execute(project_query)
    project_info = cur.fetchall()
    end_time = project_info[0][0]
    goal_type = project_info[0][1]
    goal_weight = project_info[0][2]

    weight_query = f"""
                    select cur_weight 
                    from pha_tracking 
                    where user_id = {user_id} and update_time = '{max_update_time}';
                    """
    cur.execute(weight_query)
    AT_WEIGHT = cur.fetchall()[0][0]
  
    # 프로젝트가 끝남 , 감소 목표
    if today > end_time and goal_type == 'diet':
        if goal_weight >= AT_WEIGHT:
       
            update_query = f"""
                UPDATE pha_project SET is_achieved = True 
                WHERE pha_project.project_id = {project_id} 
            """
            
        else:
         
            update_query = f"""
                UPDATE pha_project SET is_achieved = False 
                WHERE pha_project.project_id = {project_id}
            """
            
    # 프로젝트가 끝남, 증량 목표  
    elif today > end_time and goal_type == 'putting  on  weight':
        if goal_weight <= AT_WEIGHT:
            
            update_query = f"""
                UPDATE pha_project SET is_achieved = True
                WHERE pha_project.project_id = {project_id}
            """
            
        else:
           
            update_query = f"""
                UPDATE pha_project SET is_achieved = False 
                WHERE pha_project.project_id = {project_id}
            """
            
    #프로젝트가 안 끝남 
    elif today < end_time:
        
        update_query = f"""
                UPDATE pha_project SET is_achieved = False 
                WHERE pha_project.project_id = {project_id}
            """
        
    cur.execute(update_query)
    conn.commit()
cur.close()        
conn.close()