import pyhop
import json
import inspect

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough(state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        tasks = []

        required_items = rule.get('Requires', {})
        consumed_items = rule.get('Consumes', {})

        for item, amount in required_items.items():
            tasks.append(('have_enough', ID, item, amount))

        for item, amount in consumed_items.items():
            tasks.append(('have_enough', ID, item, amount))

        operation_name = f"op_{name.replace(' ', '_')}"
        tasks.append((operation_name, ID))

        return tasks

    return method


def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
    
	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)
    
    # Iterate through all the recipes
    for name, rule in data['Recipes'].items():
        # Create the method with a safe name
        method = make_method(name, rule)
        method_name = 'produce_' + list(rule['Produces'].keys())[0]
        pyhop.declare_methods(method_name, method)

    # Directly declare a simple method for producing wood using punch_for_wood
    def produce_wood(state, ID):
        return [('op_punch_for_wood', ID)]
    pyhop.declare_methods('produce_wood', produce_wood)

def make_operator(rule):
    def operator(state, ID):
        required_time = rule.get('Time', 0)
        if state.time[ID] < required_time:
            return False

        required_items = rule.get('Requires', {})
        for item, amount in required_items.items():
            if getattr(state, item)[ID] < amount:
                return False

        consumed_items = rule.get('Consumes', {})
        for item, amount in consumed_items.items():
            if getattr(state, item)[ID] < amount:
                return False
            current_amount = getattr(state, item)
            current_amount[ID] -= amount
            setattr(state, item, current_amount)

        produced_items = rule.get('Produces', {})
        for item, amount in produced_items.items():
            current_amount = getattr(state, item)
            current_amount[ID] += amount
            setattr(state, item, current_amount)

        state.time[ID] -= required_time
        return state

    return operator


def declare_operators(data):
    # your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
    operators = []
    # iterate through the operator list
    for recipe_name, rule in data['Recipes'].items():
        # Get the current operator
        operator = make_operator(rule)
        operator.__name__ = f"op_{recipe_name.replace(' ', '_')}"
        operators.append(operator)
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    # prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters:
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        if depth > 100:
            return True
        return False# if True, prune this branch
    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: time}

    for item in data['Items']:
        setattr(state, item, {ID: 0})

    for item in data['Tools']:
        setattr(state, item, {ID: 0})

    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})

    return state

def set_up_goals(data, ID):
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))

    return goals

if __name__ == '__main__':
    rules_filename = 'crafting.json'

    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, 'agent', time=100)
    goals = set_up_goals(data, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    # pyhop.print_operators()
    # pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=1)
    #pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

    pyhop.print_state(state)

    # Test case a
    state_a = set_up_state(data, 'agent', time=0)
    state_a.plank = {'agent': 1}
    goals_a = [('have_enough', 'agent', 'plank', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case a:")
    pyhop.pyhop(state_a, goals_a, verbose=1)

    # Test case b
    state_b = set_up_state(data, 'agent', time=300)
    goals_b = [('have_enough', 'agent', 'plank', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case b:")
    pyhop.pyhop(state_b, goals_b, verbose=1)

    # Test case c
    state_c = set_up_state(data, 'agent', time=10)
    state_c.plank = {'agent': 3}
    state_c.stick = {'agent': 2}
    goals_c = [('have_enough', 'agent', 'wooden_pickaxe', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case c:")
    pyhop.pyhop(state_c, goals_c, verbose=1)

    '''
    #Test case d
    state_d = set_up_state(data, 'agent', time=100)
    goals_d = [('have_enough', 'agent', 'iron_pickaxe', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case d:")
    pyhop.pyhop(state_d, goals_d, verbose=1)
    '''

    
    #pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=2)
    

    


    # Print the final states for verification
    print("\nFinal state for test case a:")
    pyhop.print_state(state_a)
    print("\nFinal state for test case b:")
    pyhop.print_state(state_b)
    print("\nFinal state for test case c:")
    pyhop.print_state(state_c)