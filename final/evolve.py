import neat
import copy
import pickle
import krpc
import time

def new_pop():
'''Creates a new Population p '''
    p = neat.Population(config)
    # Add statistics to pretty print progress
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    return p

'''Code to save, return and delete populations using pickle'''
def save_object(prefix, pop):
    pickle.dump(copy.deepcopy(p), open(prefix + '.pkl', 'wb'))
def return_population(prefix):
    loaded = pickle.load(open(prefix + '.pkl', 'rb'))
    return loaded
def delete_population(prefix):
    try:
        os.remove(prefix + '.pkl')
    except FileNotFoundError:
        print('Not found')

'''Creates a new ship using the global connection established in main'''
def create_new_ship():
    global connection
    print("========== New Voyage ===========")
    connection.space_center.quickload()
    vessel = connection.space_center.active_vessel
    # Pre-flight
    vessel.control.sas = False
    vessel.control.rcs = False
    vessel.control.throttle = 0.10
    return vessel

'''Fitness function to optimize flight for sub-70k meters.'''
def fitness_func_sub70(nets, config):
    # For each genome in 'nets' create a Neural Network
    global connection
    for genome_id, genome in nets:
        # times += 1

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        vessel = create_new_ship() # Create a new ship
        
        # Set up connections for variables
        altitude = connection.add_stream(getattr, vessel.flight(), 'mean_altitude')
        universal_time = connection.add_stream(getattr, connection.space_center, 'ut')
        telemetry_pitch = connection.add_stream(getattr, vessel.flight(), 'pitch')
        telemetry_heading = connection.add_stream(getattr, vessel.flight(), 'heading')
        telemetry_roll = connection.add_stream(getattr, vessel.flight(), 'roll')
        srf = vessel.orbit.body.reference_frame
        telemetry_speed = connection.add_stream(getattr, vessel.flight(srf), 'speed')
        apoapsis = connection.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
        periapsis = connection.add_stream(getattr, vessel.orbit, "periapsis_altitude")
        
        # Set up variables
        launch_time = universal_time()
        starting_fuel = vessel.resources.amount('LiquidFuel')
        last_altitude = altitude()
        max_altitude = 0
        warnings = 0
        vessel.control.activate_next_stage()
        starting_energy = (connection.space_center.g * vessel.mass *\
                connection.space_center.bodies["Kerbin"].mass) /\
                vessel.orbit.radius
        
        print("[" + str(universal_time()) + "]:\tLiftoff")

        reached_basic = False
        in_flight = True
        while in_flight and ((universal_time() - launch_time) < 200):
            # Error Check for crash
            current_altitude = altitude()

            warning_rate = current_altitude - last_altitude
            #print(warning_rate)
            if (warning_rate < 1):
                # print("WARNING")
                warnings += max(1, abs(warning_rate))
            else:
                warnings = max(0, warnings - warning_rate)
            if (warnings > 60):
                # print("FAILURE")
                in_flight = False
            
            inputs = [current_altitude,\
                      telemetry_speed(),\
                      telemetry_pitch(),\
                      telemetry_heading(),\
                      telemetry_roll()]
            
            actions = net.activate(inputs) # Activate using inputs
            #perform actions
            vessel.control.throttle = ((actions[0] / 60.0) + 0.5)
            vessel.control.pitch = (actions[1] / 30.0)
            vessel.control.yaw = (actions[2] / 30.0)
            vessel.control.roll = (actions[3] / 30.0)

            max_altitude = max(current_altitude, max_altitude)
            last_altitude = current_altitude

            time.sleep(0.10)
            # Break if altitude is greater than 70k
            if (current_altitude > 70000):
                in_flight = False
                reached_basic = True
                break
        # Use fuel used to measure fitness
        fuel_used = starting_fuel - vessel.resources.amount('LiquidFuel')
        fitness = max_altitude / (2 ** (fuel_used / starting_fuel))
            
        #remove telemetry streams
        altitude.remove()
        universal_time.remove()
        telemetry_pitch.remove()
        telemetry_heading.remove()
        telemetry_roll.remove()
        telemetry_speed.remove()
        apoapsis.remove()
        periapsis.remove()
        print(genome_id, fitness)
        genome.fitness = fitness

'''Fitness functions for greater than 70k flight'''
def fitness_func_adv(nets, config):
    # global times
    # For each genome in 'nets' create a Neural Network
    global connection
    for genome_id, genome in nets:
        # times += 1

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        vessel = create_new_ship() # Create a new ship
        
        # Set up connections
        altitude = connection.add_stream(getattr, vessel.flight(), 'mean_altitude')
        universal_time = connection.add_stream(getattr, connection.space_center, 'ut')
        telemetry_pitch = connection.add_stream(getattr, vessel.flight(), 'pitch')
        telemetry_heading = connection.add_stream(getattr, vessel.flight(), 'heading')
        telemetry_roll = connection.add_stream(getattr, vessel.flight(), 'roll')
        srf = vessel.orbit.body.reference_frame
        telemetry_speed = connection.add_stream(getattr, vessel.flight(srf), 'speed')
        apoapsis = connection.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
        periapsis = connection.add_stream(getattr, vessel.orbit, "periapsis_altitude")
        
        launch_time = universal_time()
        starting_fuel = vessel.resources.amount('LiquidFuel')
        last_altitude = altitude()
        max_altitude = 0
        warnings = 0
        vessel.control.activate_next_stage()
        starting_energy = (connection.space_center.g * vessel.mass *\
                connection.space_center.bodies["Kerbin"].mass) /\
                vessel.orbit.radius
        
        print("[" + str(universal_time()) + "]:\tLiftoff")

        reached_basic = False
        in_flight = True
        while in_flight and ((universal_time() - launch_time) < 200):
            # Error Check for crash
            current_altitude = altitude()
            
            if (current_altitude - last_altitude < 1):
                #print("WARNING")
                warnings += 1
            else:
                warnings = max(0, warnings - 1)
            if (warnings > 20):
                #print("FAILURE")
                in_flight = False
            
            inputs = [current_altitude,\
                      telemetry_speed(),\
                      telemetry_pitch(),\
                      telemetry_heading(),\
                      telemetry_roll()]
            
            actions = net.activate(inputs) # Activate using inputs
            #perform actions
            vessel.control.throttle = actions[0]
            vessel.control.pitch = actions[1]
            vessel.control.yaw = actions[2]
            vessel.control.roll = actions[3]

            max_altitude = max(current_altitude, max_altitude)
            last_altitude = current_altitude

            time.sleep(0.10)

            if (apoapsis() > 70000 and periapsis() > 70000):
                orbit_energy = 0.5 * vessel.mass * (vessel.orbit.speed ** 2) +\
                (connection.space_center.g * vessel.mass *\
                connection.space_center.bodies["Kerbin"].mass) /\
                vessel.orbit.radius
                orbit_energy = orbit_energy
                reached_basic = True
                break

        # Use the orbit energy to measure fitness
        fuel_used = starting_fuel - vessel.resources.amount('LiquidFuel')
        fitness = max_altitude
        if reached_basic:
            fitness = ((orbit_energy - starting_energy) / (10 ** 3)) + max_altitude
        fitness = fitness / (1 + (3 * vessel.orbit.eccentricity))
            
        #remove telemetry streams
        altitude.remove()
        universal_time.remove()
        telemetry_pitch.remove()
        telemetry_heading.remove()
        telemetry_roll.remove()
        telemetry_speed.remove()
        apoapsis.remove()
        periapsis.remove()
        print(genome_id, fitness)
        genome.fitness = fitness

'''Visualize a particular net'''
def visualize_vessel(net):
# Set up connections
    global connection
    vessel = create_new_ship()
    altitude = connection.add_stream(getattr, vessel.flight(), 'mean_altitude')
    universal_time = connection.add_stream(getattr, connection.space_center, 'ut')
    telemetry_pitch = connection.add_stream(getattr, vessel.flight(), 'pitch')
    telemetry_heading = connection.add_stream(getattr, vessel.flight(), 'heading')
    telemetry_roll = connection.add_stream(getattr, vessel.flight(), 'roll')
    
    launch_time = universal_time()
    last_altitude = altitude()
    max_altiude = 0
    warnings = 0
    vessel.control.activate_next_stage()
    print("[" + str(universal_time()) + "]:\tLiftoff")

    reached_basic = False
    in_flight = True
    while in_flight and ((universal_time() - launch_time) < 200):
        # Error Check for crash
        current_altitude = altitude()

        if (current_altitude - last_altitude < 2):
            print("WARNING")
            warnings += 1
        else:
            warnings = max(0, warnings - 1)
        if (warnings > 20):
            print("FAILURE")
            in_flight = False
        
        inputs = [current_altitude, telemetry_pitch(), telemetry_heading(), telemetry_roll()]
        actions = net.activate(inputs) # Activate using inputs
        #perform actions
        vessel.control.throttle = actions[0]
        vessel.control.pitch = actions[1]
        vessel.control.yaw = actions[2]
        vessel.control.roll = actions[3]

        max_altiude = max(current_altitude, max_altiude)
        last_altitude = current_altitude

        time.sleep(0.10)

        if current_altitude >= 70000:
            break

    altitude.remove()
    universal_time.remove()
    telemetry_pitch.remove()
    telemetry_heading.remove()
    telemetry_roll.remove()

'''Global Config variable'''
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                     'config.txt')

if __name__ == '__main__':
    print("running...")
    # connect
    connection = krpc.connect()
    print("connected")
    p = new_pop()
    
    # Run the fitness function and save the population every 5 turns
    for i in range(15):
        winner = p.run(fitness_func_sub70, 5) # Run
        save_object(("a" + str(i) + "0"), p) # prefix as first argument
        winner_net = neat.nn.FeedForwardNetwork.create(winner, config) # Gets the fittest from the population
        save_object(("a" + str(i) + "0_best"), winner_net) # This saves the winner as "X0 - best" where X is current loop iter

    # # To load and visualize a vessel - uncomment below and comment out above
    # loaded_net = return_population("NAME") # Replace NAME with object name
    # visualize_vessel(loaded_net)
