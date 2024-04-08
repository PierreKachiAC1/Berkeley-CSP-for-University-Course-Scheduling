from csp import *
import tabulate
from search import *


class timeslot:
    
    
    def __init__(self, day, time):
        days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']
        if day not in days:
            raise ValueError(f'Invalid day: {day}')
        if time not in ['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']:
            raise ValueError(f'Invalid time: {time}')
        
        self.day = day
        self.time = time
    def __str__(self):
        return f'{self.day} {self.time}'

class availability:
    def __init__(self, timeslot_list=None):
        if timeslot_list is None:
            timeslot_list = []
        self.timeslots = set(timeslot_list)
        
    def fill_availability(self):
        days = ['MW', 'TR', 'MWF', 'TTH', 'MTWTHF']
        times = ['8:00-9:15', '9:30-10:45', '11:00-12:15', '12:30-1:45', '2:00-3:15', '3:30-4:45', '5:00-6:15', '6:30-7:45', '8:00-9:15']
        for day in days:
            for time in times:
                self.timeslots.add(timeslot(day, time))
    
    def remove_slot(self, timeslot):
        self.timeslots.remove(timeslot)
    

    def add_slot(self, timeslot):
        self.timeslots.add(timeslot)
    def __str__(self):
        return f'{self.timeslots}'

class Room:
    def __init__(self, code, capacity, availability=None):
        self.room_code = code
        self.capacity = capacity
        if availability is None:
            availability = availability()  
        self.availability = availability

    def add_slot(self, timeslot):
        self.availability.add_slot(timeslot)

    def remove_slot(self, timeslot):
        self.availability.remove_slot(timeslot)
    def __str__(self):
        return self.room_code
    
class Professor:
    def __init__(self, name, availability=None):
        self.name = name
        if availability is None:
            availability = availability()  
        self.availability = availability

    def add_slot(self, timeslot):
        self.availability.add_slot(timeslot)

    def remove_slot(self, timeslot):
        self.availability.remove_slot(timeslot)
    
    def __str__(self):
        return self.name

class course_struct:
    def __init__(self, course_code, title, professor, room, time_slot, dep):
        self.course_code = course_code
        self.title = title
        self.professor = professor  
        self.room = room  
        self.time_slot = time_slot
        self.pre_req = []
        # self.qualified_ranked_instructors = qualified_ranked_instructors
        self.dep=dep
    
    
    def __str__(self):
        return f'{self.course_code} - {self.title} - {self.professor} - {self.room} - {self.time_slot}'
    
# class course:
#     def __init__(self, course_code, title, available_rooms,available_ranked_professors=None):
#         if available_ranked_professors is None:
#             available_ranked_professors = {}
#         self.course_code = course_code
#         self.title = title
#         self.available_ranked_profs = available_ranked_professors  
#         self.room = available_rooms  
#         self.students = []
#         self.enrolled = 0
#         self.available_timeslots = []

#     def add_student(self, student):
#         self.students.append(student)
#         self.enrolled += 1

#     def remove_student(self, student):
#         self.students.remove(student)
#         self.enrolled -= 1

#     def __str__(self):
#         return f'{self.course_code} - {self.title} -'

class csp_course_dom:
    def __init__(self, course_list, course_prof_ranked, room_list):
        self.course_list = course_list
        self.course_prof_observer = course_prof_ranked
        self.room_list = room_list

    def generate_domains(self):
            domains = {}
            for course in self.course_list:
                course_domain = []
                for prof in (self.course_prof_observer.course_prof_ranked[course.course_code][1] +self.course_prof_observer.course_prof_ranked[course.course_code][2]):
                    for slot in prof.availability.timeslots:
                        for room in self.room_list:
                            course_domain.append(course_struct(course.course_code, course.title, prof, room, slot, course.dep))
                domains[course.course_code] = course_domain
            return domains
    

class course_prof_observer:
    def __init__(self, course_prof_ranked):
        self.course_prof_ranked = course_prof_ranked

    def add_prof(self, course_code,rank, prof):
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
          
def generate_brute_domains(course_list, prof_list, room_list):
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
#problem for later is that what if a course is a prerequisite for another one, then they can be on the same timeslot and no need to check for that
def main():

    slot1 = timeslot("MW", "8:00-9:15")
    slot2 = timeslot("TR", "9:30-10:45")

    availability1 = availability([slot1, slot2])
    availability2 = availability()
    availability2.fill_availability()

    prof1 = Professor("Jessie Pinkman", availability1)
    prof2 = Professor("Walter White", availability2)

    room1 = Room("101", 50, availability2)
    room2 = Room("102", 40, availability2)

    prof1.add_slot(timeslot("MW", "11:00-12:15"))
    prof1.remove_slot(slot1)

    room1.add_slot(slot1)
    room1.remove_slot(slot1)
    
    course1 = course_struct("CS101", "Introduction to CS", prof1, room1, slot1, "Computer Science")
    course2 = course_struct("CS102", "Introduction to Programming", prof1, room1, slot1, "Computer Science")
    course3 = course_struct("CS103", "Introduction to Methanphetamine Production", prof1, room1, slot1, "Computer Science")

    prof_list1 = [Professor(f"prof{i}", availability2) for i in range(1, 100)]
    room_list1 = [Room(f"room{i}", 50, availability2) for i in range(1, 20)]
    course_list = [course_struct(f"cs{i}", f"course{i}", prof_list1[random.randint(0,98)], room_list1[random.randint(0,18)], slot1, "Computer Science") for i in range(1, 100) ]
    
    
    
    #things to do: 1 make tabulation better for now to make it more clear eg: course, prof, timeslot as columns something like that
    #try to add randomness to generate the courses to test the code, 
    #work on a way of embedding data in a way that I can generate and retrieve automatically it while keeping the code working
    #^^maybe csv maybe json whatever, so that we can later on make it work with the LLM
    #if I have time, try and also work on extra constraints, just to make sure we can and add it to the code, already mentioned 
    #^^ prerequisites constraints to keep in mind and work on any other constraints I can come up with to add
    #also try and think of a way to translate english into constraints

    #top priority make a github and add mr laurent and father tony

    #always when trying to solve any problem keep in mind that 20% of my time should be spent looking for already written solutions
    #this could save lives and always might save time, so always look for solutions before trying to write your own

    course_prof_ranked = {"CS101": {1:[prof1],2:[prof2]}, "CS102": {1:[prof2],2:[prof1]},"CS103": {1:[prof1],2:[prof2]}}
    observer = course_prof_observer(course_prof_ranked)
    # print(prof1 in course_prof_ranked["CS101"][1])

    course_list = [course1, course2, course3]
    room_list = [room1, room2]
    prof_list = [prof1, prof2]

    brute_dom= generate_brute_domains(course_list, prof_list, room_list)
    csp_domain = csp_course_dom(course_list, observer, room_list)
    domains = csp_domain.generate_domains()
    
    # for course_code, course_domain in domains.items():
    #     print(f"Domains for {course_code}:")
    #     for domain in course_domain:
    #         print(domain)
   
   
    def scheduling_constraint(course_name1, course1, course_name2, course2):
        if course1.time_slot== course2.time_slot and (course1.professor == course2.professor or course1.room == course2.room):
            return False
        # course1.professor.availability.remove_slot(course1.time_slot)
        # course1.room.availability.remove_slot(course1.time_slot)
        return True
    
    #make sure the code is capable of generating a solution, but if there are no solutions, it should not crash and tell me that there are none
    course_keys =[course.course_code for course in course_list]
    neighbours = {course.course_code: [course2.course_code for course2 in course_list if course2.course_code != course.course_code] for course in course_list}



    csp = CSP(course_keys,brute_dom, neighbours, scheduling_constraint)
    print(AC3(csp))

    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
    if solution:
        print("Solution found:")
        print(tabulate.tabulate(solution.items()))
    else:
        print("No solution found.")

    csp = CSP(course_keys,domains, neighbours, scheduling_constraint)
    s=AC3(csp)
    print(s)
    solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
    if solution:
        print("Solution found:")
        print(tabulate.tabulate(solution.items()))
    else:
        print("No solution found.")
        


if __name__ == "__main__":
    main()
