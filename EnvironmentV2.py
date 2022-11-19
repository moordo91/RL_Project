import math
from gym import Env
from gym.spaces import Discrete
import random


class PC:
    
    def __init__(self):
        self.pwSize = random.randint(4, 10)
        self.updateVer = random.randint(0, 1)   # update 상태가 최신이면 1, 최신이 아니면 0
        self.dataRate = random.randrange(0, 100)
        self.hacked = False


class Action:

    def __init__(self, target):
        self.pwSize = target[0].pwSize
        self.updateVer = target[0].updateVer
        self.dataRate = target[0].dataRate
        self.hacked = target[0].hacked
        self.link = target[1]
    
    def pwHack(self):   # https://www.security.org/how-secure-is-my-password/
        probability = random.random()
        if probability > 11.7 * (1.85 ** -self.pwSize):    # uniform distribution으로 계산
            self.hacked = False
        else:
            self.hacked = True
        return self.hacked
    
    def osHack(self):
        probability = random.random()
        if probability > 0.07 * (10**self.updateVer):
            self.hacked = True
        else:
            self.hacked = False
        return self.hacked

    def drHack(self):
        probability = random.random()
        if probability < self.dataRate / 100:
            self.hacked = True
        else:
            self.hacked = False
        return self.hacked
    
    def jumpPC(self):
        return random.sample(self.link, 1)[0]


class HackingEnv(Env):
    
    def __init__(self, network, size):
        self.size = size
        self.network = network
        self.state = network[0]
        self.start = network[0]
        
        self.action_space = Discrete(4)
        self.observation_space = Discrete(size)
        self.hacking_length = 24

    def reset(self):
        start = self.start
        self.state = start
        self.hacking_length = 24
        for i in range(self.size):
            self.network[i][0].hacked = False
        resetedState = (start[0].pwSize, start[0].updateVer, start[0].dataRate, start[0].hacked)
        return resetedState
    
    def step(self, action):
        self.hacking_length -= 1
        reward = 0

        while self.state[0].hacked:
            nextIdx = Action(self.state).jumpPC()
            self.state = self.network[nextIdx]

        if action:
            nextIdx = Action(self.state).jumpPC()
            self.state = self.network[nextIdx]
            reward += 1.5
        else:
            reward -= 1

        # 종료 조건
        for i in range(self.size):
            if not self.network[i][0].hacked:
                done = False
                break

        done = True if self.hacking_length <= 0 else False

        info = {}
        
        nextState = (self.state[0].pwSize, self.state[0].updateVer, self.state[0].dataRate, self.state[0].hacked)
        return nextState, reward, done, info

    def render(self):
        pass

    def action_return(self):
        act = Action(self.state)
        return [act.pwHack(), act.osHack(), act.drHack(), act.jumpPC(),]
        
        

def gen_network(size, edge):

    network = []

    for _ in range(size):
        network.append([PC(), []])

    population = [i for i in range(size)]
    for i in range(size):
        if i in population:
            population.remove(i)

        if len(population) < edge:
            population = [j for j in range(size)]
            population.remove(i)
        
        basket = random.sample(population, k=edge)
        for num in basket:
            network[i][1].append(num)
            population.remove(num)

    return network

