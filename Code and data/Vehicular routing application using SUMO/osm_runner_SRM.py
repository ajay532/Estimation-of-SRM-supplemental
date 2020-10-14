#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
import subprocess
import random
random.seed(1234)
import numpy
import math
from scipy.stats import norm

# global Variables
total_routes = 5
total_vehicles = 2000
next_generated_vehicle_step = 0  # step at which next vehicle will generated
global_step = 0  # next step going to occur on simulation
global_data = {}
global_a = 0.0  # for calculaing CVaR
global_m = 100  # Subdivisions of trapezoidal integral
# intializing iid_delay 2d array
iid_delay = []
for i in range(1, total_routes + 2):  # loop will run (1 to 6) only, array form [[0][1][2][3][4][5]]
    iid_delay.append([])

# opening files to write global_data
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("data.xml", "w"))
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("route1_data.xml", "w"))
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("route2_data.xml", "w"))
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("route3_data.xml", "w"))
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("route4_data.xml", "w"))
print('veh_id \t departure_time \t arrival_time \t duration \n', file=open("route5_data.xml", "w"))

# we need to import python modules from the $SUMO_HOME/tools directory.
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci


# VaR at level a.
def VaR(a, route_no):  # iid_delay are duration of vehicles
        global iid_delay
        delays = iid_delay[route_no]
        delays.sort()
        if a == 0:
            return delays[0]
        return delays[int(math.ceil(len(delays) * a)) - 1]

# user risk aversion function
def phi(p):
	K = 5.0 # constant for user
	# phi =  K e^(-K(1-b))/(1-e^(-K))
	value = K * numpy.exp(-K*(1-p))/float(1 - numpy.exp(-K))
	return value

# CVaR at level a by acerbi's formula and using trapezoidal rule with m subdivisions.
# we will tweak it with phi to use it as SRM
def CVaR(route_no):
    global global_a
    global iid_delay
    global global_m  # subdivision number for trapezoidal rule.
    '''
    delays = iid_delay[route_no]
    delays.sort()
    print('route_no = %i' % (route_no))
    print(delays)
    '''
    if global_a == 1:
        print ("Error: CVaR can not be calculate at level 1, since 1/(1-a) become undefined")
        return -1
    CVaR_a = 0.0
    h = float((1-global_a)/global_m)  # width of single subdivision.
    for k in range(1, global_m+1):
        CVaR_a = CVaR_a + phi(global_a + ((k - 1) * h)) * VaR(global_a + ((k - 1) * h), route_no) + phi(global_a + (k* h)) * VaR(global_a + (k * h), route_no)
    CVaR_a = (CVaR_a * float(h)) / float(2 * (1 - global_a))
    return CVaR_a


# simulation step and storage of data
def simulation_step():
    global global_data
    global global_step
    global next_generated_vehicle_step
    traci.simulationStep()  # On this line only simulation happen and previous all work done on this step.
    departed_list = traci.simulation.getDepartedIDList()  # Vehicle Id that are departed at this step.
    arrived_list = traci.simulation.getArrivedIDList()  # Vehicle Id that are arrived at this step.
    # print('step = %i  "%s" \n' % (step, arrived_list), file=open("arrived_list.xml", "a"))
    # print('step = %i  "%s" \n' % (step, departed_list), file=open("departed_list.xml", "a"))
    for item in departed_list:
        global_data[item] = [global_step, 0, 0]
    for item in arrived_list:
        global_data[item][1] = global_step
        global_data[item][2] = global_data[item][1] - global_data[item][0]
        # store data
        print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("data.xml", "a"))
        # storing iid_delay and data for specific route
        route_name = item.split('_')
        if route_name[0] == "route1":
            print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("route1_data.xml", "a"))
            iid_delay[1].append(global_data[item][2])
        if route_name[0] == "route2":
            print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("route2_data.xml", "a"))
            iid_delay[2].append(global_data[item][2])
        if route_name[0] == "route3":
            print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("route3_data.xml", "a"))
            iid_delay[3].append(global_data[item][2])
        if route_name[0] == "route4":
            print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("route4_data.xml", "a"))
            iid_delay[4].append(global_data[item][2])
        if route_name[0] == "route5":
            print('%s \t %s \t %s \t %s \n' % (item, global_data[item][0], global_data[item][1], global_data[item][2]), file=open("route5_data.xml", "a"))
            iid_delay[5].append(global_data[item][2])
    global_step += 1

    return


# generate vehicle for a route
def generate_vehicle(route_no, veh_no):  # route no [1 to 5] veh_no [1 to ..]
    global global_data
    global global_step
    global next_generated_vehicle_step
    route_name = "route" + `route_no`
    veh_id = route_name + "_" + `veh_no`  # Vehicle Id for a specific route.
    if next_generated_vehicle_step < global_step:
        next_generated_vehicle_step = global_step
    depart_time = str(next_generated_vehicle_step)  # departure time of a vehicle based on which step it is added in the simulation.
    traci.vehicle.addFull(veh_id, route_name, typeID="passenger", depart=depart_time,
                departLane="first", departPos="7.60", departSpeed="0.00",
                 arrivalLane="current", arrivalPos="93.0", arrivalSpeed="current",
                fromTaz="", toTaz="", line="", personCapacity=0, personNumber=0)  # Adding a vehicle.
    next_generated_vehicle_step += 20
    return


# Successive reject algorithm
def Successive_reject(total_routes, total_vehicles):
    # Initialization
    global global_data
    global global_step
    global next_generated_vehicle_step
    global iid_delay
    N = total_vehicles
    K = total_routes
    n_k = [0 for i in range(1, K+2)]  # 1 to K array with 0, IMP: no vehicle yet generated, vehicle no start with 1
    A = {i for i in range(1, K+1)}  # set 1 to K arms
    cvar_matrix = [[0 for j in range(1, K+2)] for i in range(1, K+2)]
    # log_k_bar calculation
    log_k_bar = 0.5
    for i in range(2, K+1):
        log_k_bar = log_k_bar + 1/float(i)
    # Each phase count {1 to K-1}
    n = [0 for xi in range(0, K)]

    for k in range(1, K):  # K-1 phases

        # Part A for calculating CVaR
        n[k] = int(math.ceil((1/log_k_bar) * ((N - K)/(K + 1 - k))))
        if k == 1:  # If it is first phase n[1]
            for j in range(1, n[k]+1):
                for i in A:  # for each left route
                    n_k[i] = n_k[i] + 1  # counting no of vehicle generated yet
                    # generate_vehicle_for_route_i
                    generate_vehicle(i, n_k[i])  # genrate vehicle on route i with vehicle no as n_k[i]
            while(1):   # code to detect all vhicles for this stage has arrived or not.
                simulation_step()
                state = 1
                for i in A:
                    if len(iid_delay[i]) != n_k[i]:
                        state *= 0
                if state == 1:
                    break
        else:
            for j in range(1, n[k] - n[k-1] + 1):
                for i in A:  # for each left route
                    n_k[i] = n_k[i] + 1  # counting no of vehicle generated yet
                    # generate_vehicle_for_route_i
                    generate_vehicle(i, n_k[i])  # genrate vehicle on route i with vehicle no as n_k[i]
            while(1):   # code to detect all vhicles for this stage has arrived or not.
                simulation_step()
                state = 1
                for i in A:
                    if len(iid_delay[i]) != n_k[i]:
                        state *= 0
                if state == 1:
                    break
        # Part B eliminating route
        # calculate CVaR
        
        max_cvar = [0, 0]  # first denote value second denote index.
        for i in A:
            cvar = CVaR(i)
            cvar_matrix[k][i] = cvar
            if cvar > max_cvar[0]:
                max_cvar[0] = cvar
                max_cvar[1] = i
        A.discard(max_cvar[1])
    while traci.simulation.getMinExpectedNumber() > 0:
        simulation_step()
    cvar_matrix[K][max_cvar[1]] = max_cvar[0]
    for k in range(1, K):
        print (cvar_matrix[k][1:K+1])
	'''
    # printing mean of routes
    
    print("mean of routes are")
    xyz = iid_delay
    del xyz[0]
    xyz = numpy.array(xyz)
    print(xyz.mean(1))
    '''
    return


# Options for command line arguments.
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# This is the main entry point of this script.
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    # For full output append this command below, , "--full-output", "fulloutput.xml".
    traci.start([sumoBinary, "-c", "osm.sumocfg", "--tripinfo-output", "tripinfo.xml"])
    global total_routes
    global total_vehicles
    Successive_reject(total_routes, total_vehicles)
    traci.close()
    sys.stdout.flush()
    # Officially simulation is over.
