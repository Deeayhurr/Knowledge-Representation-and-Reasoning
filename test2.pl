state(f,g).
state(f,ng).
state(nf,g).
state(nf,ng).
fluent(f).
fluent(g).
fluent(nf).
fluent(ng).
action(action).
agent(bill).
agent(jim).
causes(agent(AG), action(AC), RETURN, INDEX) :- AG = jim, AC = action,  INDEX = 0, state(A,g)=state(f,ng), RETURN = state(A,ng).
causes(agent(AG), action(AC), RETURN, INDEX) :- AG = bill, AC = action,  INDEX = 0, state(A,g)=state(f,ng), RETURN = state(nf,B).