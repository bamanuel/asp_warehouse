%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% sort and object declaration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% static fluents
node(X,Y):- init(object(node,N), value(at,pair(X,Y))).
highway(X,Y):- init(object(highway,H), value(at,pair(X,Y))).
pickingStation(PS,X,Y):- init(object(pickingStation,PS), value(at,pair(X,Y))).

% initial object and their location
{robot(R);robot(R,X,Y,0)}=2:- init(object(robot,R),value(at,pair(X,Y))).
{shelf(S);shelf(S,X,Y,0)}=2:- init(object(shelf,S),value(at,pair(X,Y))).
{product(I);product(I,S,U,0)}=2:- init(object(product,I),value(on,pair(S,U))).
{order(O);order(O,I,U,PS,0)}=2:- init(object(order,O),value(line,pair(I,U))),
    init(object(order,O),value(pickingStation,PS)).

% initial auxiliary states
{carries(R,S,f,0)}:- robot(R), shelf(S).
{product(I,S,0,0)}:- product(I), shelf(S).
{order(O,I,0,PS,0)}:- order(O), product(I), pickingStation(PS,X,Y).

%%%%%%%%%%%%%%%%%%%
% state description
%%%%%%%%%%%%%%%%%%%

% Two robots cannot occupy same cell
R1=R2:- robot(R1,X,Y,T), robot(R2,X,Y,T).

% Two shelves cannot occupy same cell
S1=S2:- shelf(S1,X,Y,T), shelf(S2,X,Y,T).

% robot cannot go outside bounds of warehouse
:- robot(R,X,Y,T), not node(X,Y).

% robots cannot ghost through each other
R1=R2:- robot(R1,X1,Y1,T), robot(R2,X2,Y2,T),
        robot(R1,X2,Y2,T-1), robot(R2,X1,Y1,T-1).

% location of shelf is determined by robot that carries it
shelf(S,X,Y,T):- carries(R,S,t,T), robot(R,X,Y,T), robot(R).

% Exclude unsuccessful plans
:- order(O,I,U,PS,maxstep), U>0.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% effect and preconditions of action
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Move
robot(R,X+Dx,Y+Dy,T):- move(R,Dx,Dy,T), robot(R,X,Y,T-1).

% Pickup
carries(R,S,t,T):- pickup(R,S,T).
{X1=X2;Y1=Y2}=2:- pickup(R,S,T), robot(R,X1,Y1,T-1), shelf(S,X2,Y2,T-1).
:- pickup(R,S,T), carries(R,S1,t,T-1).

% Putdown
carries(R,S,f,T):- putdown(R,S,T).
:- putdown(R,S,T), carries(R,S,f,T-1).
:- putdown(R,S,T), robot(R,X,Y,T), highway(X,Y).

% Deliver
order(O,I,U1-U,PS,T):- deliver(R,O,S,I,U,PS,T), order(O,I,U1,PS,T-1).
product(I,S,U1-U,T):- deliver(R,O,S,I,U,PS,T), product(I,S,U1,T-1).
:- deliver(R,O,S,I,U,PS,T), carries(R,S,f,T-1).
:- deliver(R,O,S,I,U,PS,T), carries(R,S,t,T-1), product(I,S,U1,T-1), U1 < U.
{X1=X2;Y1=Y2}=2:- deliver(R,O,S,I,U,PS,T), robot(R,X1,Y1,T-1), pickingStation(PS,X2,Y2).

% One action per timestep per robot
:- 2{move(R,Dx,Dy,T); pickup(R,S1,T); putdown(R,S2,T); deliver(R,O,S3,I,U,PS,T)}, robot(R), T=1..maxstep.

%%%%%%%%%%%%%%%%%%%%%%%%%%%
% domain independent axioms
%%%%%%%%%%%%%%%%%%%%%%%%%%%

% uniqueness and existence of fluent values
:- not {robot(R,X,Y,T)}=1, robot(R), T=0..maxstep.
:- not {shelf(S,X,Y,T)}=1, shelf(S), T=0..maxstep.
:- not {carries(R,S,B,T)}=1, robot(R), shelf(S), T=0..maxstep.
:- not {product(I,S,U,T)}=1, product(I), shelf(S), T=0..maxstep.
:- not {order(O,I,U,PS,T)}=1, order(O), product(I), pickingStation(PS,X,Y), T=0..maxstep.

% Commonsense law of inertia
{robot(R,X,Y,T)}:- robot(R,X,Y,T-1), T=1..maxstep.
{shelf(S,X,Y,T)}:- shelf(S,X,Y,T-1), T=1..maxstep.
{carries(R,S,B,T)}:- carries(R,S,B,T-1), T=1..maxstep.
{product(I,S,U,T)}:- product(I,S,U,T-1), T=1..maxstep.
{order(O,I,U,PS,T)}:- order(O,I,U,PS,T-1), T=1..maxstep.

% Actions are exogenous 
{move(R,Dx,Dy,T): Dx=-1..1, Dy=-1..1, |Dx|!=|Dy|}:- robot(R), T=1..maxstep.
{pickup(R,S,T)}:- robot(R), shelf(S), T=1..maxstep.
{putdown(R,S,T)}:- robot(R), shelf(S), T=1..maxstep.
{deliver(R,O,S,I,1..U,PS,T)}:- robot(R), order(O,I,U,PS,T-1), product(I,S,U1,T-1), T=1..maxstep.

% Translate actions into occur terms
occurs(object(robot,R),move(Dx,Dy),T):- move(R,Dx,Dy,T).
occurs(object(robot,R),pickup,T):- pickup(R,S,T).
occurs(object(robot,R),putdown,T):- putdown(R,S,T).
occurs(object(robot,R),deliver(O,I,U),T):- deliver(R,O,S,I,U,PS,T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Optimization
%%%%%%%%%%%%%%%%%%%%%%%%%%%

actions(N):- N=#count{1,A,O,T:occurs(O,A,T)}.
time(V):- V=#max{T:occurs(O,A,T)}.
#minimize{T@1:time(T)}.
#minimize{N@0:actions(N)}.

#show actions/1.
#show time/1.
#show occurs/3.
