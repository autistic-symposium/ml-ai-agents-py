## reinforcement learning notes

<br>

### overview

* we formalize the problem of reinforcement using ideas from dynamical system theory, as the optimal control of incompletely-known Markov decision processes.
* a learning agent must be able to sense the state of its environment to some extent and must be able to take actions that affect the state.
* markov decision processes are intented to include just these three aspects, sensation, action, and goal.
* the agent has to exploit what it has already experienced in order to obtain reward, but it has also to explore in order to make better action selections in the future.
* on a stochastic tasks, each action must be tried many times to gain a reliable estimate of its expected reward.

<br>

---

### elements of reinforcement learning

* beyond the agent and the environment, 4 more elements belong to a reinforcement learning system: a policy, a reward signal, a value funtion, and a model of the environmnet.
* a policy defines the learning agent's way of behacing at a given time. It's a mapping from perceiv ed states of the environment to actions to be taken when in those states. in general, policies may be stochastics (specifying probabilities for each action).
* a reward signal defines the goal of a reinforcement learning problem: on each time step, the environment sends to the reinforcement learning agent a single number called the reward. the agent's sole objective is to maximize the total reward over the run.
* a value function specifies what is good in the long run, the valye of a state in the total amount of reward an agent can expect to accumulate over the future, starting from that state
* a model of the environment.
* the most important feature distinguishing reinforcement learning from other types of learning is that it uses training information that evaluates the actions taken rather than instructs by giving correct actions. 

<br>

---

### finite markov decision processes (mdps)

* the problem involves evaluating feedbacks and choosing different actions in different situations.
* mdps are a classical formalization of sequential decision making, where actions influence not just immediate rewards, but also subsequent situations.
* mdps involve delayed reward and the need to trade off immediate and delayed reward.

##### the agent-environment interface

* mdps are meant to be a straightfoward framing of the problem of learning from interaction to achieve a goal.
* the learner and the decision makers is called the agent.
* the thing it interacts with, comprimising everything outside the agent, is called the environment.
* the environment gives rise to rewards, numerical values that the agent seeks to maximize over time through its choice of actions.

<br>

<img width="466" src="https://user-images.githubusercontent.com/1130416/228971927-3c574911-d0ca-4d2d-b795-8b0776599952.png">

<br>

* the agent and the environment interact at each of a sequence of discrete steps, t = 0, 1, 2, 3...
* at each time step t, the agent receives some representation of the environments state St
* on that basis, the agent selects an action At
* one step later, in part of a consequence of its action, the agent receives a numerical rewards and finds itself in a new state.
* the mdp and the agent together give rise to a sequence (trajectory)
* in a finite mdp, the set of states, actions, and rewards all have a finite number of elements. in this case, the random variables R and S have well defined discrete probability distributions dependent only on the proceding state and action.
* in a markov decision process, the probabilities given by p completely characterize the environment's dynamics.
* the state must include information about all aspects of the past agent-environment interaction that make a differnce for the future.
* anything that cannot be changed arbitrarily by the agent is considered to be outside of it and thus part of its environment.



##### goals and rewards


* each episode ends in a special state called the terminal state, followed by a reset to a standard starting state or to a sample from a standard distribution of starting states.
* almost all reinforcement learning algorithms involve estimating value functions—functions of states (or of state–action pairs) that estimate how good it is for the agent to be in a given state (or how good it is to perform a given action in a given state). 
* the Bellman equation averages over all the possibilities, weighting each by its probability of occurring. tt states that the value of the start state must equal the
(discounted) value of the expected next state, plus the reward expected along the way.
* solving a reinforcement learning task means finding a policy that achieves a lot of reward over the long run. 

<br>

---

### dynamic programming

* collection of algorithms that can be used to compute optimal policies given a perfect model of the environment as a mdp.
* a common way of obtaining approximate solutions for tasks with continuous states and actions is to quantize the state and action spaces and then apply finite-state DP methods. 
* the reason for computing the value function for a policy is to help find better policies.
* asynchronous DP algorithms are in-place iterative DP algorithms that are not organized in terms of systematic sweeps of the state set. these algorithms update the values of states in any order whatsoever, using whatever values of other states happen to be available. the values of some states may be updated several times before the values of others ar
* policy evaluation refers to the (typi- cally) iterative computation of the value function for a given policy. 
* policy improvement refers to the computation of an improved policy given the value function for that policy.


##### generalized policy interaction

* policy iteration consists of two simultaneous, interacting processes, one making the value function consistent with the current policy (policy evaluation), and the other making the policy greedy with respect to the current value function (policy improvement). 
* generalized policy iteration (GPI) refers to the general idea of letting policy-evaluation and policy-improvement processes interact, independent of the granularity and other details of the two processes. 
* DP is sometimes thought to be of limited applicability because of the curse of dimen- sionality, the fact that the number of states often grows exponentially with the number of state variables






