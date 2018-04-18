import neat
import copy
import pickle
import krpc
import time

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

def fitness_func(nets, config):
    # global times
    # For each genome in 'nets' create a Neural Network
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

            time.sleep(0.10)

            if current_altitude >= 70000:
                break
        fitness = max_altiude
        # if reached_basic:
        #     fitness = get_altitude + delta_v(vessel)
        #remove telemetry streams
        altitude.remove()
        universal_time.remove()
        telemetry_pitch.remove()
        telemetry_heading.remove()
        telemetry_roll.remove()

        genome.fitness = fitness

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                     'neat_config')

# times = 0

print("running...")
#connect
connection = krpc.connect()
print("connected")

# Creates a new population p
p = neat.Population(config)
# Add statistics to pretty print progress
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

winner = p.run(fitness_func, 5) # Run 

winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

def save_population(prefix, pop):
    pickle.dump(copy.deepcopy(p), open(prefix + '.pkl', 'wb'))
def return_population(prefix):
    loaded = pickle.load(open(prefix + '.pkl', 'rb'))
    return loaded
def delete_population(prefix):
    try:
        os.remove(prefix + '.pkl')
    except FileNotFoundError:
        print('Not found')

