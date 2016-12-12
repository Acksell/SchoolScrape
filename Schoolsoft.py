#~*~ coding: iso-8859-1 ~*~

# Schoolsoft API
# Axel Engström, Europaskolan
# 2016-12-06

import time
import requests

from secrets import USERNAME, PASSWORD


DEBUG = False

def log(response, *other):
    '''Logs responses status code, response headers and a slice of the raw html'''
    loglist = ['%d %s' % (response.status_code,response.reason), response.url, 
               response.history, response.headers] + list(other) + ['-------------------']
    with open('responses.txt','a') as logfile:
        write = lambda *objects: logfile.write(''.join(str(obj)+'\n' for obj in objects))
        response.encoding = 'ISO-8859-1'
        write(*loglist)
    if DEBUG: 
        for i in loglist[:-1]: print(i)

session = requests.Session()
# Will change when project is finished, right now it resembles a normal browser User-Agent.
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}

### Authentication
login_url = 'https://sms3.schoolsoft.se/es/jsp/Login.jsp'

data = {'action':'login','usertype':1,'ssusername':USERNAME,'sspassword':PASSWORD,'button':'Logga in'}
response = session.post(login_url, data=data, headers=headers)
log(response)

# Wait until next request
time.sleep(1)

### Get schedule
schedule_url = 'https://sms3.schoolsoft.se/es/jsp/student/right_student_schedule.jsp'
data = {'menu':'schedule'}
get_schedule = session.get(schedule_url, params=data, headers=headers)
log(get_schedule)


# Close connection manually so that the next request
# doesn't have to wait after Keepalive is dropped. 
requests.Response.close(response) 








