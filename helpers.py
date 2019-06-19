"""
Helper methods for the c150.data data retrieval process
"""

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


def eprint(description):
    print("ERROR: ", description)


def iprint(description):
    print("INFO: ", description)


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
        eprint("ERROR: Connection to database failed.")
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
            eprint("Failed to execute insert statement: ", insert_stmnt)
        finally:
            conn.close()
    return 0 


def executeSqlSelect(select_stmnt):
    """
    Executes select and returns the rows themselves
    
    Args:
        select_stmnt (str): sql select statement 
    
    Returns:
        List of Rows: cursor object that executed the select statement
        None: on error
    """
    conn = connectToDB()
    if conn is not None:
        try:
            cursor = conn.cursor()
            response = cursor.execute(select_stmnt)
            allRows = cursor.fetchall()
            iprint("What a list of rows looks like: ", allRows)
            return cursor.fetchall()
        except:
            eprint("Failed to execute insert statement: ", select_stmnt)
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
    if rows[0] is not None:
        refresh_date = rows[0][3] #TODO add constants here
        iprint("This is what a mySQL row looks like: ", rows[0])
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
    iprint("Refreshing authtoken...")
    oauth_session = OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
    body = "grant_type=refresh_token"
    updated_token = oauth_session.refresh_token(refresh_url,
                                                refresh_token=refresh_token,
                                                body=body)
    return insertNewToken(updated_token)


def getAuthToken():
    """
    Returns a valid authtoken to be used for API calls
    
    Returns:
        Row: The Row object of a valid token 
    """
    if refreshAuthTokenIfNeeded() is False:
        print("Could not successfully refresh auth token.")
        return None

    select_st = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
    result = executeSqlSelect(select_st)
    #TODO work on this
    if num_rows == 0:
        print("Error: An access token does not exist")
    return cursor.fetchone() # The first toke will be the most recently inserted one 
    except:
        print("Failed to fetch access_token")
    finally:
        conn.close()


def getHeaders():
    access_token = getAuthToken()[1]
    return {'host': 'api.sandbox.trainingpeaks.com','content-type':
            'application/json', 'Authorization': 'Bearer ' + access_token}



def getAthleteId():
    """
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/athlete/profile',
                     headers=getHeaders())
    id = (r.json())["Id"]
    return id
    """
    pass


def getHoursForAthlete(id, start_date, end_date, headers):
    print("Getting hours for athlete {}...".format(id))
    api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)
    response = requests.get(api_url, headers=headers)

    json_response = response.json()
    sum_hours = 0
    for workout in json_response:
        total_time = workout['TotalTime']
        if type(total_time) is float:
            sum_hours += float(total_time)
    return sum_hours



def getAllAthletesHours(start_date, end_date):
    headers = getHeaders()
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/coach/athletes',
                     headers=headers)
    athletes = list()
    req_json = r.json()
    # convert inputted dates from MM/DD/YYYY to YYYY-MM-DD
    dStart = datetime.datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.datetime.strptime(end_date, '%m/%d/%Y')
    start_date_f = dStart.strftime('%Y-%m-%d')
    end_date_f = dEnd.strftime('%Y-%m-%d')
    # Create athlete object and add to list
    count = 1 
    for athlete in req_json:
        eprint("Working on Athlete #", count)
        # date formatted YYYY-MM-DD
        hours = getHoursForAthlete(athlete['Id'],
                                           start_date_f, end_date_f, headers)
        rounded_hours = round(hours, 2)
        athlete_info = {
            "name": "{} {}".format(athlete["FirstName"], athlete["LastName"]),
            "hours": hours,
            "rounded_hours": rounded_hours
        }
        athletes.append(athlete_info)
        count += 1

    # sort list of athletes based on number of hours
    sorted_athletes = sorted(athletes, key=operator.itemgetter('hours'), reverse=True)
    print(sorted_athletes)

    return (len(athletes), sorted_athletes)


def insertAllAthletesIntoDB():
    sql_insert = str()
    sql_insert = """
                    INSERT INTO athletes('id', 'name', 'email', 'dob', 'coach_id', 'weight', 'last_updated_workouts')
                        VALUES
                    """
    athletes = getAllAthletes()
    for athlete in athletes:
        sql_insert.append("({}, {}, {}, {}, {}, {}, {}),")
    sql_insert[sql_insert.len()-1] = ";" # Replace the last char in the insert statement (,) with a ;
    execute_sql(sql_insert)
