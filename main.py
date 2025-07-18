import sys
import math

# Win the water fight by controlling the most territory, or out-soak your opponent!

class Entity:
    x:int
    y:int

    def __init__(self, x,y):
        self.x = x
        self.y = y

    def dist(self, B:object):# B: Entity
        return abs(self.x - B.x) + abs(self.y - B.y)

    def pythagore_dist(self, B:object):
        return ( (self.x - B.x)**2 + (self.y - B.y)**2 ) ** 0.5

    def __str__(self):
        return f"{self.x} {self.y}"

class Rect:
    left: int
    right: int
    top: int
    down: int

    def __init__(self, A: Entity, B: Entity):
        self.left = min(A.x, B.x)
        self.right = max(A.x, B.x)
        self.top = min(A.y, B.y)
        self.down = max(A.y, B.y)

    def isEntityInsideMe(self, e: Entity):
        return e.x >= self.left and e.x <= self.right and e.y >= self.top and e.y <= self.down  

class Block(Entity):
    height: int

    def __init__(self, x, y, height):
        super().__init__(x ,y)
        self.height = height

class Agent(Entity):
    agent_id:int
    player:int
    shoot_cooldown:int
    optimal_range:int
    soaking_power:int
    splash_bomb:int
    wetness:int

    def __init__(self, agent_id, player, shoot_cooldown, optimal_range, soaking_power, splash_bombs):
        super().__init__(-1,-1)
        self.agent_id=agent_id
        self.player=player
        self.shoot_cooldown=shoot_cooldown
        self.optimal_range=optimal_range
        self.soaking_power=soaking_power
        self.splash_bomb=splash_bombs

class Squad():
    agents: dict

    def __init__(self, agents:dict):
        # {agent_id: Agent()}
        self.agents = agents.copy()
    
    def is_agent_member(self, agent_id:int):
        return agent_id in self.agents.keys()

    def update_agent_coord(self, agent_id, x,y):
        if agent_id in self.agents.keys():
            self.agents[agent_id].x = x
            self.agents[agent_id].y = y

    def rank_wetness(self):
        res = list(self.agents.values())
        res.sort(key=lambda x:x.wetness)
        return res
    
    def eliminate_agent(self, agent_id:int):
        self.agents.pop(agent_id)


class MyEngine():
    canvas : Rect

    @classmethod
    def assign_target(cls, agents:dict, targets:list):
        squad_dist_target = {} # [{agent_1: [[targets_1, dist], [targets_2, dist]]}]
        # we gonna form first the agent-dist-target relations
        min_target_dist = None
        for _agent in agents:
            agent = agents[_agent]
            agent_dist_target = []
            for _x in range(len(targets)):
                target_dist = agent.dist(Entity(targets[_x][0], targets[_x][1]))
                agent_dist_target += [
                    [target_dist, targets[_x]]
                ]
                if min_target_dist == None:
                    min_target_dist = target_dist
                min_target_dist = min(min_target_dist, target_dist)
            
            squad_dist_target[agent.agent_id]=sorted(agent_dist_target)
        res = []
        while len(squad_dist_target):
            mini = list(squad_dist_target.keys())[0] # Take the first agent as minima
            min_target_dist = squad_dist_target[mini][0][0]

            for agent_id in squad_dist_target:
                if squad_dist_target[agent_id][0][0] < min_target_dist:
                    min_target_dist = squad_dist_target[agent_id][0][0]
                    mini = agent_id
            res += [[mini, squad_dist_target[mini][0][1]]]
            remove_target = squad_dist_target[mini][0][1]
            del(squad_dist_target[mini])
            for agent_id in squad_dist_target:
                squad_dist_target[agent_id] = [dist for dist in squad_dist_target[agent_id] if dist[1] != remove_target]
            new_squad_dist_target = {}
            for agent_id in squad_dist_target:
                if squad_dist_target[agent_id] != []:
                    new_squad_dist_target[agent_id] = squad_dist_target[agent_id] 
            squad_dist_target = new_squad_dist_target
        return res

    @classmethod
    def assign_target_agent(cls, agents:dict, targets:list[Agent]):
        # targets are Agent
        squad_dist_target = {} # [{agent_1: [[targets_1, dist], [targets_2, dist]]}]
        # we gonna form first the agent-dist-target relations
        min_target_dist = None
        for _agent in agents:
            agent = agents[_agent]
            agent_dist_target = []
            for _x in range(len(targets)):
                target_dist = agent.dist(targets[_x])
                agent_dist_target += [
                    [target_dist, targets[_x]]
                ]
                if min_target_dist == None:
                    min_target_dist = target_dist
                min_target_dist = min(min_target_dist, target_dist)
            
            squad_dist_target[agent.agent_id]=sorted(agent_dist_target)
        res = []
        while len(squad_dist_target):
            mini = list(squad_dist_target.keys())[0] # Take the first agent as minima
            min_target_dist = squad_dist_target[mini][0][0]

            for agent_id in squad_dist_target:
                if squad_dist_target[agent_id][0][0] < min_target_dist:
                    min_target_dist = squad_dist_target[agent_id][0][0]
            remove_target = []
            for agent_id in squad_dist_target.copy():
                if squad_dist_target[agent_id][0][0] == min_target_dist:
                    res += [[agent_id, squad_dist_target[agent_id][0][1].agent_id]]
                    remove_target = squad_dist_target[agent_id][0][1]
                    squad_dist_target.pop(agent_id)

            for agent_id in squad_dist_target:
                squad_dist_target[agent_id] = [dist for dist in squad_dist_target[agent_id] if dist[1] not in remove_target]
            new_squad_dist_target = {}
            for agent_id in squad_dist_target:
                if squad_dist_target[agent_id] != []:
                    new_squad_dist_target[agent_id] = squad_dist_target[agent_id] 
            squad_dist_target = new_squad_dist_target
        return res        

    @classmethod
    def get_coverage(cls, cover:Block, predator:Agent, dir_prey_cover:int):
        up_cover = Rect(Entity(cover.x-2, cover.y-1), Entity(cover.x+2, cover.y-3))
        right_cover = Rect(Entity(cover.x-1, cover.y-2), Entity(cover.x-3, cover.y+2))
        down_cover = Rect(Entity(cover.x+2, cover.y+1), Entity(cover.x-2, cover.y+3))
        left_cover = Rect(Entity(cover.x+1, cover.y-2), Entity(cover.x+3, cover.y+2))

        ortho_cover = [up_cover, right_cover, down_cover, left_cover]
        if cover.pythagore_dist(predator) > 2 and ortho_cover[dir_prey_cover].isEntityInsideMe(predator):
            return 1
        return 0

    @classmethod
    def get_ortho_spot(cls, spot):
        return [Entity(spot.x + x, spot.y + y) for x,y in [[0,-1],[1,0], [0,1], [-1,0]]]

    @classmethod
    def take_best_spot(cls, cover:Block, forbidden_spot:list[Entity], predators: list[Agent]):
        blind_spots = []

        up_cover = Rect(Entity(cover.x-2, cover.y-1), Entity(cover.x+2, cover.y-3))
        right_cover = Rect(Entity(cover.x-1, cover.y-2), Entity(cover.x-3, cover.y+2))
        down_cover = Rect(Entity(cover.x+2, cover.y+1), Entity(cover.x-2, cover.y+3))
        left_cover = Rect(Entity(cover.x+1, cover.y-2), Entity(cover.x+3, cover.y+2))

        ortho_cover = [up_cover, right_cover, down_cover, left_cover]

        # orthoganally adjacent of Entity
        # up right down left
        ortho_spot = cls.get_ortho_spot(cover)
        for _spot in range(4):
            spot = ortho_spot[_spot]
            if spot not in forbidden_spot and cls.canvas.isEntityInsideMe(spot):
                blind_spot = 0
                for predator in predators:
                    if cover.pythagore_dist(predator) > 2 and ortho_cover[_spot].isEntityInsideMe(predator):
                        blind_spot += 1               
                blind_spots += [[blind_spot, spot]]
        blind_spots.sort(key=lambda x:-x[0]) # Most blind spot
        return blind_spots[0][1]

    @classmethod
    def take_cover(cls, agent:Agent, cover:list[Block], predators:list[Agent]):
        # predators : list of Agent attacking me#
        # sort criteria : blocking_strength, distance , 
        max_height = max(x.height for x in cover)
        filtered_cover = [x for x in cover if x.height==max_height]
        filtered_cover.sort(key=lambda n:n.dist(agent))
        max_cover = filtered_cover[0]
        spot = cls.take_best_spot(max_cover, forbidden_spot = [Entity(x.x, x.y) for x in predators], predators=predators)
        return spot
        # cover: Block object list
        # The predators could be a squad Objects, but the squada Objects is not needed so much here
    

my_id = int(input())  # Your player id (0 or 1)
agent_data_count = int(input())  # Total number of agents in the game
myagents = {}
ennemy_agents = {}
for i in range(agent_data_count):
    # agent_id: Unique identifier for this agent
    # player: Player id of this agent
    # shoot_cooldown: Number of turns between each of this agent's shots
    # optimal_range: Maximum manhattan distance for greatest damage output
    # soaking_power: Damage output within optimal conditions
    # splash_bombs: Number of splash bombs this can throw this game
    agent_id, player, shoot_cooldown, optimal_range, soaking_power, splash_bombs = [int(j) for j in input().split()]
    agent = Agent(agent_id=agent_id, player=player, shoot_cooldown=shoot_cooldown, optimal_range=optimal_range, soaking_power=soaking_power, splash_bombs=splash_bombs)
    if player == 0:
        myagents[agent_id]=agent
    else:
        ennemy_agents[agent_id]=agent
# width: Width of the game map
# height: Height of the game map

mysquads = Squad(myagents)
ennemy_squads = Squad(ennemy_agents)
cover = [] # Block object list of obstacles
cover_entity = [] # Entity objct list of obstacles

width, height = [int(i) for i in input().split()]
for i in range(height):
    inputs = input().split()
    for j in range(width):
        # x: X coordinate, 0 is left edge
        # y: Y coordinate, 0 is top edge
        x = int(inputs[3*j])
        y = int(inputs[3*j+1])
        tile_type = int(inputs[3*j+2])
        if tile_type != 0:
            cover += [Block(x=x, y=y, height=tile_type)]
            cover_entity += [Entity(x=x, y=y)]
# cover.sort(key=lambda c:-c.height)
# game loop
MyEngine.canvas = Rect(Entity(0,0), Entity(width-1, height-1))

while True:
    agent_count = int(input())  # Total number of agents still in the game
    for i in range(agent_count):
        # cooldown: Number of turns before this agent can shoot
        # wetness: Damage (0-100) this agent has taken
        agent_id, x, y, cooldown, splash_bombs, wetness = [int(j) for j in input().split()]

        # update data
        if mysquads.is_agent_member(agent_id):
            mysquads.update_agent_coord(agent_id, x,y)
            mysquads.agents[agent_id].wetness = wetness
        else:
            ennemy_squads.update_agent_coord(agent_id, x,y)
            ennemy_squads.agents[agent_id].wetness = wetness

    my_agent_count = int(input())  # Number of alive agents controlled by you
    # action = mysquads.assign_target([[6,1], [6,3]])
    ennemy_attacking = MyEngine.assign_target_agent(ennemy_squads.agents, list(mysquads.agents.values()))
    my_predator = {}
    for ennemy, myagent in ennemy_attacking:
        my_predator[mysquads.agents[myagent]] = (my_predator.get(mysquads.agents[myagent]) or []) + [ennemy_squads.agents[ennemy]] 
    # my_action = mysquads.assign_target_agent([[agent.x,agent.y] for agent in mysquads.agents.values()])
    hide_action = {}
    shoot_action = {}
    #Debug my_predator
    # print([[x.agent_id, [x.agent_id for x in my_predator[x]]] for x in my_predator])
    for myagent in my_predator: 
        hide_spot = MyEngine.take_cover(myagent, cover, my_predator[myagent])
        hide_action[myagent.agent_id]=hide_spot

        mytargets = []
        for predator in my_predator[myagent]:
            ennemy_shield = 0
            spots = MyEngine.get_ortho_spot(predator)
            # checking around enemy if there is cover
            for _spot in range(4): #up right down left
                if [spots[_spot].x, spots[_spot].y] in [[_.x, _.y]for _ in cover_entity]:
                    block = [c for c in cover if c.x==spots[_spot].x and c.y==spots[_spot].y][0]
                    shield = MyEngine.get_coverage(cover=block, predator=myagent, dir_prey_cover=(_spot+2)%4) # reversing POV like if up -> down
                    ennemy_shield = max(ennemy_shield, shield and block.height or 0)
            mytargets += [[ennemy_shield, predator]]
        mytargets.sort(key=lambda x:x[0])
        mytarget = mytargets[0][1]
        shoot_action[myagent.agent_id] = mytarget

    # for x in hide_action:
    #     print(f"{x} {hide_action[x]}")
    # for x in shoot_action:
    #     print(f"{x} {shoot_action[x]}")
    # shoot_on = ennemy_squads.rank_wetness()[-1]
    for agent_id in mysquads.agents.keys():
        shoots = f"SHOOT {shoot_action[agent_id].agent_id}"
        move = f"MOVE {hide_action[agent_id]}"
        actions = [move , shoots]
        print(f"{agent_id}; {'; '.join(actions)}")
        # agent = action[i][0]
        # target = action[i][1]
        # print(f"{agent};  MOVE {target[0]} {target[1]}")
        # agent_id --> shoot_on
        # shoot_on.wetness += mysquads.agents[agent_id].soaking_power
        # print(f"{agent_id};  SHOOT {shoot_on.agent_id}")
    
    # remove died agent
    for agent_id in ennemy_squads.agents.copy():
        if ennemy_squads.agents[agent_id].wetness >= 100:
            ennemy_squads.eliminate_agent(agent_id)
    for agent_id in mysquads.agents.copy():
        if mysquads.agents[agent_id].wetness >= 100:
            mysquads.eliminate_agent(agent_id)
