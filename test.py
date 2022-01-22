import subprocess


def validate(file, expected):
    write_file(file)
    actual = execute(1)
    expected = parse_output(expected)
    if actual != expected:
        print(actual)
        print(expected)
        assert False

def write_file(data):
    with open('testfile.lp', 'w') as f:
        f.write(data)

def parse_output(data, delimiter='\n'):
    data = data.split(delimiter)
    #print(data)
    result = data[-1].strip()
    answers = data[:-1]
    models = [sorted(answers[i+1].strip().split(' ')) for i in range(0, len(answers), 2)]
    #print(models)
    return {'satisfiable': result == 'SATISFIABLE', 'models': sorted(models)}

def execute(maxstep, num_answers=0):
    proc = subprocess.Popen(['clingo', 'scenario1.lp', 'rules.lp', 'testfile.lp', str(num_answers), '-c', f'maxstep={maxstep}'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr  = proc.communicate(timeout=1)
    stdout = stdout.decode()
    #print(proc.returncode, stdout, stderr)
    if stderr:
        print(stderr)
    #stdout = stdout.split('\r\n')
    start = 'Solving...'
    i = stdout.index(start) + len('Solving...') + 2
    j = stdout.index('\r\n\r\nModels       :')
    return parse_output(stdout[i:j], delimiter='\r\n')

def test_robots_cannot_move_through_each_other():
    scenario = '''init(object(robot,1),value(at,pair(4,3))).
                init(object(robot,2),value(at,pair(4,4))).
                move(1,0,1,1).
                move(2,0,-1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_object_cannot_move_outside_bounds_of_warehouse():
    scenario = 'init(object(robot,1),value(at,pair(5,5))).'
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_two_shelves_cannot_be_in_same_cell():
    scenario = '''init(object(shelf,1),value(at,pair(2,4))).
                init(object(shelf,2),value(at,pair(2,4))).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_two_robots_cannot_be_in_same_cell():
    scenario = '''init(object(robot,1),value(at,pair(2,4))).
                init(object(robot,2),value(at,pair(2,4))).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_robot_cannot_be_in_different_cells():
    scenario = '''init(object(robot,1),value(at,pair(2,4))).
                init(object(robot,1),value(at,pair(1,1))).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_exogenous_movement():
    scenario = '''init(object(robot,1),value(at,pair(2,2))).
                #show move/4.'''
    expected = '''Answer: 1

                Answer: 2
                move(1,0,-1,1)
                Answer: 3
                move(1,0,1,1)
                Answer: 4
                move(1,1,0,1)
                Answer: 5
                move(1,-1,0,1)
                SATISFIABLE'''
    validate(scenario, expected)

def test_robot_movement():
    scenario = '''init(object(robot,1),value(at,pair(4,3))).
                move(1,-1,0,1).
                :- robot(1,3,3,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_one_action_per_time_step():
    scenario = '''init(object(robot,1),value(at,pair(2,2))).
                init(object(shelf,1),value(at,pair(2,2))).
                move(1,-1,0,1).
                pickup(1,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_location_of_carried_shelf():
    scenario = '''init(object(robot,1),value(at,pair(2,2))).
                init(object(shelf,1),value(at,pair(1,1))).
                carries(1,1,t,0).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_carried_shelf_moves_with_robot():
    scenario = '''init(object(robot,1),value(at,pair(2,2))).
                init(object(shelf,1),value(at,pair(2,2))).
                carries(1,1,t,1).
                :- putdown(R,S,T).
                #show shelf/4.
                #show robot/4.'''
    expected = '''Answer: 1
                robot(1,2,2,1) robot(1,2,2,0) shelf(1,2,2,1) shelf(1,2,2,0)
                Answer: 2
                robot(1,2,2,1) robot(1,2,2,0) shelf(1,2,2,1) shelf(1,2,2,0)
                Answer: 3
                robot(1,2,2,0) robot(1,2,1,1) shelf(1,2,1,1) shelf(1,2,2,0)
                Answer: 4
                robot(1,2,2,0) robot(1,3,2,1) shelf(1,3,2,1) shelf(1,2,2,0)
                Answer: 5
                robot(1,2,2,0) robot(1,2,3,1) shelf(1,2,3,1) shelf(1,2,2,0)
                Answer: 6
                robot(1,2,2,0) robot(1,1,2,1) shelf(1,1,2,1) shelf(1,2,2,0)
                SATISFIABLE'''
    validate(scenario, expected)

def test_carries_false_common_sense_of_inertia():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                :- carries(1,1,f,1).
                :- pickup(R,S,T).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_carries_true_common_sense_of_inertia():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                carries(1,1,t,0).
                :- carries(1,1,t,1).
                :- putdown(R,S,T).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_pickup_if_already_carrying():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                pickup(1,1,1).
                carries(1,1,t,0).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_pickup_if_not_in_same_location():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(1,1))).
                pickup(1,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_putdown_if_not_already_carrying():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                putdown(1,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_putdown_on_highway():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                init(object(highway,1),value(at,pair(2,2))).
                carries(1,1,t,0).
                putdown(1,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_putdown_on_pickingStation():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                init(object(pickingStation,1),value(at,pair(2,2))).
                carries(1,1,t,0).
                putdown(1,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_deliver_if_not_carrying():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                init(object(product,1),value(on,pair(1,10))).
                init(object(pickingStation,1),value(at,pair(2,2))).
                init(object(order,1),value(line,pair(1,10))).
                init(object(order,1),value(pickingStation,1)).
                deliver(1,1,1,1,10,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_cannot_deliver_more_than_available():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                init(object(product,1),value(on,pair(1,10))).
                init(object(pickingStation,1),value(at,pair(2,2))).
                init(object(order,1),value(line,pair(1,10))).
                init(object(order,1),value(pickingStation,1)).
                carries(1,1,t,0).
                deliver(1,1,1,1,11,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

def test_must_deliver_at_picking_station():
    scenario = '''init(object(shelf,1),value(at,pair(2,2))).
                init(object(robot,1),value(at,pair(2,2))).
                init(object(product,1),value(on,pair(1,10))).
                init(object(pickingStation,1),value(at,pair(1,2))).
                init(object(order,1),value(line,pair(1,10))).
                init(object(order,1),value(pickingStation,1)).
                carries(1,1,t,0).
                deliver(1,1,1,1,10,1,1).'''
    expected = 'UNSATISFIABLE'
    validate(scenario, expected)

#2 robots should be able to do 2 actions at same time
#todo test all exogenous movement, should output 2 cases each
#   where their effect is triggered and not triggered


test_cannot_deliver_more_than_available()
test_cannot_deliver_if_not_carrying()
test_must_deliver_at_picking_station()

test_exogenous_movement()
test_two_robots_cannot_be_in_same_cell()
test_robots_cannot_move_through_each_other()
test_object_cannot_move_outside_bounds_of_warehouse()
test_robot_cannot_be_in_different_cells()
test_two_shelves_cannot_be_in_same_cell()
test_one_action_per_time_step()
test_location_of_carried_shelf()
test_carried_shelf_moves_with_robot()
test_carries_false_common_sense_of_inertia()
test_carries_true_common_sense_of_inertia()
test_cannot_pickup_if_already_carrying()
test_cannot_pickup_if_not_in_same_location()
test_cannot_putdown_if_not_already_carrying()
test_cannot_putdown_on_highway()
test_cannot_putdown_on_pickingStation()
