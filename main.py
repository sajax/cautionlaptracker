import irsdk
import time

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_race_lap = 0
    caution_laps = 0
    race_lap_count = 0

    last_session_num = -1

# here we check if we are connected to iRacing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset all your in State variables
        state.last_race_lap = 0
        state.caution_laps = 0
        state.last_session_num = 0
        # we are shut down ir library (clear all internal variables)
        ir.shutdown()
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        # print('irsdk connected')

# our main loop, where we retrieve data
# and do something useful with it
def loop():
    # on each tick we freeze buffer with live telemetry
    # it is optional, useful if you use vars like CarIdxXXX
    # in this way you will have consistent data from this vars inside one tick
    # because sometimes while you retrieve one CarIdxXXX variable
    # another one in next line of code can be changed
    # to the next iracing internal tick_count
    ir.freeze_var_buffer_latest()

    # retrieve live telemetry data
    # check here for list of available variables
    # https://github.com/kutu/pyirsdk/blob/master/vars.txt
    # this is not full list, because some cars has additional
    # specific variables, like break bias, wings adjustment, etc
    # t = ir['SessionTime']
    # print('session time:', t)

    if ir['SessionInfo']:
        session_info = ir['SessionInfo']

    session_num = ir['SessionNum']
    current_session = session_info['Sessions'][session_num]

    session_changed = ir['SessionNum'] != state.last_session_num

    # Reset if SessionNum has changed
    if session_changed:
        state.caution_laps = 0
        state.last_race_lap = 0
        print('=== Session', str(ir['SessionNum'] + 1), current_session['SessionName'], '===')

    caution_active = True if ir['SessionFlags'] & irsdk.Flags.caution or ir['SessionFlags'] & irsdk.Flags.caution_waving else False

    if ir['RaceLaps'] > state.last_race_lap or session_changed:
        if caution_active:
            state.caution_laps += 1

        adjusted_lap_count = ir['RaceLaps'] - state.caution_laps
        race_finished = ir['SessionState'] == irsdk.SessionState.checkered or adjusted_lap_count > state.race_lap_count

        if not race_finished:
            lap_string = str(adjusted_lap_count) + " / " + str(state.race_lap_count)
            print('Lap', ir['RaceLaps'], 'Started | Caution:', 'Yes' if caution_active else 'No', '| Caution Laps:', state.caution_laps, '| Lap:', lap_string)
            # Write Lap to File
            file = open("lap.txt", 'w')
            file.write(lap_string)

        if race_finished:
            print('=== Race Finished ===')

    state.last_race_lap = ir['RaceLaps']
    state.last_session_num = ir['SessionNum']

if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()
    # Set Race Lap Count
    while state.race_lap_count < 1:
        try:
            state.race_lap_count = int(input("Enter Race Distance: "))
        except ValueError:
            print("Race lap count must be a number")
        if state.race_lap_count < 1:
            print("Race lap count must be greater than 0")

    print("Waiting for iRacing...")

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                loop()
            # sleep for 1 second
            # maximum you can use is 1/60
            # cause iracing update data with 60 fps
            time.sleep(1/5)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass
