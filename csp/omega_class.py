from csp import *
from tabulate import tabulate
from search import *
import random
import string
import time
import json


class timeslots:#class for the time slots, is a combination of days and times, crucial for the scheduling of the courses
    def __init__(self, day, time):
        days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']#combination of days
        #Dr. Bakouny's note: it would be better to have individual days rather than day slots for more flexibility
        if day not in days:
            raise ValueError(f'Invalid day: {day}')
        if time not in ['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']:#all possible university time slots
            raise ValueError(f'Invalid time: {time}')
        
        self.day = day
        self.time = time
    
    def randomize(self):#function that creates a random time slot, mainly used for testing
        days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']
        times=['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']
        self.day=days[random.randint(0,4)]
        self.time=times[random.randint(0,8)]

    
    def __eq__(self, other):# equality operator for the timeslots, allows us to compare objects of the class
        return self.day == other.day and self.time == other.time

    def __str__(self):#string representation of the timeslot
        return f'{self.day} {self.time}'

class availability:#class for the availability of the professors and the rooms, contains a list of timeslots
    def __init__(self, timeslot_list=None):#constructor for the availability class
        if timeslot_list is None:
            timeslot_list = []
        self.timeslots = timeslot_list
        
    def fill_availability(self):#function that fills the availability with all possible time slots, mainly useful for the rooms, and generating brute domains
        days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']
        times = ['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']
        for day in days:
            for time in times:
                self.timeslots.append(timeslots(day, time))
    
    def remove_slot(self, timeslot):
        self.timeslots.remove(timeslot)
    def add_slot(self, timeslot):
        self.timeslots.append(timeslot)
    def __str__(self):
        return f'{self.timeslots}'
    def __eq__(self, other):
        return self.timeslots == other.timeslots

class Room:#class for the rooms, contains a room code, capacity and availability
    def __init__(self, code, capacity,av=availability() ):
        self.room_code = code
        self.capacity = capacity
 
        self.availability = av

    def add_slot(self, timeslot):
        self.availability.add_slot(timeslot)

    def remove_slot(self, timeslot):
        self.availability.remove_slot(timeslot)
    def __str__(self):
        return self.room_code
    
class Professor:#class for the professors, contains a name and availability
    def __init__(self, name,av=availability()):
        self.name = name
        self.availability = av
    def add_slot(self, timeslot):
        self.availability.add_slot(timeslot)

    def remove_slot(self, timeslot):
        self.availability.remove_slot(timeslot)
    
    def __str__(self):
        return self.name

class course_struct:#class for the courses, contains a course code, title, professor, room, time slot, department, enrollment and constraints
    def __init__(self, course_code, title, professor, room, time_slot, dep,enrollment=0,constraints=[]):
        self.course_code = course_code
        self.title = title
        self.professor = professor  
        self.room = room  
        self.time_slot = time_slot#up to be changed as per Dr. Bakouny's note
        self.enrollment = enrollment
        self.dep=dep
        self.constraints = constraints #list of constraint objects for the course to be judged in constraint function we give to the csp
    
    
    def __str__(self):
        return f'{self.course_code} - {self.title} - {self.professor} - {self.room} - {self.time_slot}'


class course_prof_abs: #class that represents a dictionary of courses and their ranked professors, ina format where each course should have 2 ranks of professors{1:[p1,p2], 2:[p3,p4]}, to be used in the domain generation 
    def __init__(self, course_prof_ranked):
        self.course_prof_ranked = course_prof_ranked

    def add_prof(self, course_code,rank, prof):#function that adds a professor to the course, in a specific rank
        self.course_prof_ranked[course_code][rank].append(prof)

    def remove_prof(self, course_code, prof):
        for prof_list in self.course_prof_ranked[course_code]:
           for p in prof_list:
               if p == prof:
                   prof_list.remove(p)
                   break
    def remove_prof(self, course_code, prof,rank):
        for prof in self.course_prof_ranked[course_code][rank]:
            if prof == prof:
                self.course_prof_ranked[course_code][rank].remove(prof)
                break


class csp_course_dom:#main class responsible for generating domains and neighbours for the csp, contains a list of courses, a course_prof_abs object and a list of rooms
    def __init__(self, course_list, course_prof_ranked, room_list,soft_constraints=None):#soft constraints not implemented yet
        self.course_list = course_list
        self.course_prof_observer = course_prof_ranked
        self.room_list = room_list
        self.soft_constraints = soft_constraints

    def generate_domains(self):#generates domains based on actual availability of professors and rooms, and the course_prof_abs object
        domains = {}
        for course in self.course_list:
            course_domain = []
            for prof in (self.course_prof_observer.course_prof_ranked[course.course_code][1] +self.course_prof_observer.course_prof_ranked[course.course_code][2]):
                for slot in prof.availability.timeslots:
                    for room in self.room_list:
                        course_domain.append(course_struct(course.course_code, course.title, prof, room, slot, course.dep))
            domains[course.course_code] = course_domain
        return domains
    def generate_neighbours(self):#generates neighbours for the csp, based on the course list
        neighbours = {}
        for course in self.course_list:
            neighbours[course.course_code] = [course2.course_code for course2 in self.course_list if course2.course_code != course.course_code]
        return neighbours



def generate_brute_domains(course_list, prof_list, room_list):#generates brute domains, where all possible combinations of professors, rooms and time slots are considered
    domains = {}
    availability1 = availability()
    availability1.fill_availability()
    for course in course_list:
        course_domain = []
        for prof in prof_list:
            for slot in availability1.timeslots:
                for room in room_list:
                    course_domain.append(course_struct(course.course_code, course.title, prof, room, slot, course.dep))
        domains[course.course_code] = course_domain
    return domains
    
def generate_random_string(length):
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for i in range(length))
    
    return random_string

def generate_random_domains(iter):#generates random domains, where professors, rooms and courses are generated randomly
    days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']
    times=['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']
    ts_list=[]
    p_list=[]
    r_list=[]
    c_list=[]
    for i in range(iter):
        for j in range(random.randint(1,10)):
            t = timeslots(days[random.randint(0,4)],times[random.randint(0,8)])
            if t not in ts_list:
                ts_list.append(t)
        
        availability1 = availability(ts_list)
        availability2=availability()
        availability2.fill_availability()
        p_list.append(Professor(generate_random_string(10),availability1))
        r_list.append(Room(generate_random_string(2)+str(random.randint(100,105)),random.randint(20,100),availability2))
        c_list.append(course_struct("code:"+generate_random_string(5),"cname:"+generate_random_string(10),p_list[i],r_list[i],ts_list[random.randint(0,len(ts_list)-1)],generate_random_string(10)))
    course_prof_ranked = {}
    for c in c_list:
        course_prof_ranked[c.course_code] = {1:[p_list[random.randint(0,len(p_list)//2)]],2:[p_list[random.randint(len(p_list)//2,len(p_list)-1)]]}
    observer = course_prof_abs(course_prof_ranked)
    csp_domain = csp_course_dom(c_list, observer, r_list)
    return c_list,p_list,r_list,csp_domain


class Constraint:#abstract class for the constraints, meant to be the parent class of all constraints
    def is_satisfied(self, assignment):
        raise NotImplementedError("This method should be implemented by subclasses.")

class BinarySameRoomConstraint(Constraint):#constraint that checks if two courses are in the same room, but not at the same time, in case we want different courses to be in the same room
    def __init__(self, course1):
        self.courses = course1
        self.type = "BinarySameRoomConstraint"
        
    def is_satisfied(self, c1,c2):
        return c1.room == c2.room and c1.time_slot != c2.time_slot

class NaryConstraint(Constraint):#abstract class for nary constraints, meant to be the parent class of all nary constraints, that is constraints that involve more than 2 courses
    def is_satisfied(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")

class BinaryTimeConstraint(NaryConstraint):#constraint that checks if two courses are at the same time, in case we want different courses to be at the same time
    def __init__(self,C1):
        self.courses=C1
        self.type = "BinaryTimeConstraint"
    def is_satisfied(self,c2):
        
        if not self.check(self.courses, c2):
            return False
        return True
    def check(self, value1, value2):
        return value1.time_slot == value2.time_slot

class ConstraintFactory:#factory class for the constraints, not used, tested, or implemented yet but potentially useful alongside the deserializer
    def __init__(self, professors, rooms, courses):
        self.professors = {prof["name"]: prof for prof in professors}
        self.rooms = {room["code"]: room for room in rooms}
        self.courses = {course["course_code"]: course for course in courses}

    def create_constraint(self, constraint_def):
        constraint_type = constraint_def["type"]
        variables = constraint_def.get("variables", [])
        parameters = constraint_def.get("parameters", {})

        if constraint_type == "NaryTimeConstraint":
            course1_code, course2_code = variables
            course1 = self.courses[course1_code]
            course2 = self.courses[course2_code]
            return BinaryTimeConstraint(course1, course2)

        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

class PreferredTimeConstraint(Constraint):#soft constraint that checks if a course has a preferred time, in case we want to give priority to certain courses
    def __init__(self, courses, expression):
        self.courses = courses
        self.expression = expression

    def get_valid_assignments(self):#valid assignments are the ones that have a preferred time, to be used in domain generation, not tested or implemented yet
        valid_assignments = []
        for i, course in enumerate(self.courses, start=1):
            preferred_time = self.expression.get(str(i))
            if preferred_time:
                day, time = preferred_time
                valid_assignment = {"course_code": course["course_code"], "timeslot": {"day": day, "time": time}}
                valid_assignments.append(valid_assignment)
        return valid_assignments

class PreferredProfConstraint(Constraint):#not tested or implemented yet, meant to be used in domain generation, same as previous class but for professors
    def __init__(self, courses, expression):
        self.courses = courses
        self.expression = expression

    def get_valid_assignments(self):
        valid_assignments = []
        for i, course in enumerate(self.courses, start=1):
            preferred_prof = self.expression.get(str(i))
            if preferred_prof:
                valid_assignment = {"course_code": course.course_code, "professor": preferred_prof}
                valid_assignments.append(valid_assignment)
        return valid_assignments


def scheduling_constraint(course_name1, course1, course_name2, course2):#current scheduling constraint, checks courses are not at the same time, and that they are not in the same room or have the same professor, and that the enrollment is not too high
    if (course1.time_slot== course2.time_slot and (course1.professor == course2.professor or course1.room == course2.room)) or course1.enrollment > course1.room.capacity+10 or course2.enrollment > course2.room.capacity+10: 
            return False
    for constraint in course1.constraints:#checks if the constraints in course 1 are satisfied
        if constraint.type=="BinaryTimeConstraint":
            if course1 in constraint.courses and course2 in constraint.courses:
                if not constraint.is_satisfied(course1,course2):
                    return False
        if constraint.type=="BinarySameRoomConstraint":
            if course1 in constraint.courses and course2 in constraint.courses:
                if not constraint.is_satisfied(course1,course2):
                    return False
    for constraint in course1.constraints:#checks if the constraints in course 2 are satisfied
        if constraint.type=="BinaryTimeConstraint":
            if course1 in constraint.courses and course2 in constraint.courses:
                if not constraint.is_satisfied(course1,course2):
                    return False
        if constraint.type=="BinarySameRoomConstraint":
            if course1 in constraint.courses and course2 in constraint.courses:
                if not constraint.is_satisfied(course1,course2):
                    return False
    
    return True

class deserializer:#class that deserializes the json file, and creates the professors, rooms, courses and constraints
    def __init__(self,json_path):
        self.json_path=json_path
        self.professors=[]
        self.rooms=[]
        self.courses=[]
        self.course_prof_ranked={}
        self.soft_constraints=[]
    def deserialize(self):
        with open(self.json_path, "r") as file:
            data = json.load(file)
        professors = data["professors"]
        rooms = data["rooms"]
        courses = data["courses"]
        soft_constraints = data["soft_constraints"]
        for i in professors:
            prof = Professor(i["name"])
            if i["availability"]=="full":
                prof.availability.fill_availability()
            else:
                for j in i["availability"]:
                    prof.add_slot(timeslots(j["day"],j["time"]))
            self.professors.append(prof)
        for i in rooms:
            room = Room(i["code"],i["capacity"])
            if i["availability"]=="full":
                room.availability.fill_availability()
            else:
                for j in i["availability"]:
                    room.add_slot(timeslots(j["day"],j["time"]))
            self.rooms.append(room)
        for i in courses:
            self.course_prof_ranked[i["course_code"]] = {1:[],2:[]}
            for prof in self.professors:
                if prof.name in i["ranked_professors"]["1"]:
                    self.course_prof_ranked[i["course_code"]][1].append(prof)
                if prof.name in i["ranked_professors"]["2"]:
                    self.course_prof_ranked[i["course_code"]][2].append(prof)
                    
            
            course = course_struct(i["course_code"],i["title"],self.course_prof_ranked[i["course_code"]][1][0],timeslots(i["timeslot"]["day"], i["timeslot"]["time"]),i["department"],i["enrollment"])
           
            self.courses.append(course)
        for i in courses:
            tempcons = i["constraints"]
            for j in tempcons:
                if j["type"]=="NaryTimeConstraint":
                    courses = [course for course in self.courses if course.course_code in j["variables"]]
                    course.constraints.append(BinaryTimeConstraint(courses))
                if j["type"]=="BinarySameRoomConstraint":
                    c1 = [course for course in self.courses if course.course_code in j["variables"]["courses"]]
                    con = BinarySameRoomConstraint(c1)
                    for c in c1:
                        c.constraints.append(con)
                   
        
        for i in soft_constraints:
            if i["type"]=="PreferredTimeConstraint":
                courses = [course for course in self.courses if course.course_code in i["variables"]]
                self.soft_constraints.append(PreferredTimeConstraint(courses,i["expression"]))
            if i["type"]=="PreferredProfConstraint":
                courses = [course for course in self.courses if course.course_code in i["variables"]]
                self.soft_constraints.append(PreferredProfConstraint(courses,i["expression"])) #not implemented yet in domain generation, should implement them more dynamically
        return self.professors,self.rooms,self.courses,self.course_prof_ranked
                   
                         

def main():

    slot1 = timeslots("MW", "8:00-9:15")
    slot2 = timeslots("TR", "9:30-10:45")

    availability1 = availability([slot1, slot2])
    print(availability1.timeslots[0])
    availability2 = availability()
    availability2.fill_availability()

    prof1 = Professor("Jessie Pinkman", availability1)
    prof2 = Professor("Walter White", availability2)

    room1 = Room("101", 50, availability2)
    room2 = Room("102", 40, availability2)

    prof1.add_slot(timeslots("MW", "11:00-12:15"))
    prof1.remove_slot(slot1)

    room1.add_slot(slot1)
    room1.remove_slot(slot1)
    
    course1 = course_struct("CS101", "Introduction to CS", prof1, room1, slot1, "Computer Science")
    course2 = course_struct("CS102", "Introduction to Programming", prof1, room1, slot1, "Computer Science")
    course3 = course_struct("CS103", "Introduction to Methanphetamine Production", prof1, room1, slot1, "Computer Science")

    prof_list1 = [Professor(f"prof{i}", availability2) for i in range(1, 100)]
    room_list1 = [Room(f"room{i}", 50, availability2) for i in range(1, 20)]
    course_list = [course_struct(f"cs{i}", f"course{i}", prof_list1[random.randint(0,98)], room_list1[random.randint(0,18)], slot1, "Computer Science") for i in range(1, 100) ]
    course_prof_ranked = {"CS101": {1:[prof1],2:[prof2]}, "CS102": {1:[prof2],2:[prof1]},"CS103": {1:[prof1],2:[prof2]}}
    observer = course_prof_abs(course_prof_ranked)

    course_list = [course1, course2, course3]
    room_list = [room1, room2]
    prof_list = [prof1, prof2]

    brute_dom= generate_brute_domains(course_list, prof_list, room_list)
    csp_domain = csp_course_dom(course_list, observer, room_list)
    domains = csp_domain.generate_domains()


   ############################################################################################################################################################################
   #old scheduling constraint, not used anymore
   
    # def scheduling_constraint(course_name1, course1, course_name2, course2):
    #     if course1.time_slot== course2.time_slot and (course1.professor == course2.professor or course1.room == course2.room):
    #         return False
    #     if(course1.course_code=="CS101" and course2.course_code=="CS102") or (course1.course_code=="CS102" and course2.course_code=="CS101"):
    #         if course1.time_slot== course2.time_slot:
    #             return False
        
    #     return True
    
    course_keys =[course.course_code for course in course_list]
    neighbours = {course.course_code: [course2.course_code for course2 in course_list if course2.course_code != course.course_code] for course in course_list}


############################################################################################################################################################################

    csp = CSP(course_keys,brute_dom, neighbours, scheduling_constraint)
    print(AC3(csp))

    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
    if solution:
            print("Solution found:")
            
            data = [[key] + [value.__dict__[k] for k in value.__dict__ if k != "constraints"] for key, value in solution.items()]
            
            headers = ["Course Code"] + [k for k in vars(next(iter(solution.values()))) if k != "constraints"]
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
############################################################################################################################################################################

    csp = CSP(course_keys,domains, neighbours, scheduling_constraint)
    s=AC3(csp)
    print(s)
    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
    if solution:
            print("Solution found:")
            
            data = [[key] + [value.__dict__[k] for k in value.__dict__ if k != "constraints"] for key, value in solution.items()]
            
            headers = ["Course Code"] + [k for k in vars(next(iter(solution.values()))) if k != "constraints"]
            
            print(tabulate(data, headers=headers, tablefmt="grid"))

############################################################################################################################################################################

    st = time.time()
    c_list,p_list,r_list,csp_domain = generate_random_domains(100)
    domains = csp_domain.generate_domains()
    course_keys =[course.course_code for course in c_list]
    neighbours = {course.course_code: [course2.course_code for course2 in c_list if course2.course_code != course.course_code] for course in c_list}
    csp = CSP(course_keys,domains, neighbours, scheduling_constraint)
    s=AC3(csp)
    print(s)
    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
    if solution:
            print("Solution found:")
            
            data = [[key] + [value.__dict__[k] for k in value.__dict__ if k != "constraints"] for key, value in solution.items()]
            
            headers = ["Course Code"] + [k for k in vars(next(iter(solution.values()))) if k != "constraints"]
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
    et = time.time()
    print(f"time taken: for latest solution{et-st}")


    ds =deserializer("data.json")
    profs, rooms , courses, course_prof_ranked = ds.deserialize()
    cpo = course_prof_abs(course_prof_ranked)
    ccd = csp_course_dom(courses,cpo,rooms)
    domains = ccd.generate_domains()
    neighbours = ccd.generate_neighbours()
    csp = CSP([course.course_code for course in courses],domains, neighbours, scheduling_constraint)
    s=AC3(csp)
    print(s)
    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)

    if solution:
            print("Solution found:")
            print(solution)
            
            data = [[key] + [value.__dict__[k] for k in value.__dict__ if k != "constraints"] for key, value in solution.items()]
            headers = ["Course Code"] + [k for k in vars(next(iter(solution.values()))) if k != "constraints"]
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
if __name__ == "__main__":
    main()
