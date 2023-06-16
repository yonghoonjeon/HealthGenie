import datetime 
import random 
import my_db_setting


# delete from pha_healthinfo;
# delete from pha_meal;
# delete from pha_project;
# delete from pha_tracking;
# delete from pha_user;

# Connect to the PostgreSQL database
conn = my_db_setting.my_db_setting()
cur = conn.cursor()

# delete_meal_query = f"DELETE FROM pha_meal WHERE user_id IN (SELECT user_id FROM pha_meal);"
# cur.execute(delete_meal_query)

# delete_project_query = f"DELETE FROM pha_project WHERE user_id IN (SELECT user_id FROM pha_project);"
# cur.execute(delete_project_query)

# delete_healthinfo_query = f"DELETE FROM pha_healthinfo WHERE user_id_id IN (SELECT user_id_id FROM pha_healthinfo);"
# cur.execute(delete_healthinfo_query)

# delete_tracking_query = f"DELETE FROM pha_healthinfo WHERE user_id_id IN (SELECT user_id_id FROM pha_healthinfo);"
# cur.execute(delete_healthinfo_query)

# Construct the SQL DELETE statement

# Commit the changes
#conn.commit()

# 40 people 
list_user_name = [
    'JaneKim', 'DayeLee', 'TeasupKim', 'JaejinLee', 'SeraLee', 'SojungYeon','YeonJung', 'SeungunLee', 'KyuBChoi',
    'ByungChanKim', 'JaePill', 'DongKwan', 'Jonghwan', 'JaeMyung','HyoriLee', 'JugiHong','YoonjinNa', 'DonghwaKim',
    'KisungNam','OhjungSea', 'NamGilKim','AraChoi','Micheal','Scalet Johanson','Whiteny huston','Naive',
    'SangdongLee','KimNamKil' ,'Rain','Sunny','Soyeon Kim','Sangyook Lee','OhJunghWAN','hYUNGYONG','soonja',
    'Honaldo','kanadara','ohmakase','SommonNam','TaeHeeKim','Bonggil Lee','BongCham','Boodam','ComGuDAK',
    'SangsilNa', 'Olando', 'Baboo Lilm','Unaki','Solando' ,'Kibong Oh',
    'John', 'Mary', 'Michael', 'Jennifer', 'Sarah','Jessica', 'James', 'Emily', 'Robert', 'Emma', 'Joseph',
    'Elizabeth', 'Daniel', 'Lauren', 'Thomas','Ashley', 'Matthew', 'Olivia', 'Christopher', 'Hannah', 'Andrew',
    'Sophia', 'Grace', 'Nicholas', 'Ava', 'Ryan', 'Abigail', 'Jacob', 'Victoria', 'Brandon', 'Natalie', 'Jonathan',
    'Alexis', 'Samuel', 'Lily', 'Tyler', 'Chloe', 'Madison', 'Zachary', 'Alyssa', 'Nathan','Ella','Austin','Mia',
    'Ethan','Samantha','Christian','Haley','William', 'Anna', 'Alexander', 'Megan', 'Kayla', 'Dylan', 'Rachel',
    'Gabriel', 'Kaitlyn', 'Benjamin', 'Mackenzie', 'Joshua', 'Brooke', 'Elijah', 'Julia', 'Sydney', 'Jasmine',
    'Luke', 'Katherine', 'Isaac', 'Destiny', 'Jason', 'Alexandra', 'Caleb', 'Nicole', 'Paige', 'Jack', 'Maria',
    'Logan', 'Sara', 'Juan', 'Sophie', 'Kevin', 'Morgan', 'Isaiah', 'David', 'Katelyn', 'Allison', 'Aaron', 'Nevaeh',
    'Henry', 'Gabrielle', 'Owen', 'Jordan', 'Wyatt', 'Caroline', 'Cameron', 'Sierra', 'Liam', 'Ariana', 'Connor',
    'Audrey', 'Jayden', 'Maya', 'Noah', 'Claire', 'Evan', 'Autumn', 'Sebastian', 'Aiden', 'Brooklyn', 'Julian',
    'Jocelyn', 'Mason', 'Kimberly', 'Trevor', 'Vanessa', 'Alex', 'Melissa', 'Ian', 'Gabriella', 'Blake', 'Amelia',
    'Nathaniel', 'Trinity', 'Carson', 'Faith', 'Angel', 'Kylie', 'Riley', "Lillian", "Micah", "Leah", "Colton", "Savannah",
    "Jordan", "Maya", "Dominic", "Jade", "Xavier", "Rebecca", "Jaden", "Evelyn", "Parker", "Madeline", "Adam", "Grace","Jose"
]

# password = Jane902
password = "pbkdf2_sha256$260000$wAXbpU2jDq24g8V7HWkSxi$AwsjU0JX0Pa15iwyBaz9Q9293N/3e/O/1LLmpDOzjsQ="

random_number = random.randint(1, 1000)
mail_list = ['gmail.com', 'snu.ac.kr', 'naver.com' , 'nate.com']

list_email = []
email = ""
for user_name in list_user_name:
    mail_idx = random.randint(0, len(mail_list)-1)
    email = user_name + str(random_number) + "@" + mail_list[mail_idx]
    list_email.append(email)

last_login = datetime.datetime.now()

is_superuser = False 
is_staff = False 
is_active = True 

date_joined = datetime.datetime(2022, 1, 1, 17, 2, 30)

list_sex = ['female','male']



query_list = []
user_id = 2
for user_name, email in zip(list_user_name, list_email):
    #sex 
    sex_idx = random.randint(0, 1)
    sex = list_sex[sex_idx]

    age = random.randint(20, 50)
    height = random.randrange(155, 185)
    weight = random.randrange(50, 80)

    query_list.append((password, str(last_login), 'false', user_id, user_name, email, 'false', 'true', str(date_joined), sex, age, height, weight))
    user_id += 1 

for result_query in query_list:
    insert_query = f"""
                    insert into pha_user (password, last_login, is_superuser, user_id, user_name, email, is_staff, is_active,date_joined, sex, age, height, weight)
                    values {result_query}
                    """
    cur.execute(insert_query)
    conn.commit()

update_date_query = f"""UPDATE pha_user
SET date_joined = date_joined::timestamp AT TIME ZONE 'UTC' + INTERVAL '9 hours 30 minutes';"""

cur.execute(update_date_query)
conn.commit()

last_login_update_query = f"""
                            UPDATE pha_user
SET last_login = last_login::timestamp AT TIME ZONE 'UTC' + INTERVAL '9 hours 30 minutes';
                            """

cur.execute(last_login_update_query)
conn.commit()

# Close the cursor and the database connection
cur.close()
conn.close()
