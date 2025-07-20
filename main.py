import sys
import math

BOMB_RANGE = 4
class Entity:None
class Entity:
    x:int
    y:int

    def __init__(self, x,y):
        self.x = x
        self.y = y

    def dist(self, B:object)->int:# B: Entity
        return abs(self.x - B.x) + abs(self.y - B.y)

    def pythagore_dist(self, B:object):
        return ( (self.x - B.x)**2 + (self.y - B.y)**2 ) ** 0.5

    def __str__(self):
        return f"{self.x} {self.y}"
    
    def __eq__(self, value):
        if isinstance(value, Entity):
            return self.x == value.x and self.y == value.y
        return False

    def chooseNearestEntity(self, entities: list[Entity])->int:
        min_entity = -1
        min_dist = -1
        for entity in range(len(entities)):
            dist = self.dist(entities[entity])
            if min_entity == None or dist < min_dist:
                min_entity = entity
                min_dist = dist
        return min_entity
    
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

    def __str__(self):
        return f"Rect: {self.top} {self.right} {self.down} {self.down}"

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

    def getDomain(self, domain_size=None):
        # get an agent domain like territory
        if domain_size==None:
            domain_size = self.optimal_range
        return Rect(Entity(self.x - domain_size, self.y - domain_size), Entity(self.x + domain_size, self.y + domain_size))

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

    def getOrthoPeripheral(self)->dict:
        # return top right down left
        agents = list(self.agents.values())
        agents.sort(key=lambda A:A.x)
        left = agents[0]
        right = agents[-1]
        agents.sort(key=lambda A:A.y)
        top = agents[0]
        down = agents[0]

        return {"top":top,"right":right,"down":down,"left":left}



class MyEngine():
    canvas : Rect
    forbidden_spot: list[Entity]
    general_radar: Rect



    @classmethod
    def computeNotControlledZone(cls,zone:Rect, bluePeripheral:dict, redPeripheral:dict)->list[Entity]:
        res = []
        for y in range(zone.top, zone.down+1):
            for x in range(zone.left, zone.right+1):
                entity = Entity(x, y)
                blue_distance = [] 
                for direction in bluePeripheral:
                    blue_distance += [bluePeripheral[direction].dist(entity)]
                red_distance = [] 
                for direction in redPeripheral:
                    red_distance += [redPeripheral[direction].dist(entity)]
                if min(blue_distance) >= min(red_distance):
                    res += [entity]
        return res

    @classmethod
    def substractZoneFromRect(cls, A: Rect, zones: list[Rect])->list[Entity]:
        # get all avalaible places after removing zone
        available_places = []
        for y in range(A.top, A.down+1):
            for x in range(A.left, A.right+1):
                entity = Entity(x, y)
                available = True
                for zone in zones:
                    if zone.isEntityInsideMe(entity):
                        available = False
                        break
                if available:
                    available_places += [entity]
        return available_places


    @classmethod
    def get_obstacle_around_agent(cls, agent: Agent, domain_surface_pad= 1):
        obstacle = 0
        domain = Rect(Entity(agent.x-domain_surface_pad, agent.y-domain_surface_pad), Entity(agent.x+domain_surface_pad, agent.y+domain_surface_pad))
        # for y in range(domain.top, domain.down + 1):
        #     for x in range(domain.left, domain.right + 1):
        #         if Entity(x, y) in cls.forbidden_spot:
        #             obstacle += 1
        max_obstacle = 0
        for y in range(1, domain.down - domain.top):
            for x in range(1, domain.right  - domain.left):
                Y = domain.top + y
                X = domain.left + x                    
                R = Rect(Entity(domain.left, domain.top), Entity(X, Y))
                obstacle = 0
                for _x in range(R.left, R.right+1):
                    for _y in range(R.top, R.down+1):
                        if Entity(_x, _y) in cls.forbidden_spot:
                            obstacle += 1
                max_obstacle = max(max_obstacle, obstacle)
        return max_obstacle


    @classmethod
    # this method is not good yet
    def isagentTrapped(cls, agent: Agent, domain_size=1, forbidden_spot=[]):
        forbidden = cls.forbidden_spot + forbidden_spot
        for surface in range(1, domain_size+1):
            domain = Rect(Entity(agent.x-surface, agent.y-surface), Entity(agent.x+surface, agent.y+surface))
            obstacle = 0
            for x in range(domain.left, domain.right+1):
                if Entity(x, domain.top) in forbidden:
                    obstacle += 1
                if Entity(x, domain.down) in forbidden:
                    obstacle += 1

            for y in range(domain.top, domain.down + 1):
                if Entity(domain.right, y) in forbidden:
                    obstacle += 1
                if Entity(domain.left, y) in forbidden:
                    obstacle += 1
            perimeter = ((domain.right - domain.left+1) + (domain.down - domain.top+1))*2 - 4
            # print(f"{agent.agent_id}:[{surface}] [{perimeter}]{obstacle}", file=sys.stderr, flush=True)
            if obstacle == perimeter:
                return 1
        return 0


    @classmethod
    def check_multiple_kill(cls, targets: list[Agent], friend: list[Agent])->list:
        max_target_victim = None
        for target in targets:
            rect = target.getDomain(domain_size=1)
            victim = 0
            collateral = 0
            for y in range(rect.top, rect.down):
                for x in range(rect.left, rect.right):
                    _entity = Entity(x, y)
                    if _entity != target and target in targets:
                        victim += 1
                    if _entity in friend:
                        collateral += 1
            if collateral < victim:
                if max_target_victim == None or max_target_victim[0] > victim:
                    max_target_victim = [victim, target]

        return max_target_victim

    @classmethod
    def assign_target_for_multiple_kill(cls, agents: dict, targets:list[Agent], dont_move_zone: list[Rect]=[]):
        target_and_victim = []
        for target in targets:
            victim = 1
            for y in range(-1,2):
                for x in range(-1,2):
                    _entity = Entity(target.x+x, target.y+y)
                    if _entity != target and _entity in targets:
                        victim += 1
            target_and_victim += [[victim, target]]
        target_and_victim.sort(key=lambda x:-x[0])
        target_and_victim_copy = target_and_victim.copy()
        res = []
        # forbidden_spot = [Entity(target.x, target.y) for target in targets]
        for agent_id in agents:
            print(f"{agent_id} {agents[agent_id]} {cls.get_obstacle_around_agent(agents[agent_id], domain_surface_pad = 3)}", file = sys.stderr, flush=True)
            forbid = 0
            for dont_move in dont_move_zone:
                if dont_move.isEntityInsideMe(Entity(agents[agent_id].x, agents[agent_id].y)):
                    forbid = 1
                    break
            
            if forbid:
                res += [[agent_id, None]]
                continue

            if len(target_and_victim):
                i = 0
                while i < len(target_and_victim):
                    collateral = 0
                    for agent in agents:
                        if agents[agent] == target_and_victim[i][1]:
                            collateral = 1
                            break
                    if not collateral:
                        break
                    
                    i += 1
                print(f"i = {i}", file=sys.stderr, flush=True)
                i = i % len(target_and_victim) # shorty code if i > len(target_and_victim) then go back to zero
                res += [[agent_id, target_and_victim[i][1]]]
                target_and_victim.remove(target_and_victim[i])
            else:
                res += [[agent_id, target_and_victim_copy[0][1]]]
        return res

    @classmethod
    def assign_target(cls, agents:dict, targets:list[Entity])->list:
        squad_dist_target = {} # [{agent_1: [[targets_1, dist], [targets_2, dist]]}]
        # we gonna form first the agent-dist-target relations
        for _agent in agents:
            agent = agents[_agent]
            agent_dist_target = []
            for target in targets:
                target_dist = agent.dist(target)
                agent_dist_target += [
                    [target_dist, target]
                ]
            
            squad_dist_target[agent.agent_id]=sorted(agent_dist_target, key=lambda x:x[0])
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
            squad_dist_target.pop(mini)

            for agent_id in squad_dist_target.copy():
                if [agents[agent_id].dist(remove_target), remove_target] in squad_dist_target[agent_id]:
                    squad_dist_target[agent_id].remove([agents[agent_id].dist(remove_target), remove_target])
                if squad_dist_target[agent_id] == []:
                    squad_dist_target.pop(agent_id)

        return res

    @classmethod
    def assign_target_agent(cls, agents:dict, targets:list[Agent]):
        if not len(targets):
            return []
        # targets are Agent
        # and if same dist-agent-target the agents can target the same targets
        squad_dist_target = {} # [{agent_1: [[targets_1, dist], [targets_2, dist]]}]
        # we gonna form first the agent-dist-target relations
        for _agent in agents:
            agent = agents[_agent]
            agent_dist_target = []
            for _x in range(len(targets)):
                target_dist = agent.dist(targets[_x])
                agent_dist_target += [
                    [target_dist, targets[_x]]
                ]
            
            squad_dist_target[agent.agent_id]=sorted(agent_dist_target, key=lambda x:x[0])
        
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
                    if squad_dist_target[agent_id][0][1] not in remove_target:
                        remove_target += [ squad_dist_target[agent_id][0][1] ]
                    squad_dist_target.pop(agent_id)

            for agent_id in squad_dist_target.copy():
                for remove in remove_target:
                    if [agents[agent_id].dist(remove), remove] in squad_dist_target[agent_id]:
                        squad_dist_target[agent_id].remove([agents[agent_id].dist(remove), remove])
                if squad_dist_target[agent_id] == []:
                    squad_dist_target.pop(agent_id)

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
        
        if not len(blind_spots):return None
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

width, height = [int(i) for i in input().split()]

MyEngine.canvas = Rect(Entity(0,0), Entity(width-1, height-1))
MyEngine.forbidden_spot = []



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
            MyEngine.forbidden_spot += [Entity(x=x, y=y)]
# cover.sort(key=lambda c:-c.height)
# game loop

dont_move_zone = []
for corner in [
    [0,0],
    [MyEngine.canvas.right - 4, 0],
    [MyEngine.canvas.right - 4, MyEngine.canvas.down - 4],
    [0, MyEngine.canvas.down - 4],
]:
    x,y = corner
    rect = Rect(Entity(x, y), Entity(x+4, y+4))
    dont_move_zone += [rect]

DEBUG = 0

while True:
    agent_count = int(input())  # Total number of agents still in the game
    checking_survival = []
    for i in range(agent_count):
        # cooldown: Number of turns before this agent can shoot
        # wetness: Damage (0-100) this agent has taken
        agent_id, x, y, cooldown, splash_bombs, wetness = [int(j) for j in input().split()]
        checking_survival += [agent_id]
        # update data
        if mysquads.is_agent_member(agent_id):
            mysquads.update_agent_coord(agent_id, x,y)
            mysquads.agents[agent_id].wetness = wetness
            mysquads.agents[agent_id].shoot_cooldown = cooldown
            mysquads.agents[agent_id].splash_bomb = splash_bombs
        else:
            ennemy_squads.update_agent_coord(agent_id, x,y)
            ennemy_squads.agents[agent_id].wetness = wetness
            ennemy_squads.agents[agent_id].shoot_cooldown = cooldown
            ennemy_squads.agents[agent_id].splash_bomb = splash_bombs
    my_agent_count = int(input())  # Number of alive agents controlled by you

    # update squad check survivor
    for myagent_id in mysquads.agents.copy():
        if mysquads.agents[myagent_id].agent_id not in checking_survival:
            mysquads.eliminate_agent(myagent_id)

    for ennemy_agent_id in ennemy_squads.agents.copy():
        if ennemy_squads.agents[ennemy_agent_id].agent_id not in checking_survival:
            ennemy_squads.eliminate_agent(ennemy_agent_id)
    # update squad check survivor


    # init territory
    my_territory = []
    ennemy_territory = []

    for myagent in mysquads.agents.values():
        my_territory += [myagent.getDomain()]

    for ennemy_agent in ennemy_squads.agents.values():
        ennemy_territory += [ennemy_agent.getDomain()]

    
    available_places = MyEngine.computeNotControlledZone(MyEngine.canvas, mysquads.getOrthoPeripheral(), ennemy_squads.getOrthoPeripheral())
    if DEBUG >= 20:
        for place in available_places:
            print(f"{place}",file=sys.stderr, flush=True)
        print(f"len={len(available_places)}",file=sys.stderr, flush=True)
    # available_places = MyEngine.substractZoneFromRect(MyEngine.canvas,my_territory)# + ennemy_territory)
    #available_places = [place for place in available_places if (place not in list(ennemy_squads.agents.values())) and (place not in cover) and (place not in list(mysquads.agents.values()))] # filter places
    # init territory
    agent_explorer = {}
    agent_attacker = {}
    for agent_id in mysquads.agents:
        agent_domain = mysquads.agents[agent_id].getDomain()
        ennemy_detected = []
        for ennemy_id in ennemy_squads.agents:
            if agent_domain.isEntityInsideMe(ennemy_squads.agents[ennemy_id]):
                ennemy_detected += [ennemy_squads.agents[ennemy_id]]

        if len(ennemy_detected) > 0:
            can_shoot = mysquads.agents[agent_id].shoot_cooldown == 0
            can_bomb = mysquads.agents[agent_id].splash_bomb > 0 and (min([mysquads.agents[agent_id].dist(ennemy) for ennemy in ennemy_detected]) <= BOMB_RANGE)
            weapon = None

            # check if multiple kill
            if can_bomb:
                victim, target = MyEngine.check_multiple_kill(ennemy_detected, list(mysquads.agents.values()))
                if victim:
                    weapon = f"THROW {target}"

            if (weapon == None):
                if can_shoot:
                    target = mysquads.agents[agent_id].chooseNearestEntity(ennemy_detected)
                    weapon = f"SHOOT {ennemy_detected[target].agent_id}"
                
                else:
                    agent_explorer[agent_id]=mysquads.agents[agent_id]
                    continue

            hide = MyEngine.take_cover(mysquads.agents[agent_id], cover, ennemy_detected)

            action = []
            if hide:
                # MOVE
                action += [f"MOVE {hide}"]
            # ATTACK
            action += [
                f"{weapon}"
            ]
            print(f"{agent_id}; {'; '.join(action)}")

        else:
            # Explorer
            agent_explorer[agent_id]=mysquads.agents[agent_id]

    explore_action = MyEngine.assign_target(agent_explorer, available_places)
    for agent_id, target in explore_action:
        print(f"{agent_id}; MOVE {target}")
    DEBUG += 1




