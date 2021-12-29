fluent(alive).
fluent(loaded).
fluent(nalive).
fluent(nloaded).
fluent(hasgun).
fluent(nhasgun).

action(takegun).
action(shoot).

state(alive, hasgun, loaded).
state(alive, nHasgun, loaded).
state(alive, nHasgun, nLoaded).
state(alive, hasgun, nLoaded).
state(nAlive, hasgun, loaded).
state(nAlive, nHasgun, loaded).
state(nAlive, hasgun, nLoaded).
state(nAlive, nHasgun, nLoaded).

action(action, agent, out)
agent(bill).

% causes(agent(AG), action(A), [state(fluent(INI_1))], RETURN) :- AG = bill, A = shoot, INI_1 = alive, RETURN = nloaded.
% causes(agent(AG), action(A), [state(fluent(INI_1))], RETURN) :- AG = bill, A = shoot, INI_1 = loaded, RETURN = nalive.
% causes(agent(AG), action(A), RETURN) :- AG = bill, A = shoot, RETURN = nalive.

causes(agent(AG), action(A), RETURN) :- AG = bill, A = shoot, state(X, hasgun, loaded), state(X,Y,Z), RETURN=state(nAlive, Y, nLoaded).
causes(agent(AG), action(A), RETURN) :- AG = bill, A = takegun, state(X, nHasgun, Y), RETURN=state(X, hasgun, Y).
causes(agent(AG), action(A), RETURN) :- AG = bill, A = takegun, state(X, nHasgun, Y), RETURN=state(X, hasgun, Y).



after(agent(bill), action(takegun), RETURN) :- RETURN=state(X, hasgun, Y).
