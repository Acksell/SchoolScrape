#-*- coding: iso-8859-1 -*-

# Schoolsoft API
# Axel Engström, Europaskolan
# 2016-12-06

import time
import datetime
import re

import requests

from secrets import USERNAME, PASSWORD


DEBUG = False

def log(response, *other):
    '''
    Logs the response's status code, final url destination, history of responses until
    final destination, received headers and anything else that was given.
    '''
    # Opted to not use starred unpacking syntax of python3.5 to make it more backwards 
    # compatible. The current solution of adding lists is rather ugly though.
    loglist = ['{} {}'.format(response.status_code, response.reason), response.url, 
               response.history, response.headers] + list(other) + ['-------------------']
    with open('responses.txt','a') as logfile:
        logfile.write(''.join(str(obj)+'\n' for obj in loglist))
    if DEBUG: 
        for i in loglist[:-1]: print(i)

class Schoolsoft:
    BASE_URL = 'https://sms3.schoolsoft.se/es/jsp/'  # Europaskolan
    # NOTE BUG /student/ might change if you're a teacher.
    SCHEDULE_PATH = BASE_URL + 'student/right_student_schedule.jsp'
    LOGIN_PATH = BASE_URL    + 'Login.jsp'
    
    def __init__(self, username, password, usertype=1):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.usertype = usertype #usertype 1==student
        
        # Will change when project is finished, right now it resembles a normal browser User-Agent.
        self.headers = {'User-Agent': 'https://github.com/Acksell/SchoolScrape'}
        
        self.last_logged_in = None
        self.login()
        self.schedule = {}
    
    def SSRequest(url, method='GET',logging=DEBUG):
        def decorator(function_to_be_wrapped):
            def schoolsoft_requester(self, *args,**kwargs):
                data = function_to_be_wrapped(self, *args, **kwargs)
                if 'term' in data and data['term'] is 0:  # default argument
                    data['term'] = datetime.date.today().isocalendar()[1]
                if method == 'POST':
                    response = self.session.post(url, data=data, headers=self.headers)
                else: # assumes no other method than GET and POST.
                    response = self.session.get(url, params=data, headers=self.headers)
                if logging: log(response)
                return response
            return schoolsoft_requester
        return decorator
    
    @SSRequest(LOGIN_PATH, method='POST')
    def login(self):
        self.last_logged_in = time.time()
        return {'ssusername':self.username, 'action':'login', 'usertype':self.usertype,
                'sspassword':self.password, 'button':'Logga in'}
    
    @SSRequest(SCHEDULE_PATH)
    def get_schedule(self, week=0):
        '''Gets the logged in user's schedule for a given week.'''
        return {'requestid':-2, 'type':0, 'teacher':0, 'student':0, 'room':0, 'term':week}
    
    @SSRequest(SCHEDULE_PATH)
    def get_room_schedule(self, room_id, week=0):
        '''Gets the schedule of the provided room for a given week.'''
        return {'requestid':-2, 'type':3, 'room':room_id, 'term':week}
    
    @SSRequest(SCHEDULE_PATH)
    def get_staff_schedule(self, staff_id, week=0):
        return {'requestid':-2, 'type':1, 'teacher':staff_id, 'term':week}

    @SSRequest(SCHEDULE_PATH)
    def get_student_schedule(self, student_id, week=0):
        return {'requestid':-2, 'type':2, 'student':student_id, 'term':week}
    
    @SSRequest(SCHEDULE_PATH)
    def get_class_schedule(self, class_id, week=0):
        return {'requestid':class_id, 'type':1, 'term':week}
    
    def __enter__(self):
        '''Allows use of the 'with' statement'''
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):  # TODO: will add error handling
        '''Allows use of the 'with' statement'''
        self.session.close()


