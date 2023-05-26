#ref: https://verificationkr.tistory.com/580

import random 
import datetime 
import time
import csv
import psycopg2
import my_db_setting
'''
insert into pha_tracking (track_id, update_time, cur_weight, user_id)
values;

'''

# def str_time_prop(start, end, time_format, prop, n_data):
#     """Get a time at a proportion of a range of two formatted times.

#     start and end should be strings specifying times formatted in the
#     given format (strftime-style), giving an interval [start, end].
#     prop specifies how a proportion of the interval to be taken after
#     start.  The returned time will be in the specified format.
#     """
#     if n_data < 12*30*3:
#         stime =time.mktime(time.strptime('2022-'+start, time_format))
#         etime =time.mktime(time.strptime('2022-'+end, time_format))

#         ptime = stime + prop * (etime - stime)
#     else:
#         stime =time.mktime(time.strptime('2023-'+start, time_format))
#         etime =time.mktime(time.strptime('2023-'+end, time_format))

#         ptime = stime + prop * (etime - stime)

#     return time.strftime(time_format, time.localtime(ptime))


# def random_date(start, end, prop, n_data):
#     return str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop, n_data)

def generate_dates(start_date):
    dates = []
    current_date = start_date

    # Generate dates for one year
    for _ in range(365 + 30*4 + 25):
        #cur_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
        
        rhour = random.randrange(7, 24)    
        rminute = random.randrange(0, 60)
        rsec = random.randrange(0, 60)

        result = current_date.replace(hour=rhour, minute=rminute, second=rsec)

        dates.append(result.strftime('%Y-%m-%d %H:%M:%S'))
        current_date += datetime.timedelta(days=1)

    return dates

########## setting ##########################
conn = my_db_setting.my_db_setting()
cur = conn.cursor()

cur.execute("select user_id, date_joined, weight from pha_user where is_superuser = false;")
data = cur.fetchall()


list_min_w = []
list_max_w = []
list_user_id = []
list_joined_time = []
list_current_weight = []
for each_idx, each in enumerate(data):
    list_min_w.append(each[2] - 15)
    list_max_w.append(each[2] + 15)
    list_user_id.append(each[0])
    list_joined_time.append(each[1])
    list_current_weight.append(each[2])

set_duration_of_project = list(range(5))
############################################################# generating data 
track_id = 1
query_list = []
for user_id, joined_time, min_w, max_w, cur_weight in zip(list_user_id, list_joined_time, list_min_w, list_max_w, list_current_weight):


    # 2022년때 12*30, 2023년 7월까지 데이터 생성  
    joined_time = datetime.datetime.strptime(str(joined_time)[0:19], '%Y-%m-%d %H:%M:%S')
    list_update_time = generate_dates(joined_time) 
    r_duration = random.randint(2, 5)
    for time_idx, update_time in enumerate(list_update_time): 
           
        # start = str(joined_time)
        # end_time = datetime.datetime(2023, 7, 31, 23,59,59)
        # end = str(end_time)
        
        # # if i <12*30*3:
        # #     random_date_ = random_date(start[5:19], end[5:19], random.random(), i)
        # #     random_date_ = datetime.datetime.strptime(random_date_, '%Y-%m-%d %H:%M:%S')
        # # else:
        # #     start_time = datetime.datetime(2023, 1, 1, 0,0,0)
        # #     start = str(start_time)
        # #     end_time = datetime.datetime(2023, 7, 31, 23,59,59)
        # #     end = str(end_time)
        # #     random_date_ = random_date(start[5:19], end[5:19], random.random(), i)
        # #     random_date_ = datetime.datetime.strptime(random_date_, '%Y-%m-%d %H:%M:%S')
        # date_format = "%Y-%m-%d %H:%M:%S"
        # datetime1 = datetime.strptime(joined_time, date_format)
        # datetime2 = datetime.strptime(end_time, date_format)
        if time_idx == 0:
            update_weight = cur_weight 
        else:
            if update_weight >= min_w:
                if time_idx < 30 * r_duration :
                    if time_idx == 0:
                        update_weight = cur_weight - 0.15
                    else:
                        update_weight -= 0.15
                elif 30*r_duration <= time_idx < 30*r_duration*2: 
                    update_weight += 0.001
                elif 30*r_duration*2 <= time_idx < 30*r_duration*r_duration*r_duration:
                    update_weight -= 0.001
                elif 30*r_duration*r_duration*r_duration<= time_idx < 30*r_duration*r_duration*r_duration*r_duration:
                    update_weight += 0.2
            elif update_weight < min_w:
                update_weight += 0.5
            elif update_weight >= max_w:
                update_weight -= 0.3
        
        query_list.append((track_id, str(update_time), update_weight, user_id))
        track_id += 1
            
# with open('w_tracking_data_generated.csv', mode='w', newline='') as file:
#     writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
#     writer.writerow(query_list)

for result_query in query_list:
    insert_query = f"""
                    insert into pha_tracking (track_id, update_time, cur_weight, user_id)
                    values {result_query};
                    """
    cur.execute(insert_query)
    conn.commit()