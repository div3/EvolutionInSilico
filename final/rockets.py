import krpc
import time

def main():
    print("running...")
    #connect
    connection = krpc.connect()
    print("connected")

    #start a new voyage
    while True:
        print("========== New Voyage ===========")
        connection.space_center.quickload()
        vessel = connection.space_center.active_vessel

        #enable telemetry streaming
        altitude = connection.add_stream(getattr, vessel.flight(), 'mean_altitude')
        universal_time = connection.add_stream(getattr, connection.space_center, 'ut')
        telemetry_pitch = connection.add_stream(getattr, vessel.flight(), 'pitch')
        telemetry_heading = connection.add_stream(getattr, vessel.flight(), 'heading')
        telemetry_roll = connection.add_stream(getattr, vessel.flight(), 'roll')

        #set pre-flight conditions
        vessel.control.sas = False
        vessel.control.rcs = False
        vessel.control.throttle = 0.10
        launch_time = universal_time()
        last_altitude = altitude()
        warnings = 0
        
        #launch
        vessel.control.activate_next_stage()
        print("[" + str(universal_time()) + "]:\tLiftoff")
        
        in_flight = True
        while in_flight and \
              ((universal_time() - launch_time) < 10):
            time.sleep(0.1)

            #keep track of failure state
            current_altitude = altitude()
            if (current_altitude - last_altitude < 5):
                print("WARNING")
                warnings += 1
            else:
                warnings = max(0, warnings - 1)
            if (warnings > 10):
                print("FAILURE")
                in_flight = False
            last_altitude = current_altitude

            #gather telemetry
            inputs = [current_altitude,\
                      telemetry_pitch(),\
                      telemetry_heading(),\
                      telemetry_roll()]

            #pass into neural network
            actions = get_actions(inputs)

            #perform actions
            vessel.control.throttle = actions[0]
            vessel.control.pitch = actions[1]
            vessel.control.yaw = actions[2]
            vessel.control.roll = actions[3]

            print("alt.: " + str(altitude()))

        #remove telemetry streams
        altitude.remove()
        universal_time.remove()
        telemetry_pitch.remove()
        telemetry_heading.remove()
        telemetry_roll.remove()
        #end single voyage while loop
        
    #end infinite while loop

    ###end main###


#takes in a list of inputs
#returns a list of outputs
#[throttle(0, 1), pitch(-1, 1), yaw(-1, 1), roll(-1, 1)]
def get_actions(inputs):
    return [0, 0, 0, 0]
    ###end get actions###

########
main()

