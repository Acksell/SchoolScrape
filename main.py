#-*- coding: iso-8859-1 -*-

# Schoolsoft API
# Axel Engström, Europaskolan
# 2017-03-18


###  scrapped ((x+b)(x+a)^2)/(2*b*a^2) + 0.5
def weight_function(t, a):
    '''
    Parameter t is time and a is when you are expected to leave.
    Weight function:
      t^p + t^p     e^(a-t)        e^a
     -----------*--------------*---------  , p = 2 
         a^p      1 + e^(a-t)    1 + e^a 
    '''
    from math import e
    p=2
    def logistic_function(t):
        return (e**(a-t))/(1.0+e**(a-t))
    
    return (-t**p + a**p)/(a**p)*logistic_function(t)/logistic_function(0)

def shift(A, shifting):
    '''Returns a set with all values in set `A` shifted by -`shifting`'''
    return set(i-shifting for i in A)

if __name__ == '__main__':
    import datetime
    import time
    from urllib.parse import urlparse, parse_qs
    
    from Schoolsoft import Schoolsoft
    from ScheduleParser import ScheduleParser, minutes_to_hhmm, hhmm_to_minutes
    from secrets import USERNAME, PASSWORD
    
    today = datetime.date.today().isocalendar()[2] - 1 # 0-6
    
    with Schoolsoft(USERNAME, PASSWORD) as ss:
        ALL_ROOMS = ScheduleParser(ss.get_room_schedule(0)).get_all_options()
        all_rooms = {}
        rooms = ['A', 'AC','B','C','D','E','F','GC','GvR','K','LdV','MC','N','O']
        for name, href in ALL_ROOMS[:]:
            # extract room_id from href params
            room_id = parse_qs(urlparse(href).query).get('room') 
            if room_id:
                room_id = room_id[0]
            if name in rooms:
                all_rooms[name] = ScheduleParser(ss.get_room_schedule(room_id))
                time.sleep(0.1)
                print('%s %s GET %s' % (room_id,name.encode(),href))
        
        end = hhmm_to_minutes(input("When do you need to go?"))
        now = hhmm_to_minutes(time.strftime("%H:%M"))
        spare_time = set(range(now, end))
        
        room_integrals = {}
        for roomname in rooms:
            room_today = all_rooms[roomname].schedule[today]
            booked = set()
            for lesson in room_today:
                booked |= lesson
            room_time = shift(spare_time - booked, now)
            integral = 0
            for t in room_time:
                integral += weight_function(t, end)
            room_integrals[roomname] = integral
        
        #can definitely grab data in the previous loop instead of repeating it in this one.
        best_rooms = sorted(room_integrals.items(), key=lambda x: x[1], reverse=True)
        for room in best_rooms:
            lesson_overlap = False
            for lesson in all_rooms[room[0]].schedule[today]:
                if (now >= lesson.start and end <= lesson.end) or end >= lesson.end > now or end > lesson.start >= now:
                    print(lesson)
                    lesson_overlap = True
            if not lesson_overlap:
                print('%s is completely up for grabs!' % room[0])
            ###TODO Don't include lessons that are yours, or allow to specify time interval.
            
            
    