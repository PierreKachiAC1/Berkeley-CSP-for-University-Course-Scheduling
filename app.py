from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from omega_class import *
app = Flask(__name__)

request_history_dir = 'requestHistory'

os.makedirs(request_history_dir, exist_ok=True)

@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(request_history_dir, f"request_{timestamp}.json")

        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        #dont forget to send both the presentation and the code

        #priority: comment the code, send the code and presentation by email to father rouhayem, and finally clean up the useless files
        ds =deserializer(filename)
        profs, rooms , courses, course_prof_ranked = ds.deserialize()
        cpo = course_prof_abs(course_prof_ranked)
        ccd = csp_course_dom(courses,cpo,rooms)
        domains = ccd.generate_domains()
        neighbours = ccd.generate_neighbours()
        csp = CSP([course.course_code for course in courses],domains, neighbours, scheduling_constraint)
        s=AC3(csp)
        print(s)
        solution = backtracking_search(csp, select_unassigned_variable=mrv, order_domain_values=lcv)
        if solution is None:
            return jsonify({"error": "No solution found"}), 400
        else:
            tempdict = {}
            for key in solution.keys():
                tempdict[key] = {"course_title":solution[key].title, "professor":str(solution[key].professor), "room":str(solution[key].room), "time":str(solution[key].time_slot)}
                #fix api output to be parsable
            return jsonify(tempdict), 200
               
                #comment about python in the presentation, since we plan on using this with llms and most machine learning is written in python we picked this json, even though a statically typed language would be easier
                #words to use: do not use ideal, use programming jargon in general, near optimal*, its an np complete problem, solution in this case, a complete algorithm is one that always finds a
                #extra importance on terminology
                #try as close to 15 as possible, max 17
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
