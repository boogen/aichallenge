#!/usr/bin/env python
from ants import *
from collections import deque
from sets import Set
import binaryheap
import math

KILL = 1
SAFE = 2
EQUAL = 3
DIE = 4

class roboboogie:
    def __init__(self):
        pass
        
    

    def do_setup(self, ants):
        self.agents = {'food':{}, 'explore':{}, 'hills':{}, 'enemy':{}}

        self.directions = ('n', 'e', 's', 'w')
        self.dirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]
        self.max_value = sys.maxint # ants.rows + ants.cols
        self.open_list = []
        self.last_seen = {}
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.open_list.append(0)
                self.last_seen[(row, col)] = 0
        self.open_list.append(0)
        self.rows = ants.rows
        self.cols = ants.cols

        self.visible = {}

        self.neighbours = {}
        for row in range(ants.rows):
            for col in range(ants.cols):
                loc = (row, col)
                nbrs = []
                for dir in self.directions:
                    n = ants.destination(loc, dir)
                    nbrs.append(n)
                self.neighbours[loc] = nbrs
        self.paths = []
        self.crash = False
        self.kill_counter = 0

    
    def clear(self, ants):
        for row in range(ants.rows):
            for col in range(ants.cols):
                n = (row, col)
                self.visible[n] = ants.visible(n)
                if self.visible[n]:
                    self.last_seen[n] = self.max_value
                elif self.last_seen[n] > 0:
                    self.last_seen[n] -= 1
                    
                for goal in self.agents.keys():
                    self.agents[goal][n] = 0
        
    def fast_bfs(self, ants, start_list, fun):
        marked = set(start_list)

        index = 0
        i = 0
        for loc in start_list:
            self.open_list[i] = loc
            i += 1
        length = len(start_list)
  
        t = 0
        
        while index < length:
            loc = self.open_list[index]
            index += 1
            fun(ants, loc)
            for new_loc in self.neighbours[loc]:
                if new_loc not in marked:
                    self.open_list[length] = new_loc
                    length += 1
                    marked.add(new_loc)


    def recalculate_scents(self, ants):
        time1 = ants.time_remaining()
        self.clear(ants)

#        time1 = ants.time_remaining()
        self.enemy_hills = set([ hill_loc for hill_loc, owner in ants.hill_list.items() if owner != MY_ANT])
        
        self.fast_bfs(ants, self.enemy_hills, self.diffuse_hills)

        self.enemy_ants = set([ant_loc for ant_loc, owner in ants.ant_list.items() if owner != MY_ANT])
        self.fast_bfs(ants, self.enemy_ants, self.diffuse_ants)
#        print "1. bfs: " + str(time1 - ants.time_remaining())
        unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                loc = (row, col)
                if not self.visible[loc]:
                    for n in self.neighbours[loc]:
                        if self.visible[n]:
                            unseen.append(loc)
                            break

        self.fast_bfs(ants, unseen, self.diffuse_explore)
            


    def diffuse_hills(self, ants, loc):
        if not ants.passable(loc):
            self.agents['hills'][loc] = 0
            return
        if not self.visible[loc]:
            self.agents['hills'][loc] = 0
            return

        if loc in self.enemy_hills:
            self.agents['hills'][loc] = self.max_value
        else:
            self.diffuse(ants, loc, 'hills')

    def diffuse_ants(self, ants, loc):
        if not ants.passable(loc):
            self.agents['enemy'][loc] = 0
            return
        if not self.visible[loc]:
            self.agents['enemy'][loc] = 0
            return
        
        if loc in self.enemy_ants:
            self.agents['enemy'][loc] = self.max_value
        else:
            self.diffuse(ants, loc, 'enemy')

    def diffuse_explore(self, ants, loc):
        if not ants.passable(loc):
            self.agents['explore'][loc] = 0
            return

        if not self.visible[loc]:
            self.agents['explore'][loc] = self.max_value - self.last_seen[loc]
        else:
            self.diffuse(ants, loc, 'explore')

    def diffuse_food(self, ants, loc):

        if not ants.passable(loc):
            self.agents['food'][loc] = 0
            return
        if loc in ants.my_ants():
            self.agents['food'][loc] = 0
            return
        if not self.visible[loc]:
            self.agents['food'][loc] = 0
            return


        if loc in ants.food():
            self.agents['food'][loc] = self.max_value
        else:
            self.diffuse(ants, loc, 'food')



    
    def diffuse(self, ants, loc, goal):
        value = 0
        p = 0.25
        if goal == 'hills':
            p = 0.99
        for n in self.neighbours[loc]:
            value += 0.25 * self.agents[goal][n]

        self.agents[goal][loc] = value
        
    def find_goal(self, ants, ant_loc, goal):
        max_value = 0
        dest = ant_loc
        for neighbour in self.neighbours[ant_loc]:
            if self.agents[goal][neighbour] > max_value:
                max_value = self.agents[goal][neighbour]
                dest = neighbour
        
        if dest != ant_loc:
            return [ant_loc, dest]
        else:
            return [ant_loc]

    def make_move(self, ants, path):
        if len(path) > 1:
            if path[1] not in self.incoming:
                self.incoming[path[1]] = []
            self.incoming[path[1]].append(path)
            self.outgoing[path[0]] = path[1]

        
    def topological_sort(self, ants):
        L = deque([])
        marked = set([])
        for path in self.paths:
            if path[0] in self.outgoing and self.outgoing[path[0]] not in self.outgoing:
                L.append(path)
                marked.add(path[0])

        sorted = []

        while len(L):
            path = L.popleft()
            sorted.append(path)
            if path[0] in self.incoming:
                for p in self.incoming[path[0]]:
                    if p[0] not in marked and p != path:
                        L.append(p)
                        marked.add(p[0])

        for ant_loc in self.standing:
            can_kill, pos = self.try_to_kill(ants, ant_loc)
            if can_kill:
                self.kill_counter += 1
                self.orders.add(pos)
                dir = ants.direction(ant_loc, pos)[0]
                ants.issue_order((ant_loc, dir))
            elif (self.tiles[ant_loc] == KILL or self.tiles[ant_loc] == SAFE) and ant_loc not in self.orders:
                self.orders.add(ant_loc)
            else:
                for n in self.neighbours[ant_loc]:
                    if ants.passable(n) and self.tiles[n] == SAFE and n not in self.orders:
                        self.orders.add(n)
                        dir = ants.direction(ant_loc, n)[0]
                        ants.issue_order((ant_loc, dir))
                        break

            
        for path in sorted:
            if len(path) > 1:
                
                can_kill, pos = self.try_to_kill(ants, path[0])
                if can_kill:
                    self.kill_counter += 1
                    self.orders.add(pos)
                    dir = ants.direction(path[0], pos)[0]
                    ants.issue_order((path[0], dir))
                    path.pop(0)
                elif self.tiles[path[0]] == KILL and path[0] not in self.orders:
                    self.orders.add(path[0])                    
                elif self.tiles[path[1]] == SAFE and path[1] not in self.orders:
                    dir = ants.direction(path[0], path[1])[0]
                    self.orders.add(path[1])
                    ants.issue_order((path[0], dir))          
                    path.pop(0)
                elif self.tiles[path[0]] == SAFE and path[0] not in self.orders:
                    self.orders.add(path[0])
                else:
                    for n in self.neighbours[path[0]]:
                        if ants.passable(n) and self.tiles[n] == SAFE and n not in self.orders:
                            self.orders.add(n)
                            dir = ants.direction(path[0], n)[0]
                            ants.issue_order((path[0], dir))
                            path.pop(0)
                            break

                
                    
        
    def try_to_kill(self, ants, ant_loc):
        for n in self.neighbours[ant_loc]:
            if ants.passable(n) and n not in self.orders and self.tiles[n] == KILL:
                return (True, n)
        for n in self.neighbours[ant_loc]:
            if ants.passable(n) and n not in self.orders:
                for hill_loc, owner in ants.hill_list.items():
                    if ants.distance(ant_loc, hill_loc) < 10 and self.tiles[n] == EQUAL:
                        return (True, n)
                        
                    
        return (False, (0, 0))
        

    def find_path(self, ants, start, end):
        parents = {}
        costs = {}
        openlist = binaryheap.BinaryHeap(costs)
        closedlist = set([])
        costs[start] = ants.distance(start, end)
        openlist.insert(start)
        directions = ('n', 'e', 's', 'w')

        success = False
        complete = False

        n = None

 
        while not complete:
            lastN = n
            n = openlist.extractminimum()
            if n and not success:
                closedlist.add(n)
                if n == end:
                    success = True
                else:
                    for new_n in self.neighbours[n]:
                        self.__addtoopenlist__(n, new_n, 1, end, parents, openlist, closedlist, costs, ants)

            if (not n) or success:
                complete = True

        returnpath = []
        n = end
        if success:
            while n != start:
                returnpath.append(n)
                n = parents[n]
            returnpath.append(start)
            returnpath.reverse()    
    
            return returnpath


        return []
                    


    def __addtoopenlist__(self, nodefrom, nodeto, additionalcost, end, parents, openlist, closedlist, costs, ants):

        if (not ants.passable(nodeto)) or nodeto in closedlist:
            return
        if nodeto not in self.visible:
            return

  
        if not nodeto in costs:
            costs[nodeto] = costs[nodefrom] - ants.distance(nodefrom, end) + additionalcost + ants.distance(nodeto, end)
            parents[nodeto] = nodefrom
            openlist.insert(nodeto)
        elif costs[nodeto] - ants.distance(nodeto, end) > costs[nodefrom] - ants.distance(nodefrom, end) + additionalcost:
            costs[nodeto] = costs[nodefrom] - ants.distance(nodefrom, end) + additionalcost + ants.distance(nodeto, end)
            parents[nodeto] = nodefrom
            openlist.fix(nodeto)
        
        
                
        
    def __cost__(self, start, end):
        return ants.distance(start, end)


    def valid_path(self, ants, path):        
        if len(path) <= 1:
            return False
        elif not ants.passable(path[-1]):
            return False
        elif path[0] not in self.my_ants:
            return False

        return True

    def distance(self, loc1, loc2):
        return math.sqrt((loc1[0] - loc2[0]) * (loc1[0] - loc2[0]) + (loc1[1] - loc2[1]) * (loc1[1] - loc2[1]))

    def calculate_influence(self, ants):
        influence = {}
        total = {}
        for row in range(ants.rows):
            for col in range(ants.cols):
                loc = (row, col)
                total[loc] = 0
                

        all_ants = list(ants.ant_list.items())
        owners = set([])

        for ant, owner in all_ants:
            owners.add(owner)
            if owner not in influence:
                influence[owner] = {}
                
            possible_moves = list(self.neighbours[ant])
            possible_moves.append(ant)
            influenced = set([])
            for ant_loc in possible_moves:
                open_list = deque([ant_loc])
                marked = set([ant_loc])
                while len(open_list):
                    loc = open_list.popleft()
                    influenced.add(loc)
                    for n in self.neighbours[loc]:
                        if n not in marked and self.distance(ant_loc, n) <= ants.attackradius2 / 2.:
                            marked.add(n)
                            open_list.append(n)

            for loc in influenced:
                if loc not in influence[owner]:
                    influence[owner][loc] = 0
                influence[owner][loc] += 1
                total[loc] += 1
        self.enemies = {}
        for owner in owners:
            self.enemies[owner] = {}
            for row in range(ants.rows):
                for col in range(ants.cols):
                    loc = (row, col)                    
                    self.enemies[owner][loc] = total[loc]
                    if owner in influence and loc in influence[owner]:
                        self.enemies[owner][loc] -= influence[owner][loc]

        self.fighting = {}
        bazinga = set([])
        for ant_loc in ants.my_ants():
            bazinga.add(ant_loc)
            for n in self.neighbours[ant_loc]:
                bazinga.add(n)
        for some_loc in bazinga:            
            for foe_loc, owner in all_ants:
                possible_moves = list(self.neighbours[foe_loc])
                possible_moves.append(foe_loc)
                max_enemies = 0
                for enemy_loc in possible_moves:
                    if owner != MY_ANT and self.distance(some_loc, enemy_loc) <= ants.attackradius2 / 2.:
                        if self.enemies[owner][enemy_loc] > max_enemies:
                            max_enemies = self.enemies[owner][enemy_loc]
                if max_enemies > 0 and (some_loc not in self.fighting or max_enemies < self.fighting[some_loc]):
                    self.fighting[some_loc] = self.enemies[owner][enemy_loc]
            if some_loc not in self.fighting:
                self.fighting[some_loc] = 0

        self.tiles = {}
       
        for loc in bazinga:
            if self.enemies[MY_ANT][loc] < self.fighting[loc]:
                if self.enemies[MY_ANT][loc] > 0:
                    self.tiles[loc] = KILL
                else:
                    self.tiles[loc] = SAFE
            elif self.enemies[MY_ANT][loc] == self.fighting[loc]:
                if self.fighting[loc] == 0:
                    self.tiles[loc] = SAFE
                else:
                    self.tiles[loc] = EQUAL
            else:
                self.tiles[loc] = DIE

    def do_turn(self, ants):
        self.recalculate_scents(ants)
        self.calculate_influence(ants)

        self.my_ants = set(ants.my_ants())
        self.orders = set([])
        self.incoming = {}
        self.outgoing = {}

        self.paths = [path for path in self.paths if self.valid_path(ants, path)]

        targets = set([])
        busy_ants = set([])
        for path in self.paths:
            if len(path) > 1:
                targets.add(path[-1])
                busy_ants.add(path[0])

        for ant_loc in self.my_ants:
            if ant_loc not in busy_ants:
                foods = []
                for food_loc in ants.food():
                    if food_loc not in targets:
                        dist = ants.distance(ant_loc, food_loc)
                        foods.append((dist, food_loc))
                foods.sort()

                for dist, food_loc in foods:
                    path = self.find_path(ants, ant_loc, food_loc)
                    if len(path) > 0:
                        self.paths.append(path)
                        busy_ants.add(ant_loc)
                        targets.add(food_loc)
                        break

        for ant_loc in self.my_ants:
            if ant_loc not in busy_ants:
                path = self.find_goal(ants, ant_loc, 'hills')
                if len(path) > 1:
                    self.paths.append(path)
                else:
                    path = self.find_goal(ants, ant_loc, 'enemy')
                    if len(path) > 1:
                        self.paths.append(path)
                    else:
                        path = self.find_goal(ants, ant_loc, 'explore')
                        if len(path) > 1:
                            self.paths.append(path)

        for path in self.paths:
            self.make_move(ants, path)

        assigned = set([])
        for path in self.paths:
            assigned.add(path[0])
        self.standing = []
        for ant_loc in self.my_ants:
            if ant_loc not in assigned:
                self.standing.append(ant_loc)
                #self.paths.append([ant_loc, ant_loc])
                #self.orders.add(ant_loc)

        for path in self.paths:
            if len(path) > 1 and path[1] in self.outgoing and self.outgoing[path[1]] == path[0]:
                for p in self.incoming[path[0]]:
                    if path[1] == p[0]:
                        path.pop(0)
                        p.pop(0)
                        break
            
        self.topological_sort(ants)
        print "hill scent: " + str(self.agents['hills'][(47, 24)])
        print "left time: " + str(ants.time_remaining())

            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(roboboogie())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
