#~*~ coding: iso-8859-1 ~*~

# Schoolsoft API
# Axel Engström, Europaskolan
# 2016-12-06

import requests
from secrets import USERNAME, PASSWORD
import time

DEBUG = False

def log(response, stdout=DEBUG):
    '''
    Logs responses status code, response headers and a slice of the raw html
    '''
    with open('responses.txt','a') as logfile:
        response.encoding = 'ISO-8859-1'
        logfile.write(response.text[-200:])
        logfile.write('\n')
        logfile.write(str(response.status_code))
        logfile.write('\n')
        logfile.write(str(response.headers))
        logfile.write('\n------------------------------------------\n')
    if stdout:
        print(response.text.encode('ascii','xmlcharrefreplace')[-200:])
        print(response.status_code)
        print(response.headers)
        print

session = requests.Session()
# Will change when project is finished, right now it resembles a normal browser User-Agent.
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}

login_url = 'https://sms3.schoolsoft.se/es/jsp/Login.jsp'

data = {'action':'login','usertype':1,'ssusername':USERNAME,'sspassword':PASSWORD,'button':'Logga in'}
response = session.post(login_url, data=data, headers=headers)
log(response)

time.sleep(2)


startmenu_url = 'https://sms3.schoolsoft.se/es/jsp/student/right_student_startpage.jsp'
data = {'menu':'schedule'}
get_schedule = session.get(startmenu_url, params=data, headers=headers)
log(get_schedule)

# Close connection manually so that the next request
# doesn't have to wait after Keepalive is dropped. 
requests.Response.close(response) 








