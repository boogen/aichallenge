#!/usr/bin/env python
from ants import *
from collections import deque
from sets import Set
import binaryheap
import math
import random

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        self.hills = []
        # initialize data structures after learning the game settings
        self.seen = set([])
        self.unseen = []
        self.roles = {'peasants':set([]), 'guards':set([]), 'knights':set([])}
        self.targets = set([])
        self.ordered = set([])
        self.paths = []
        self.reachable = set(ants.my_hills())
        self.weights = {}

        self.border = []
        self.crosses = []

 
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))        

        
    
    def __add_path__(self, path):
        if len(self.roles['peasants']) < 50:
            self.roles['peasants'].append(path)
        

    def do_move_location(self, ants, start, end, weight):
        if ants.time_remaining() < 0.5 * ants.turntime:
            return []

        parents = {}
        costs = {}
        openlist = binaryheap.BinaryHeap(costs)
        closedlist = set([])
        costs[start] = self.__cost__(start, end)
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
                    for direction in directions:
                        new_n = ants.destination(n, direction)   
                        self.__addtoopenlist__(n, new_n, 1, end, parents, openlist, closedlist, costs, ants, weight)

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
                    


    def __addtoopenlist__(self, nodefrom, nodeto, additionalcost, end, parents, openlist, closedlist, costs, ants, weight):

        if nodeto not in self.reachable:
            return       
  
        if self.weights[nodeto] < weight:
            return

        if (not ants.passable(nodeto)) or nodeto in closedlist:
            return

  
        if not nodeto in costs:
            costs[nodeto] = costs[nodefrom] - self.__cost__(nodefrom, end) + additionalcost + self.__cost__(nodeto, end)
            parents[nodeto] = nodefrom
            openlist.insert(nodeto)
        elif costs[nodeto] - self.__cost__(nodeto, end) > costs[nodefrom] - self.__cost__(nodefrom, end) + additionalcost:
            costs[nodeto] = costs[nodefrom] - self.__cost__(nodefrom, end) + additionalcost + self.__cost__(nodeto, end)
            parents[nodeto] = nodefrom
            openlist.fix(nodeto)
        
        
                
        
    def __cost__(self, start, end):
        dx = math.fabs(end[0] - start[0])
        dy = math.fabs(end[1] - start[1])
        return dx + dy


    def do_move_direction(self, ants, loc, direction):
        new_loc = ants.destination(loc, direction)
        if (new_loc not in self.orders):
            ants.issue_order((loc, direction))
            self.orders[new_loc] = loc
            self.ordered.add(loc)

            for name, role in self.roles.iteritems():
                if loc in role:
                    role.remove(loc)
                    role.add(new_loc)
            
            return True
        else:
            return False

    def make_moves(self, ants):
        mademoves = set([])

        outgoing = {}
        incoming = {}

        L = deque([])
        sorted = []
        cycles = []
        
        for path in self.paths:
            if len(path) > 1:
                outgoing[path[0]] = path[1]
                if path[1] not in incoming:
                    incoming[path[1]] = []
                incoming[path[1]].append(path)
        
        for path in self.paths:
            if len(path) > 1:
                if path[1] in outgoing and outgoing[path[1]] == path[0]:
                    cycles.append(path)
    
        
        for path in self.paths:
            if len(path) > 1:
                if path[1] not in outgoing:
                    L.append(path)
        marked = set([])
        while len(L):
            path = L.popleft()
            if path[0] not in marked:
                marked.add(path[0])
                sorted.append(path)
                if path[0] in incoming:
                    for p in incoming[path[0]]:
                        if p != path:
                            L.append(p)
 


        for path in cycles:
            if self.uncycle(path, incoming, mademoves):
                break


        for path in sorted:
            dir = ants.direction(path[0], path[1])[0]
            if self.do_move_direction(ants, path[0], dir):
                self.move_ant(path, path[1], mademoves)
        
        return
                
    def uncycle(self, path, incoming, mademoves):
        if len(path) > 1:
            p = path
            marked = []
            good_paths = [p]
            while p[0] in incoming and len(good_paths) > 0:                         
                good_paths = []
                for some_path in incoming[p[0]]:
                    if path[0] in some_path and some_path[0] in path and some_path != path:
                        good_paths.append(some_path)
                if len(good_paths) > 0:                                    
                    p = good_paths[0]
            if len(p) > 1 and p != path:
                self.move_ant(path, p[0], mademoves)
                self.move_ant(p, path[0], mademoves)     
                return True
        
    def switch_roles(self, loc1, loc2):
        role1 = None
        role2 = None
        for name, role in self.roles.iteritems():
            if loc1 in role:
                role1 = role
            if loc2 in role:
                role2 = role

        if role1 != role2:
            role1.remove(loc1)
            role1.add(loc2)
            role2.remove(loc2)
            role2.add(loc1)
                            
    def shift_move(self, path, loc):
        path.insert(0, loc)

    def move_ant(self, path, loc,  mademoves):
        while path[0] != loc:
            path.pop(0)
        mademoves.add(path[0])
                                                                 
 
    def compute_border(self, ants):
        if len(self.border) == 0:            
            self.border = list(ants.my_hills())
            self.reachable = set(ants.my_hills())
            for hill_loc in ants.my_hills():
                self.weights[hill_loc] = 3


        changed = True

        i = 0
        while changed:            
            open_list = []
            changed = False            
            for loc in self.border:
                not_seen_neighbour = False
                for dir in ('n', 'e', 's', 'w'):
                    n = ants.destination(loc, dir)
                    if n not in self.seen:
                        not_seen_neighbour = True
                    elif n not in self.reachable:
                        if ants.passable(n):
                            changed = True
                            self.reachable.add(n)
                            open_list.append(n)
                            if n not in self.weights:
                                self.weights[n] = 3
                        else:
                            self.weights[n] = 0
                            for d in ['n', 'e', 's', 'w']:
                                self.weights[ants.destination(n, d)] = 1
                                        
                                
                                
                if not_seen_neighbour:
                    open_list.append(loc)
            if changed:
                self.border = list(open_list)
  

      
            

    def find_cross(self, ants, pos):
        return [(52, 32), (51,33), (52, 33), (53, 33), (52, 34)]
        standing_ants = set([])
        for path in self.paths:
            if len(path) == 1:
                standing_ants.add(path[0])

        directions = ['n', 'w', 's', 'e']
        marked = set([])
        openlist = deque(ants.my_hills())
        while len(openlist):
            loc = openlist.popleft()
            marked.add(loc)
            cross = [loc]
            for dir in directions:
                n_loc = ants.destination(loc, dir)
                cross.append(n_loc)
                if n_loc in self.reachable and n_loc not in marked:
                    openlist.append(n_loc)
            ok = True
            for node in cross:
                if node not in self.reachable or node in ants.my_hills() or node in standing_ants:
                    ok = False
                    break
            if ok:
                return cross
                 
        return []        
        
            
    def valid_path(self, ants, path):
        if len(path) == 0:
            return False
        elif path[0] not in self.my_ants:
            return False

        return True
 
    def append_path(self, path):
        for p in self.paths:
            if p[0] == path[0]:
                self.paths.remove(p)
                break
        if path[0] in self.roles['knights']:            
            self.paths.insert(0, path)
        else:
            self.paths.append(path)

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        self.time = 0
        self.my_ants = set(ants.my_ants())
        
        self.orders = {}
        self.ordered = set([])        


        self.paths = [path for path in self.paths if self.valid_path(ants, path)]
        for name, role in self.roles.iteritems():
            dead_ants = set([])
            for loc in role:
                if loc not in self.my_ants:
                    dead_ants.add(loc)
            role -= dead_ants
                    

        tar = set([])
        busy_ants = set([])
        waiting_ants = set([])
        for path in self.paths:
            if len(path) > 1:
                tar.add(path[-1])
                busy_ants.add(path[0])
            elif len(path) == 1:
                waiting_ants.add(path[0])



        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.seen.add(loc)
                self.unseen.remove(loc)

        self.compute_border(ants)
        
        for ant_loc in self.my_ants:
            have_role = False
            for name, role in self.roles.iteritems():
                if ant_loc in role:
                    have_role = True
                    break

            if not have_role:
#                if (len(self.roles['peasants']) < 4 or len(self.roles['peasants']) < 0.5 * len(self.my_ants)):
#                if len(self.my_ants) % 3 != 0:                    
                self.roles['peasants'].add(ant_loc)                
#                else:
#                    self.roles['knights'].add(ant_loc)
#                    if len(self.roles['knights']) % 5 == 1:
#                        cross = self.find_cross(ants, ants.my_hills()[0])
#                        print "cross: " + str(cross)
#                        self.crosses.append(cross)
                    
                    
                        
        for ant_loc in self.roles['knights']:
            if ant_loc not in busy_ants and ant_loc not in waiting_ants:
                reminder = len(self.roles['knights']) % 5
                cross = self.crosses[-1]
                path = self.do_move_location(ants, ant_loc, cross[reminder], 1)
                if len(path) > 0:
                    self.append_path(path)
                    busy_ants.add(ant_loc)
                    tar.add(cross[reminder])
                    
        if len(self.crosses):
            cross = self.crosses[-1]
            ready = True
            for loc in cross:
                if loc not in self.roles['knights']:
                    ready = False
            if ready:
                loc = random.choice(self.border)
                path = self.do_move_location(ants, cross[2], loc, 3)
                if len(path) > 0:
#                    self.append_path(path)
                    for dir in ['w', 'n', 'c', 's', 'e']:
                        if dir == 'c':
                            self.append_path(path)
                        else:
                            new_path = []
                            for n in path:
                                new_path.append(ants.destination(n, dir))
                            self.append_path(new_path)

                    self.crosses.pop()
            


        for ant_loc in self.roles['peasants']:
            if ant_loc not in busy_ants:
                foods = []
                for food_loc in ants.food():
                    if food_loc not in tar and food_loc in self.reachable:
                        dist = ants.distance(ant_loc, food_loc)
                        foods.append((dist, food_loc))
                foods.sort()
                for dist, food_loc in foods:
                    path = self.do_move_location(ants, ant_loc, food_loc, 1)
                    if len(path) > 0:
                        self.append_path(path)
                        busy_ants.add(ant_loc)
                        tar.add(food_loc)
                        break
  
 
        random.shuffle(self.border)
        for ant_loc in self.roles['peasants']:            
            if ant_loc not in busy_ants:
                for unseen_loc in self.border:
                    if unseen_loc not in tar:
                        path = self.do_move_location(ants, ant_loc, unseen_loc, 1)
                        if len(path) > 0:
                            self.append_path(path)
                            busy_ants.add(ant_loc)
                            tar.add(unseen_loc)
                            break                

        self.make_moves(ants)


    
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
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
