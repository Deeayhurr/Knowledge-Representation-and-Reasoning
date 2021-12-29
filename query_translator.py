from genericpath import isdir
from os import stat
from typing import Match
from pyswip import Prolog
from itertools import combinations
from PyQt5.QtWidgets import QTextEdit, QPushButton
import re
from os.path import isfile

class query_translator:

    QUERY_KEYWORDS = set(['holds', 'after', 'involved'])

    def __init__(self) -> None:
        self.query = ''
        self.result = True

        self.prolog = Prolog()

        self.prolog_file = open("domain.pl", "w+")
        
        self.actions_and_agents = []
        self.fluent_causes_dict = {}
        self.initial_states = []
        self.fluent = ''
        self.agent = ''
        self.state_history = []

        super().__init__()

    def read_query(self, query):
        self.query = query
        self.actions_and_agents = []
        keyword = set(self.query.split()) & self.QUERY_KEYWORDS

        if len(list(keyword)) > 0:

            for key in list(keyword):
                
                match(key):
                    case "holds":
                        self.fluent = self.query.split("holds")[0]

                    case "after":
                        try :
                            actions_and_agents = self.query.split("after")[1].split('[')[1].split(']')[0]
                            actions_and_agents = re.findall('\((.*?)\)',actions_and_agents)
                            print(actions_and_agents)
                            for action_agent in actions_and_agents:
                                if (action_agent.split(',')[0],action_agent.split(',')[1]) not in self.actions_and_agents :
                                    print((action_agent.split(',')[0],action_agent.split(',')[1]))
                                    self.actions_and_agents.append((action_agent.split(',')[0],action_agent.split(',')[1]))
                                    
                        except Exception as e :
                            print(e)

                    case "involved":
                        try :
                            self.agent = self.query.split("involved in")[0]
                            actions_and_agents = re.findall('\((.*?)\)',self.query.split("involved in")[1])
                            for action_agent in actions_and_agents:
                                if (action_agent.split(',')[0],action_agent.split(',')[1]) not in self.actions_and_agents :
                                    self.actions_and_agents.append((action_agent.split(',')[0],action_agent.split(',')[1]))

                        except Exception as e :
                            print(e)

            print(f'Fluent that is supposed to hold : {self.fluent}')

            self.prolog.consult('domain.pl')
            for index, (agent, action) in enumerate(self.actions_and_agents):
                try :
                    if index < 1 :
                        print(f"causes(agent({agent}), action({action}), RETURN, INDEX)")
                        print(list(self.prolog.query(f"causes(agent({agent}), action({action}), RETURN, INDEX)")))
                        query_answer_list = list(self.prolog.query(f"causes(agent({agent}), action({action}), RETURN, INDEX)"))
                        print(f"Result : {query_answer_list}")
                        query_before_state = self.states_initials.copy()
                        query_after_state = self.states_initials.copy()
                        print(f'before {query_before_state}')
                        visited_indices = []
                        for dict in query_answer_list:
                            state = dict['RETURN']
                            index = dict['INDEX']
                            return_fluents = [fluent.strip() for fluent in  re.findall('\((.*?)\)',state)[0].split(',')]

                            if 'Variable' in state :
                                for idx, fluent in enumerate(return_fluents):
                                    if 'Variable' in fluent :
                                        return_fluents[idx] = flatten(query_before_state)[idx]

                            query_after_state[index] = return_fluents
                            visited_indices.append(index)

                        print('----------')
                        print(self.states_initials)
                        print(visited_indices)
                        print(len(self.states_initials))
                        print(len(visited_indices))
                        if len(visited_indices) != int(len(self.states_initials)):
                            print('not involved')
                            self.result = False
                            print(False)
                            print('----------')

                        print(f'After {query_after_state}')
                        self.state_history.append(flatten(query_after_state))

                        after_flattened = flatten(query_after_state)

                        if query_before_state == query_after_state:
                            if self.fluent.strip() not in after_flattened:
                                print('not involved')
                                self.result = False

                        print(self.result)

                    else :
                        if self.agent.strip() == self.actions_and_agents[index-1][0].strip():
                            if not(self.result):
                                print('Not involved')
                                print('False')
                                return

                        query = f"{self.fluent} holds after [({','.join(self.actions_and_agents[index])})]"
                        print(query)
                        query_translator_temp = query_translator()
                        updated_state = []
                        for i in range(1, int(len(self.fluents) / 2) + 1):
                            fluent_at_index = self.fluents_dict[i]
                            not_fluent_at_index = self.fluents_dict[-i]

                            if fluent_at_index in self.state_history[index-1] and not_fluent_at_index in self.state_history[index-1]:
                                continue
                            if fluent_at_index in self.state_history[index-1]:
                                updated_state.append(fluent_at_index)
                            if not_fluent_at_index in self.state_history[index-1]:
                                updated_state.append(not_fluent_at_index)

                        print(updated_state)
                        query_translator_temp = query_translator()
                        query_translator_temp.add_domain(self.fluents, self.actions ,self.agents, updated_state, self.domains)
                        query_translator_temp.read_query(query)
                        self.result = query_translator_temp.result


                except Exception (e) :
                    print(e)

    def add_domain(self, fluents, actions, agents, initial_states, domains):
        print(f'initial state : {initial_states}')
        self.prolog = Prolog()
        self.fluents_dict = {}
        actions_dict = {}
        self.inconsistent_domain = False

        fluents = [fluent.replace('-','n') for fluent in fluents]
        self.fluents = fluents
        self.actions = actions
        self.agents = agents
        self.domains = domains
        initial_states = [fluent.replace('-','n') for fluent in initial_states]
        self.initial_states = initial_states
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
                fluent = domain.split("causes")[1].split("if")[0].strip().replace('-','n')
                agent = domain.split("by")[1].split("causes")[0].strip()
                actions_dict[(action, agent)].append(fluent)

        for domain in domains:
            if "causes" in domain:
                agent = domain.split("by")[1].split("causes")[0].strip()
                if "if" in domain:
                    pre_conditional_fluents = domain.split("if")[1].strip().replace('-','n')
                    out_fluent = domain.split("causes")[1].split("if")[0].strip().replace('-','n')
                    pre_conditional_fluents = pre_conditional_fluents.split(",")
                    pre_conditional_fluents = [
                        fluent.strip() for fluent in pre_conditional_fluents
                    ]
                    for fluent in pre_conditional_fluents:
                        fluent_causes_dict[(out_fluent, agent)].append(fluent)

        self.fluent_causes_dict = fluent_causes_dict

        for domain in domains:
            if "after" in domain:
                action = domain.split("after")[1].split("by")[0].strip()
                fluent = domain.split("after")[0].strip().replace('-','n')
                agent = domain.split("by")[1].strip()

                #checking for inconsistent domain
                for (action_, agent_), fluent__ in actions_dict.items():
                    if agent_ ==  agent:
                        if fluent in fluent__:
                            self.inconsistent_domain = False  
                            break                
                        else:
                            self.inconsistent_domain = True
                            self.result = True


                if fluent not in actions_dict[(action, agent)]:
                    actions_dict[(action, agent)].append(fluent)
                for (fluent_, agent_), caused_fluents in fluent_causes_dict.items():
                    if fluent_ == fluent and agent_ == agent:
                        for fluent__ in caused_fluents:
                            if fluent__ not in actions_dict[(action, agent)]:
                                actions_dict[(action, agent)].append(fluent__)

        self.fluent_index = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        index = 1
        for fluent in fluents:
            if fluent[0] == "n":
                f = fluent[1:]
                self.fluents_dict[index] = f.strip().lower()
                self.fluents_dict[-index] = fluent.strip().lower()
                index = index + 1

        perm = list(combinations(list(self.fluents_dict.keys()), int(len(fluents) / 2)))
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
        self.states_initials = []
        for chunk in perm:
            state = []
            for num in chunk:
                state.append(self.fluents_dict.get(num))
            
            # if all(item in state for item in initial_states):
            #     states_initial.append(state)
            if set(self.initial_states).issubset(state):
                self.states_initials.append(state)
            
            states.append(state)

        # checking for inconsistent domain
        initial_states_indices = [abs(list(self.fluents_dict.keys())[list(self.fluents_dict.values()).index(fluent)]) for fluent in self.initial_states]
        if (len(initial_states_indices) != len(set(initial_states_indices))):
            self.result = True
            self.inconsistent_domain = True
            
        # checking for inconsistent domain
        for (action, agent) in actions_dict:
            for fluent in actions_dict[(action, agent)]:
                agnt= agent
                for fluentt in actions_dict[(action, agent)]:
                    for fluent_index_dict, fluent_in_dict in self.fluents_dict.items():
                        if fluent in fluent_in_dict:
                            fluent_in_dict_index = fluent_index_dict
                        if fluentt in fluent_in_dict:
                            fluentt_in_dict_id = fluent_index_dict
                            if int(fluent_in_dict_index) + int(fluentt_in_dict_id) == 0:
                                for fluent__cs in self.initial_states:
                                    for fluent_cs in self.initial_states:
                                        if (fluent_cs in fluent_causes_dict[(fluent, agnt)] 
                                        or fluent__cs in fluent_causes_dict[(fluentt, agnt)]):
                                            self.inconsistent_domain  =  True
                                            self.result = True

        for state in states:
            print(f'state({",".join(state)})')
            self.prolog_file.write(f'state({",".join(state)}).\n')

        for fluent in fluents:
            print(f"fluent({fluent})")
            self.prolog_file.write(f"fluent({fluent}).\n")
        for action in actions:
            print(f"action({action})")
            self.prolog_file.write(f"action({action}).\n")
        for agent in agents:
            print(f"agent({agent})")
            self.prolog_file.write(f"agent({agent}).\n")
        pre_conditional_fluents = []

        
        # Treating consistent and inconsistent domain accordingly
        if self.inconsistent_domain:
            print("Inconsistent Domain")
            self.result = True
            print(self.result)
            return
        else:
            try : 
                for idx, domain in enumerate(domains):
                    action = domain.split("by")[0].strip()
                    agent = domain.split("by")[1].split("causes")[0].strip()              
                    for tmp_idx,domain_temp in enumerate(domains[idx:len(domains)]):
                        action_temp = domain_temp.split("by")[0].strip()
                        agent_temp = domain_temp.split("by")[1].split("causes")[0].strip()        
                        if action_temp == action and agent_temp == agent:
                            if 'if' in domain and 'if' not in domain_temp:
                                domains.remove(domain_temp)
                            if 'if' not in domain and 'if' in domain_temp:
                                domains.remove(domain)
            except :
                pass

            for domain in domains:
                if "causes" in domain:
                    action = domain.split("by")[0].strip()
                    agent = domain.split("by")[1].split("causes")[0].strip()
                    fluent = domain.split("causes")[1].split("if")[0].strip().replace('-','n')
                    pre_conditional_fluents = []

                    try:
                        pre_conditional_fluents = domain.split("if")[1].strip().replace('-','n')
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
                            fluent_at_index = self.fluents_dict[i]
                            not_fluent_at_index = self.fluents_dict[-i]
                            if fluent_at_index in pre_conditional_fluents:
                                ini.append(fluent_at_index)
                            if not_fluent_at_index in pre_conditional_fluents:
                                ini.append(not_fluent_at_index)

                            if (
                                fluent_at_index not in pre_conditional_fluents
                                and not_fluent_at_index not in pre_conditional_fluents
                            ):
                                ini.append(self.fluent_index[i - 1])


                            if fluent_at_index in actions_dict[(action, agent)]:
                                ini_return.append(fluent_at_index)
                            if not_fluent_at_index in actions_dict[(action, agent)]:
                                ini_return.append(not_fluent_at_index)

                            if (
                                fluent_at_index not in actions_dict[(action, agent)]
                                and not_fluent_at_index not in actions_dict[(action, agent)]
                            ):
                                ini_return.append(self.fluent_index[i - 1])
                        
                        
                        for index, states_initial in enumerate(self.states_initials):
                            print(f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},  INDEX = {index}, state({','.join(ini)})=state({','.join(states_initial)}), RETURN = state({','.join(ini_return)})")
                            self.prolog_file.write(
                                f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},  INDEX = {index}, state({','.join(ini)})=state({','.join(states_initial)}), RETURN = state({','.join(ini_return)}).\n"
                                )
                            
                            
                        
                    else:
                        ini_return = []
                        for i in range(1, int(len(fluents) / 2) + 1):
                            fluent_at_index = self.fluents_dict[i]
                            not_fluent_at_index = self.fluents_dict[-i]
                            if fluent_at_index in actions_dict[(action, agent)]:
                                ini_return.append(fluent_at_index)
                            if not_fluent_at_index in actions_dict[(action, agent)]:
                                ini_return.append(not_fluent_at_index)

                            if (
                                fluent_at_index not in actions_dict[(action, agent)]
                                and not_fluent_at_index not in actions_dict[(action, agent)]
                            ):
                                ini_return.append(self.fluent_index[i - 1])
                        for index, states_initial in enumerate(self.states_initials):
                            print(f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},INDEX= {index}, state({','.join(states_initial)}), RETURN = state({','.join(ini_return)})")
                            self.prolog_file.write(
                                f"causes(agent(AG), action(AC), RETURN, INDEX) :- AG = {agent}, AC = {action},INDEX= {index}, state({','.join(states_initial)}), RETURN = state({','.join(ini_return)}).\n"
                            )

        self.prolog_file.close()

def flatten(t):
    return [item for sublist in t for item in sublist]



# fluents = ["f","g","h","nf","ng","nh"]
# actions = ["action"]
# agents = ["bill","fred"]
# initial_states = ["f"]
# domains = [
#     "action by bill causes g if f",
#     "action by fred causes h if nh"
# ]



# #query = "bill involved in [(fred,action),(bill,action)]"
# query = "h holds after [(fred,action)]"
# query_translator_temp = query_translator()
# query_translator_temp.add_domain(fluents, actions ,agents, initial_states,domains)
# query_translator_temp.read_query(query)