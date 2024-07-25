import pyhop
import json
import time

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
        Requires = rule[0]
        Consumes = rule[1]

        list = []

        commodities = ["ingot", "coal", "ore", "cobble", "stick", "plank", "wood"]
        for check in commodities:
            for key in Consumes.keys():
                if key == check:
                    newCheck = ("have_enough", ID, key, Consumes[key])
                    list.append(newCheck)

        # get Requires to the list
        for key in Requires.keys():
            list = [("have_enough", ID, key, Requires[key])] + list

        # get the name and the id
        list.append((name, ID))

        return list

    return method


def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
    
	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)
    
    # Iterate through all the recipes
    Produces_list = {}
    for Produce in data["Recipes"].keys():
        temp = data["Recipes"][Produce]["Produces"].items()
        for key, value in temp:
            try:
                requires = data["Recipes"][Produce]["Requires"]
            except KeyError:
                requires = {}

            try:
                consumes = data["Recipes"][Produce]["Consumes"]
            except KeyError:
                consumes = {}

            new_method = make_method(
                "op_" + Produce,
                [
                    requires,
                    consumes,
                ],
            )
            new_method.__name__ = Produce
            if key not in list(Produces_list.keys()):
                Produces_list[key] = [new_method]
            else:
                Produces_list[key].append(new_method)
                # sort the recipes so that faster recipes go first
                Produces_list[key].sort(
                    key=lambda p: data["Recipes"][p.__name__]["Time"]
                )

    for key in Produces_list.keys():
        pyhop.declare_methods(str("produce_" + key), *Produces_list[key])
    return
def make_operator(rule):
    def operator(state, ID):
        requires = rule[0]
        consumes = rule[1]
        produces = rule[2]
        time = rule[3]

        # check all requires
        for require in requires.keys():
            if requires[require] > getattr(state, require)[ID]:
                return False

        # check all consumes
        for consume in consumes:
            if consumes[consume] > getattr(state, consume)[ID]:
                return False

        # check remaining time
        if time > state.time[ID]:
            return False

        # update state for consumes and produces
        for key in consumes.keys():
            total = getattr(state, key)[ID]
            consumed = consumes[key]
            newTotal = total - consumed
            setattr(state, key, {ID: newTotal})

        for key in produces.keys():
            total = getattr(state, key)[ID]
            produced = produces[key]
            newTotal = total + produced
            setattr(state, key, {ID: newTotal})
        # update time
        state.time[ID] -= time

        return state

    return operator


def declare_operators(data):
    # your code here
    # hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
    for item in data["Recipes"].keys():
        requires = {}
        consumes = {}
        if "Requires" in data["Recipes"][item]:
            # hit:requiers is a dict
            requires = data["Recipes"][item]["Requires"]
        if "Consumes" in data["Recipes"][item]:
            consumes = data["Recipes"][item]["Consumes"]
        # result
        produces = data["Recipes"][item]["Produces"]
        # get time
        time = data["Recipes"][item]["Time"]

        rule = [requires, consumes, produces, time]

        operator = make_operator(rule)
        operator.__name__ = "op_" + item

        pyhop.declare_operators(operator)

    return

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        if (
            curr_task[0] == "produce"
            and curr_task[2] in data["Tools"]
            and curr_task in calling_stack
        ):
            return True
        
        # check if we have enough of the item
        if curr_task[0] == "produce" and curr_task[2] in data["Items"]:
            total_consumes = 0
            for task in tasks:
                if task[0] == "have_enough" and task[2] == curr_task[2]:
                    total_consumes += task[3]
            total_num = getattr(state, curr_task[2])[ID]
            if total_num >= total_consumes:
                return True

        have_enough_stone_axe = ("have_enough", ID, "stone_axe", 1)
        have_enough_wooden_axe = ("have_enough", ID, "wooden_axe", 1)

        if (
            curr_task[0] == "produce"
            and curr_task[2] == "iron_axe"
            and have_enough_stone_axe in calling_stack
        ):
            return True

        if (
            curr_task[0] == "produce"
            and curr_task[2] == "stone_axe"
            and have_enough_wooden_axe in calling_stack
        ):
            return True
        
        if curr_task[0] == "produce" and curr_task[2] == "iron_pickaxe":
            required = 0
            for task in tasks:
                if task[0] == "have_enough" and task[2] == "ingot":
                    required += task[3]
            if required <= 11 and required > 0:
                return True

        if curr_task[0] == "produce" and curr_task[2] == "wooden_axe":
            required = 0
            for task in tasks:
                if task[0] == "have_enough" and task[2] == "wood":
                    required += task[3]
            if required <= 9 and required > 0:
                return True

        return False  # if True, prune this branch
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

    print("\n")

    # Test case a
    start_time = time.time()
    state_a = set_up_state(data, 'agent', time=0)
    state_a.plank = {'agent': 1}
    goals_a = [('have_enough', 'agent', 'plank', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case a:")
    pyhop.pyhop(state_a, goals_a, verbose=1)
    end_time = time.time()
    #print("Time taken for test case a: ", end_time - start_time)

    # Test case b
    start_time = time.time()
    state_b = set_up_state(data, 'agent', time=300)
    goals_b = [('have_enough', 'agent', 'plank', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case b:")
    pyhop.pyhop(state_b, goals_b, verbose=1)
    end_time = time.time()
    #print("Time taken for test case b: ", end_time - start_time)

    # Test case c
    start_time = time.time()
    state_c = set_up_state(data, 'agent', time=10)
    state_c.plank = {'agent': 3}
    state_c.stick = {'agent': 2}
    goals_c = [('have_enough', 'agent', 'wooden_pickaxe', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case c:")
    pyhop.pyhop(state_c, goals_c, verbose=1)
    end_time = time.time()
    #print("Time taken for test case c: ", end_time - start_time)
    
    #Test case d
    start_time = time.time()
    state_d = set_up_state(data, 'agent', time=100)
    goals_d = [('have_enough', 'agent', 'iron_pickaxe', 1)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case d:")
    pyhop.pyhop(state_d, goals_d, verbose=1)
    end_time = time.time()
    #print("Time taken for test case d: ", end_time - start_time)
    
    #Test case e
    start_time = time.time()
    state_e = set_up_state(data, 'agent', time=175)
    goals_e = [('have_enough', 'agent', 'cart', 1),("have_enough", "agent", "rail", 10)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case e:")
    pyhop.pyhop(state_e, goals_e, verbose=1)
    end_time = time.time()
    #print("Time taken for test case e: ", end_time - start_time)
    
    #Test case f
    start_time = time.time()
    state_f = set_up_state(data, 'agent', time=250)
    goals_f = [('have_enough', 'agent', 'cart', 1),("have_enough", "agent", "rail", 20)]
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    print("Test case f:")
    pyhop.pyhop(state_f, goals_f, verbose=1)
    end_time = time.time()
    #print("Time taken for test case f: ", end_time - start_time)
    
    #pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=2)

    '''# Print the final states for verification
    print("\nFinal state for test case a:")
    pyhop.print_state(state_a)
    print("\nFinal state for test case b:")
    pyhop.print_state(state_b)
    print("\nFinal state for test case c:")
    pyhop.print_state(state_c)
    print("\nFinal state for test case d:")
    pyhop.print_state(state_d)
    print("\nFinal state for test case e:")
    pyhop.print_state(state_e)
    print("\nFinal state for test case f:")
    pyhop.print_state(state_f)'''