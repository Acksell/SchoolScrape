
import re  #--> regular expression
from bs4 import BeautifulSoup

class ScheduleParser:
    def __init__(self, schedule_response):
        self.schedule_response = schedule_response
        self.soup = BeautifulSoup(schedule_response.text, 'html.parser')
        self.rows = self.soup.find_all('tr', class_='background schedulerow')

        self.MAX_COLSPAN = int(self.rows[0].find_all('td')[1]['colspan'])
        self.spans = dict(enumerate([[0]*self.MAX_COLSPAN for _ in range(5)]))
        self.schedule = self.map_to_days()
    
    def get_all_options(self):
        dropdown = ScheduleParser(ss.get_room_schedule(0)).soup.find_all('div', class_='btn-group')
        names_links = []
        for option in dropdown[1].find_all('a'):
            link = option.get('href')
            name = option.get_text()
            names_links.append({'name':name,'link':link})
        return names_links
    
    def _get_insertion_point(self):
        '''
        returns a tuple of the insertion indicies: (dayIndex, colIndex)
        used for determining which lesson goes to which day.
        '''
        #returns tuple pair with index and value of minimum integer in a list.
        mindx = lambda lst, nested: min(enumerate(lst), key=lambda item: item[1][1] if nested else item[1])
        candidates = [mindx(self.spans[i], nested=False) for i in range(5)]
        
        # winner is a tuple (dayIndex, (colIndex, value)) which represents the 
        # insertion coordinates and the value of the current minimum. We discard the 
        # minimum value when returning as it is only used for comparisons.
        winner = mindx(candidates, nested=True)
        return winner[0], winner[1][0]

    def map_to_days(self):
        # 0-4 <=> mon-fri
        schedule = {0:[],1:[],2:[],3:[],4:[]}
        for row in self.rows:
            td_tags = row.find_all('td')
            
            for tag in td_tags:
                insertion_day, insertion_col = self._get_insertion_point()
                if tag['class'] != ['schedulecell']:  # if it is a lesson or break
                    colspan = int(tag['colspan'])
                    rowspan = int(tag['rowspan'])
                    if tag['class'] == ['','schedulecell']:  # a lesson
                        for i in range(colspan):
                            self.spans[insertion_day][insertion_col + i] += rowspan
                        lesson_header = tag.div['title']
                        schedule[insertion_day].append(Lesson(lesson_header))
                    elif tag['class'] == ['light','schedulecell']:  # a break
                        for i in range(colspan):
                            self.spans[insertion_day][insertion_col + i] += rowspan
        return schedule

class Lesson(set):
    # Considered separating the parsing from this class but decided not to 
    # since the parsing will presumably not be upscaled and separating the 
    # two would only complicate things further and hinder readability.
    def __init__(self, lesson_header):
        self.lesson_header = lesson_header
        
        self.timespan = re.search(r'\d{1,2}:\d{2}\-\d{1,2}:\d{2}', lesson_header).group()
        self.name = re.findall(r'\d{1,2}:\d{2}\-\d{1,2}:\d{2} (.+)\] body=', lesson_header)[0]
        try:
            self.room = re.findall(r'Sal/resurs: (.+)(?:\\r\\n|\r\n)<br', lesson_header)[0]
        except IndexError:
            self.room = None
        self.start, self.end = map(hhmm_to_minutes, self.timespan.split('-'))
        
        super().__init__(range(self.start,self.end+1))
        
    def __str__(self):
        return '{} {} in {}'.format(self.timespan, self.name, self.room)

def hhmm_to_minutes(time, origin=510):
    '''
    Converts a timestring "hh:mm" to amount of seconds since origin.
    Default origin is 08:30 -> 510 minutes.
    '''
    hours, minutes = time.split(':')
    return int(hours)*60 + int(minutes) - origin

def minutes_to_hhmm(minutes, origin=510):
    return "%s:%s" % divmod(minutes, 60)
