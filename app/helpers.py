"""
Helper methods for the c150.data data retrieval process
"""

from app import logger as log
import pymysql
import datetime
import requests
import operator

from authlib.client import OAuth2Session


remote = False # CHANGE FOR DB CONNECTION

# DB schema
db_schema_name = "c150data"
# Local config
db_local_host = "localhost"
db_local_user = "root"
db_local_passwd = ""
db_local_port = 3306
# Remote config
db_remote_socket = "/var/run/mysqld/mysqld.sock" # In order to make connection on ssh it needs to use a socket instead of host
db_remote_port = 3306 
db_remote_user = "mamsterdam"
db_remote_passwd = "Columbia150"
# DB tables
db_auth_token_table = "auth_token"
db_athletes_table = "athletes"

# TP API constants 
grant_type = "refresh_token"
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
api_base_url = 'https://api.sandbox.trainingpeaks.com' # Will change when we get production access
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
refresh_padding_time = 300
redirect_uri = "www.c150data.com" if remote else "localhost:5000"




def connectToDB():
    """
    Gets a Connection object
    
    Returns:
        Connection: On success 
        None: on error
    """
    try:
        if remote:
            return pymysql.connect(unix_socket=db_remote_socket, user=db_remote_user,
                password=db_remote_passwd, db=db_schema_name)
        else: 
            return pymysql.connect(host=db_local_host, user=db_local_user, password=db_local_passwd,
                db=db_schema_name)
    except:
        log.eprint("ERROR: Connection to database failed.")
        return None


def executeSqlInsert(insert_stmnt):
    """
    Creates a connection, executes, and commits insert_stmnt
    
    Args:
        insert_stmnt (str): sql insert statement
    
    Returns:
        int: number of rows effected. 0 on error.
    """
    conn = connectToDB()
    if conn is not None:
        try:
            cursor = conn.cursor()
            num_rows_effected = cursor.execute(insert_stmnt)
            conn.commit()
            return num_rows_effected
        except:
            log.eprint("Failed to execute insert statement: " + insert_stmnt)
        finally:
            conn.close()
    return 0 


def executeSqlSelect(select_stmnt):
    """
    Executes select and returns the rows themselves
    
    Args:
        select_stmnt (str): sql select statement 
    
    Returns:
        Tuple of Rows (Tuples): cursor object that executed the select statement
        None: on error
    """
    conn = connectToDB()
    if conn is not None:
        try:
            cursor = conn.cursor()
            response = cursor.execute(select_stmnt)
            allRows = cursor.fetchall() # Looks like this line is the problem
            return allRows 
        except:
            log.eprint("Failed to execute select statement: " + select_stmnt)
        finally:
            conn.close()
    return None 



def insertNewToken(token):
    """
    Inserts token into database. This method does NOT do expiration date checking, 
    that is to be done by the method's caller 
    
    Args:
        token (dict): dict object with the following fields: access_token, token_type, expires_in, refresh_token, and scope. 
    
    Returns:
        Boolean: True on successful insertion, False on unsuccessful insertion 
    """
    access_token, token_type, expires_in, refresh_token, scope = token['access_token'], token['token_type'], token['expires_in'], token['refresh_token'], token['scope']

    # Give the expires_in time an extra 5 minutes as padding time and remove microseconds
    expires_at_date = (datetime.datetime.now() + datetime.timedelta(seconds=(int(expires_in)-refresh_padding_time))).replace(microsecond=0)

    insert_statement = "INSERT INTO {} (`access_token`, `token_type`,`expires_at`, `refresh_token`, `scope`) VALUES ('{}', '{}', '{}', '{}','{}');".format(
            db_auth_token_table, access_token, token_type, expires_at_date, refresh_token, scope)

    numRows = executeSqlInsert(insert_statement)
    if numRows == 1:
        return True
    else:
        return False
    


def refreshAuthTokenIfNeeded():
    """
    Checks if auth_token needs refreshing, and refreshes if necessary
    
    Returns:
        Boolean: True if successful, otherwise False 
    """
    select_st = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
    rows = executeSqlSelect(select_st) # TODO change how we handle the rows object here

    success = False
    if rows is not None:
        refresh_date = rows[0][3] #TODO add constants here
        if refresh_date < datetime.datetime.now():
            success = refreshAuthToken(rows[0][4]) # Pass in the refresh_token from the most recent row
        else: 
            success = True
    return success 


def refreshAuthToken(refresh_token):
    """
    Makes an API call to get a new token and inserts it into the DB
    
    Args:
        refresh_token (str): Refresh token 
    
    Returns:
        Boolean: True if successful, False otherwise 
    """
    log.iprint("Refreshing authtoken...")
    oauth_session = OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
    body = "grant_type=refresh_token"
    updated_token = oauth_session.refresh_token(refresh_url,
                                                refresh_token=refresh_token,
                                                body=body)
    return insertNewToken(updated_token)


def getValidAuthToken():
    """
    Returns a valid authtoken to be used for API calls
    
    Returns:
        Row: The Row object of a valid token 
        None: On error
    """
    if refreshAuthTokenIfNeeded() is False:
        print("Could not successfully refresh auth token.")
        return None

    select_st = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
    result = executeSqlSelect(select_st)
    if result is not None:
        return result[0]
    else:
        return None


def getAPIRequestHeaders():
    token_row = getValidAuthToken()
    if token_row is not None:
        return {'host': 'api.sandbox.trainingpeaks.com','content-type':
                'application/json', 'Authorization': 'Bearer ' + token_row[1]}
    return None



# def getHoursForAthlete(id, start_date, end_date, headers):
#     """
#     TODO We will not need this once all the athletes and workouts are in the DB
#     """
#     print("Getting hours for athlete {}...".format(id))
#     api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)
#     response = requests.get(api_url, headers=headers)

#     json_response = response.json()
#     sum_hours = 0
#     for workout in json_response:
#         total_time = workout['TotalTime']
#         if type(total_time) is float:
#             sum_hours += float(total_time)
#     return sum_hours



# def getAllAthletesHours(start_date, end_date):
#     """
#     TODO We will not need this once all the workouts and athletes are in the DB
    
#     Args:
#         start_date ([type]): [description]
#         end_date ([type]): [description]
    
#     Returns:
#         [type]: [description]
#     """
#     headers = getAPIRequestHeaders()
#     r = requests.get('https://api.sandbox.trainingpeaks.com/v1/coach/athletes',
#                      headers=headers)
#     athletes = list()
#     req_json = r.json()
#     # convert inputted dates from MM/DD/YYYY to YYYY-MM-DD
#     dStart = datetime.datetime.strptime(start_date, '%m/%d/%Y')
#     dEnd = datetime.datetime.strptime(end_date, '%m/%d/%Y')
#     start_date_f = dStart.strftime('%Y-%m-%d')
#     end_date_f = dEnd.strftime('%Y-%m-%d')
#     # Create athlete object and add to list
#     count = 1 
#     for athlete in req_json:
#         log.eprint("Working on Athlete #", count)
#         # date formatted YYYY-MM-DD
#         hours = getHoursForAthlete(athlete['Id'],
#                                            start_date_f, end_date_f, headers)
#         rounded_hours = round(hours, 2)
#         athlete_info = {
#             "name": "{} {}".format(athlete["FirstName"], athlete["LastName"]),
#             "hours": hours,
#             "rounded_hours": rounded_hours
#         }
#         athletes.append(athlete_info)
#         count += 1

#     # sort list of athletes based on number of hours
#     sorted_athletes = sorted(athletes, key=operator.itemgetter('hours'), reverse=True)
#     print(sorted_athletes)

#     return (len(athletes), sorted_athletes)


def insertAllAthletesIntoDB():
    """
    Inserts all athletes into an empty athletes table in the database
    """
    return executeSqlInsert(buildSqlInsertForAthletes(getAllAthletes()))


def buildSqlInsertForAthletes(athletes):
    # sql_insert is a list of characters so it can be changed
    sql_insert =list("""
                    INSERT INTO athletes (id, name, email, date_last_updated_workouts)
                        VALUES
                """)
    if athletes is None:
        return None
    for athlete in athletes:
        sql_insert += list("({}, '{}', '{}', {}),".format(
            athlete["id"], 
            athlete["name"],
            athlete["email"],
            "NULL"
        ))
    sql_insert[len(sql_insert)-1] = ";" # Replace the last char in the insert statement (,) with a ;
    return ''.join(sql_insert)


def getAllAthletes():
    """
    Makes an API call to get every athlete under the current coach
    
    Returns:
        List of JSON object Athletes: Every JSON object has the fields: 'id', 'name', 'email', 'coachedBy' 
    """
    # Make the API call
    headers = getAPIRequestHeaders()
    if headers is None:
        return None
    response = requests.get('{}/v1/coach/athletes'.format(api_base_url),
                headers=getAPIRequestHeaders())
    if response is None:
        return None
    athletes_to_return = list()
    for athlete in response.json():
        athletes_to_return.append({
            "id": athlete['Id'],
            "name": "{} {}".format(athlete['FirstName'], athlete['LastName']),
            "email": athlete['Email'],
            "coachedBy": athlete['CoachedBy']
        })
    return athletes_to_return


def insertWorkoutsIntoDb(start_date, end_date):
    athletes = getAllAthletes()
    all_workouts = list()
    for athlete in athletes:
        all_workouts += getWorkoutsForAthlete(athlete['id'], start_date, end_date) # Concat all_workouts with workouts for specific athlete
    executeSqlInsert(buildSqlInsertForWorkouts(all_workouts))


def getWorkoutsForAthlete(athlete_id):
    pass


def buildSqlInsertForWorkouts(workouts):
    sql_insert =list("""
                    INSERT INTO workouts (<WORKOUT FIELDS>)
                        VALUES
                """)
    if workouts is None:
        return None
    for workout in workouts:
        sql_insert += list("({}, '{}', '{}', {}),".format(
            workout["id"], 
            workout["name"],
            workout["email"]
            #etc.....
        ))
    sql_insert[len(sql_insert)-1] = ";" # Replace the last char in the insert statement (,) with a ;
    return ''.join(sql_insert)


    









