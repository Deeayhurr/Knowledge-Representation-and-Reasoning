from pyswip import Prolog
from pyswip.core import PL_put_variable
from itertools import combinations, permutations
import re
import itertools
import time
import operator


def add_domain(fluents, actions, agents, initial_states, domains):
    prolog = Prolog()
    fluents_dict = {}
    actions_dict = {}
    inconsistent_domain = False
    for action in actions:
        for agent in agents:
            actions_dict[(action, agent)] = []

    fluent_causes_dict = {}
    for fluent in fluents:
        for agent in agents:
            fluent_causes_dict[(fluent, agent)] = []

    for domain in domains:
        if "causes" in domain:
            action = domain.split("by")[0].strip()
            fluent = domain.split("causes")[1].split("if")[0].strip()
            agent = domain.split("by")[1].split("causes")[0].strip()
            actions_dict[(action, agent)].append(fluent)

    for domain in domains:
        if "causes" in domain:
            agent = domain.split("by")[1].split("causes")[0].strip()
            if "if" in domain:
                pre_conditional_fluents = domain.split("if")[1]
                out_fluent = domain.split("causes")[1].split("if")[0].strip()
                pre_conditional_fluents = pre_conditional_fluents.split(",")
                pre_conditional_fluents = [
                    fluent.strip() for fluent in pre_conditional_fluents
                ]
                for fluent in pre_conditional_fluents:
                    fluent_causes_dict[(out_fluent, agent)].append(fluent)

    for domain in domains:
        if "after" in domain:
            action = domain.split("after")[1].split("by")[0].strip()
            fluent = domain.split("after")[0].strip()
            agent = domain.split("by")[1].strip()

            #checking for inconsistent domain
            for (action_, agent_), fluent__ in actions_dict.items():
                if agent_ ==  agent:
                    if fluent in fluent__:
                        inconsistent_domain = False  
                        break                 
                    else:
                        inconsistent_domain = True

            print(inconsistent_domain)

            if fluent not in actions_dict[(action, agent)]:
                actions_dict[(action, agent)].append(fluent)
            for (fluent_, agent_), caused_fluents in fluent_causes_dict.items():
                if fluent_ == fluent and agent_ == agent:
                    for fluent__ in caused_fluents:
                        if fluent__ not in actions_dict[(action, agent)]:
                            actions_dict[(action, agent)].append(fluent__)

    fluent_index = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    index = 1
    for fluent in fluents:
        if fluent[0] == "n":
            f = fluent[1:]
            fluents_dict[index] = f.lower()
            fluents_dict[-index] = fluent.lower()
            index = index + 1

    perm = list(combinations(list(fluents_dict.keys()), int(len(fluents) / 2)))
    trash = []
    for chunk in perm:
        abs_chunk = [abs(num) for num in chunk]
        for num in abs_chunk:
            if abs_chunk.count(abs(num)) > 1:
                trash.append(chunk)
                break

    for aTrash in trash:
        if aTrash in perm:
            perm.remove(aTrash)

    states = []
    states_initials = []
    for chunk in perm:
        state = []
        for num in chunk:
            state.append(fluents_dict.get(num))
        
        # if all(item in state for item in initial_states):
        #     states_initial.append(state)
        if set(initial_states).issubset(state):
            states_initials.append(state)
        
        states.append(state)


    # checking for inconsistent domain
    initial_states_indices = [abs(list(fluents_dict.keys())[list(fluents_dict.values()).index(fluent)]) for fluent in initial_states]
    if (len(initial_states_indices) != len(set(initial_states_indices))):
        inconsistent_domain = True
        
    print(inconsistent_domain)

    # checking for inconsistent domain
    for (action, agent) in actions_dict:
        for fluent in actions_dict[(action, agent)]:
            agnt= agent
            for fluentt in actions_dict[(action, agent)]:
                for fluent_index_dict, fluent_in_dict in fluents_dict.items():
                    if fluent in fluent_in_dict:
                        fluent_in_dict_index = fluent_index_dict
                    if fluentt in fluent_in_dict:
                        fluentt_in_dict_id = fluent_index_dict
                        if int(fluent_in_dict_index) + int(fluentt_in_dict_id) == 0:
                            for fluent__cs in initial_states:
                                for fluent_cs in initial_states:
                                    if (fluent_cs in fluent_causes_dict[(fluent, agnt)] 
                                    or fluent__cs in fluent_causes_dict[(fluentt, agnt)]):
                                        inconsistent_domain  =  True
    print(inconsistent_domain)
    for state in states:
        print(f'state({",".join(state)})')
        prolog.assertz(f'state({",".join(state)})')

    for fluent in fluents:
        print(f"fluent({fluent})")
        prolog.assertz(f"fluent({fluent})")
    for action in actions:
        print(f"action({action})")
        prolog.assertz(f"action({action})")
    for agent in agents:
        print(f"agent({agent})")
        prolog.assertz(f"agent({agent})")
    pre_conditional_fluents = []

     
    # Treating consistent and inconsistent domain accordingly
    if inconsistent_domain:
        print("Inconsistent Domain")
    else:
        for domain in domains:
            if "causes" in domain:
                action = domain.split("by")[0].strip()
                agent = domain.split("by")[1].split("causes")[0].strip()
                fluent = domain.split("causes")[1].split("if")[0].strip()
                pre_conditional_fluents = []

                try:
                    pre_conditional_fluents = domain.split("if")[1]
                except:
                    pass

                if len(pre_conditional_fluents) > 0:
                    if "," in pre_conditional_fluents:
                        pre_conditional_fluents = pre_conditional_fluents.split(",")
                        pre_conditional_fluents = [
                            fluent.strip() for fluent in pre_conditional_fluents
                        ]
                    else:
                        pre_conditional_fluents = list([pre_conditional_fluents.strip()])

                    ini = []
                    ini_return = []
                    for i in range(1, int(len(fluents) / 2) + 1):
                        fluent_at_index = fluents_dict[i]
                        not_fluent_at_index = fluents_dict[-i]
                        if fluent_at_index in pre_conditional_fluents:
                            ini.append(fluent_at_index)
                        if not_fluent_at_index in pre_conditional_fluents:
                            ini.append(not_fluent_at_index)

                        if (
                            fluent_at_index not in pre_conditional_fluents
                            and not_fluent_at_index not in pre_conditional_fluents
                        ):
                            ini.append(fluent_index[i - 1])

                        if fluent_at_index in actions_dict[(action, agent)]:
                            ini_return.append(fluent_at_index)
                        if not_fluent_at_index in actions_dict[(action, agent)]:
                            ini_return.append(not_fluent_at_index)

                        if (
                            fluent_at_index not in actions_dict[(action, agent)]
                            and not_fluent_at_index not in actions_dict[(action, agent)]
                        ):
                            ini_return.append(fluent_index[i - 1])

                    all_states_indices = [fluent_index[i] for i in range(0,len(ini))]
                    
                    
                    for index, states_initial in enumerate(states_initials):
                        print(f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},  INDEX = {index}, state({','.join(ini)})=state({','.join(states_initial)}), RETURN = state({','.join(ini_return)})")
                        prolog.assertz(
                            f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},  INDEX = {index}, state({','.join(ini)})=state({','.join(states_initial)}), RETURN = state({','.join(ini_return)})"
                            )
                        
                        
                    
                else:
                    ini_return = []
                    for i in range(1, int(len(fluents) / 2) + 1):
                        fluent_at_index = fluents_dict[i]
                        not_fluent_at_index = fluents_dict[-i]
                        if fluent_at_index in actions_dict[(action, agent)]:
                            ini_return.append(fluent_at_index)
                        if not_fluent_at_index in actions_dict[(action, agent)]:
                            ini_return.append(not_fluent_at_index)

                        if (
                            fluent_at_index not in actions_dict[(action, agent)]
                            and not_fluent_at_index not in actions_dict[(action, agent)]
                        ):
                            ini_return.append(fluent_index[i - 1])
                    print(f"causes(agent(AG), action(AC), RETURN) :- AG = {agent}, AC = {action}, RETURN = state({','.join(ini_return)})")
                    prolog.assertz(
                        f"causes(agent(AG), action(AC), RETURN) :- AG = {agent}, AC = {action}, RETURN = state({','.join(ini_return)})"
                    )
        print(actions_dict)
        query_answer_list = list(prolog.query("causes(agent(tom), action(action), RETURN, INDEX)"))

        query_before_state = states_initials.copy()
        query_after_state = states_initials.copy()
        print(f'before {query_before_state}')
        for dict in query_answer_list:
            state = dict['RETURN']
            index = dict['INDEX']
            return_fluents = [fluent.strip() for fluent in  re.findall('\((.*?)\)',state)[0].split(',')]
            query_after_state[index] = return_fluents

        print(f'After {query_after_state}')

        if query_before_state == query_after_state:
            print('not involved')
        else :
            print('involved')



fluents = ["f", "g", "nf", "ng"]
actions = ["action"]
agents = ["bill", "tom"]
initial_states = ["f","g"]
domains = [
    "action by tom causes ng if g",
    "action by bill causes f if ng",
]

add_domain(fluents, actions, agents, initial_states, domains)