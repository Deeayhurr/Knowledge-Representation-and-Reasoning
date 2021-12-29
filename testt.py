from pyswip import Prolog

prolog = Prolog()
prolog.consult('domain.pl')
print(list(prolog.query('causes(agent(jim), action(action), RETURN, INDEX)')))