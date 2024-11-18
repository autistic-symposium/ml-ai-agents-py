## deep learning 

<br>

### timeline tl; dr

<br>

* **[2012: imagenet and alexnet](https://github.com/tensorflow/models/blob/master/research/slim/nets/alexnet.py)**

* **[2013: atari with deep reinforcement learning](https://www.tensorflow.org/agents/tutorials/1_dqn_tutorial)**
* **[2014: seq2seq](https://www.tensorflow.org/addons/tutorials/networks_seq2seq_nmt)**
* **[2014: adam optmizer](https://github.com/tensorflow/tensorflow/blob/v2.2.0/tensorflow/python/keras/optimizer_v2/adam.py#L32-L281)**
* **[2015: gans](https://www.tensorflow.org/tutorials/generative/dcgan)**
* **[2015: resnets](https://github.com/tensorflow/tensorflow/blob/v2.2.0/tensorflow/python/keras/applications/resnet.py)**
* **[2017: transformers](https://github.com/huggingface/transformers)**
* **[2018: bert](https://arxiv.org/abs/1810.04805)**

<br>

---

### deep reinforcement learning for trading

<br>

* a map consists of a set of states, a set of actions, a transition function that describes the probability of moving rom one state to another after taking an action, and a reward function that assigns a numerical reward to each state-action pair

* the goal of a map is to maximize its expected cumulative reward over a sequence of actions, called a policy.

* a policy is a function that maps each state to a probability distribution over actions. The optimal policy is the one that maximizes the expected cumulative rewards.

* the problem of reinforcement learning can be formalized using ideas from dynamical systems theory, specifically, as the optimal control of incompletely-known Markov decision processes.

* as opposed to supervised learning, an agent must be able to learn from its own experience. and as oppose to unsupervised learning because, reinforcement learning is trying to maximize a reward signal instead of trying to find hidden structure. 

* the agent has to exploit what it has already experienced in order to obtain reward, but it also has to explore in order to make better action selections in the future. on a stochastic task, each action must be tried many times to gain a reliable estimate of its expected reward. 

* beyond the agent and the environment, one can identify four main subelements of a reinforcement learning system: a policy, a reward signal, a value function, and, optionally, a model of the environment.

* traditional reinforcement learning problems can be formulated as a markov decision process (MDP): 
  * we have an agent acting in an environment
  * each step *t* the agent receives as the input the current state S_t, takes an action A_t, and receives a reward R_{t+1} and the next state S_{t+1}
  * the agent choose the action based on some policy pi: A_t = pi(S_t)
  * it's our goal to find a policy that maximizes the cumulative reward Sum R_t over some finite or infinite time horizon


<br>

<img width="500" src="https://user-images.githubusercontent.com/1130416/227799494-d62aab7f-d6cf-419f-be03-1d2dbdee1853.png">

<br>

#### agent

<br>

* agent is the trading agent (e.g. the human trader who opens the gui of an exchange and makes trading decision based on the current state of the exchange and their account)

<br>

#### environment

<br>

* the exchange and other agents are the environment, and they are not something we can control
* by putting other agents together into some big complex environment, we lose the ability to explicitly model them
* if we try to reverse-engineer the algorithms and strategies that other traders are running, put us into a multi-agent reinforcement learning (MARL) problem setting

<br>

#### state

<br>

* in the case of trading on an exchange, we don't observe the complete state of the environment (e.g. other agents), so we are dealing with a partially observable markov decision process (pomdp).
* what the agents observe is not the actual state S_t of the environment, but some derivation of that.
* we can call the observation X_t, which is calculated using some function of the full state X_t ~ O(S_t)
* the observation at each timestep t is simply the history of all exchange events received up to time t.
* this event history can be used to build up the current exchange state, however, in order for our agent to make decisions, extra info such as account balance and open limit orders need to be included.

<br>

#### time scale

<br>

* hft techniques: decisions are based almost entirely on market microstructure signals. decisions are made on nanoseconds timescales and trading strategies use dedicated connections to exchanges and extremly fast but simple algorithms running fpga hardware.
* neural networks are slow, they can't make predictions on nanoseconds time scales, so they can't compete with the speed of hft algorithms.
* guess: the optimal time scale is between a few milliseconds and a few minutes.
* can deep rl algorithms pick up hidden patterns?

<br>

#### action space

<br>

* the simplest approach has 3 actions: buy, hold, and sell. this works but limits us to placing market orders and to invest a deterministic amount of money at each step.
* in the next level we would let our agents learn how much money to invest, based on the uncertainty of our model, putting us into a continuous action space.
* in the next level, we would introduce limit orders, and the agent needs to decide the level (price) and wuantity of the order, and be able to cancel orders that have not been yet matched.

<br>

#### reward function

<br>

* there are several possible reward functions, an obvious would realized PnL (profit and loss). the agent receives a reward whenever it closes a position.
* the net profit is either negative or positive, and this is the reward signal.
* as the agent maximize the total cumulative reward, it learns to trade profitably. the reward function leads to the optimal policy in the limit.
* however, buy and sell actions are rare compared to doing nothing; the agent needs to learn without receiving frequent feedback.
* an alternative is unrealized pnl, which the net profit the agent would get if it were to close all of its positions immediately.
* because the unrealized pnl may change at each time step, it gives the agent more frequent feedback signals. however the direct feedback may bias the agent towards short-term actions.
* both naively optimize for profit, but a trader may want to minimize risk (lower volatility)
* using the sharpe ration is one simple way to take risk into account. other way is maximum drawdown.

<br>

<img width="505" src="https://user-images.githubusercontent.com/1130416/227811225-9af06c79-3f86-48e8-899c-ee5a80bc91e1.png">

<br>

#### learned policies

<br>

* instead of needing to hand-code a rule-based policy, rl directly learns a policy


<br>

#### trained directly in simulation environments

<br>

* we need separate backtesting and parameter optimization steps because it was difficult for our strategies to take into account environmental factors: order book liquidity, fee structures, latencies.
* getting around environmental limitations is part of the opimization process. if we simulate the latency in the reinforcement learning environment, and this results in the agent making a mistake, the agent will get a negative rewards, forcing it to learn to work around the latencies.
* by learning a model of the environment and performing rollouts using techniques like a monte carlo tree search (mcts), we could take into account potential reactions of the market (other agents)
* by being smart about the data we collect from the live environment, we can continously improve our model
* do we act optimally in the live environment to generate profits, or do we act suboptimally to gather interesting information that we can use to improve the model of our environment and other agents?

<br>

#### learning to adapt to market conditions

<br>

* some strategy may work better in a bearish environment but lose money in a bullish environment.
* because rl agents are learning powerful policies parameterized by NN, they can alos learn to adapt to market conditions by seeing them in historical data, given that they are trained over long time horizon and have sufficient memory.

<br>

#### trading as research

<br>

* the trading environment is a multiplayer game with thousands of agents acting simultaneously
* understanding how to build models of other agents is only one possible we can, we can choose perfom actions in a live environment with the goal of maximizing the information grain with respect to kind policies the other agents may be following
* trading agents receive sparse rewards from the market. naively applying reward-hungry rl algorithms will fail.
* this opens up the possibility for new algorithms and techniques, that can efficiently deal with sparse rewards.
* many of today's standard algorithms, such as dqn or a3c, use a very naive approach exploration - basically adding random noise to the policy. however, in the trading case, most states in the environment are bad, and there are only a few good ones. a naive random approach to exploration will almost never stumble upon good state-actions paris.
* the trading environment is inherently nonstationary. market conditions change and other agent join, leave, and constantly change their strategies.
* can we train an agent that can transit from bear to bull and then back to bear, without needing to be re-trained?
