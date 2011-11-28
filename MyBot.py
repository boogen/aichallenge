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
        
        self.border = []
        self.crosses = []

        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))        

        self.delme = [[(51, 37), (51, 36)], [(51, 37), (52, 37)], [(51, 37), (51, 38)], [(51, 37), (51, 36), (51, 35)], [(51, 37), (52, 37), (53, 37)], [(51, 37), (51, 38), (51, 39)]]
        
    
    def __add_path__(self, path):
        if len(self.roles['peasants']) < 50:
            self.roles['peasants'].append(path)
        

    def do_move_location(self, ants, start, end):
        if ants.time_remaining() < 0.25 * ants.turntime:
            return False

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
        
  
        if nodeto not in self.reachable:
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
        if (ants.unoccupied(new_loc) and new_loc not in self.orders):
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
        for path in self.paths:
            if path[0] not in mademoves:
                if len(path) > 1:                    
                    dir = ants.direction(path[0], path[1])[0]
                    if self.do_move_direction(ants, path[0], dir):   
                        self.move_ant(path, mademoves)
                    else:
                        for p in self.paths:
                            if p[0] == path[1] and p[0] not in mademoves:
                                if len(p) > 1:
                                    if p[1] == path[0]:                                        
                                        self.move_ant(path, mademoves)
                                        self.move_ant(p, mademoves)                                        
                                        break
                                elif path[-1] != p[0]:            
                                    self.switch_roles(path[0], p[0])
                                    self.shift_move(p, path[0])
                                    self.move_ant(path, mademoves)
                                    break
                
       
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

    def move_ant(self, path, mademoves):
        path.pop(0)
        mademoves.add(path[0])
                                                                 
 
    def compute_border(self, ants):
        if len(self.border) == 0:            
            self.border = list(ants.my_hills())
            self.reachable = set(ants.my_hills())


        changed = True

        while changed:
            open_list = []
            changed = False            
            for loc in self.border:
                not_seen_neighbour = False
                for dir in ('n', 'e', 's', 'w'):
                    n = ants.destination(loc, dir)
                    if n not in self.seen:
                        not_seen_neighbour = True
                    elif n not in self.reachable and ants.passable(n):
                        changed = True
                        self.reachable.add(n)
                        open_list.append(n)
                if not_seen_neighbour:
                    open_list.append(loc)
            self.border = list(open_list)

    def find_cross(self, ants, pos):
        ok = False
        directions = ['n', 'w', 's', 'e']
        hills = ants.my_hills()
        while not ok:
            ok = True
            cross = [pos] 
            if not ants.passable(pos) and p not in hills:
                ok = False
                pos = ants.destination(pos, random.choice(directions))
            else:

                for i in range(0, 4):
                    p = ants.destination(pos, directions[i])
                    if ants.passable(p) and p not in hills:
                        cross.append(p)
                    else:
                        pos = ants.destination(pos, directions[3 - i])
                        ok = False
                        break
            
        
        return cross

        
            
            

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):

        self.orders = {}
        self.ordered = set([])        



        for path in self.paths:
            if len(path) == 0:
                self.paths.remove(path)


        tar = set([])
        busy_ants = set([])
        for path in self.paths:
            if len(path) > 1:
                tar.add(path[-1])
                busy_ants.add(path[0])


        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.seen.add(loc)
                self.unseen.remove(loc)

        self.compute_border(ants)
        
        for ant_loc in ants.my_ants():
            have_role = False
            for name, role in self.roles.iteritems():
                if ant_loc in role:
                    have_role = True
                    break

            if not have_role:
#                if (len(self.roles['peasants']) < 4 or len(self.roles['peasants']) < 0.5 * len(ants.my_ants())):
                if len(ants.my_ants()) % 2 == 1:                    
                    self.roles['peasants'].add(ant_loc)                
                else:
                    self.roles['knights'].add(ant_loc)
                    if len(self.roles['knights']) % 5 == 1:
                        cross = self.find_cross(ants, ants.my_hills()[0])
                        print "cross " + str(cross)
                        self.crosses.append(cross)
                    
                    
                        
        for ant_loc in self.roles['knights']:
            if ant_loc not in busy_ants:
                reminder = len(self.roles['knights']) % 5
                cross = self.crosses[-1]
                path = self.do_move_location(ants, ant_loc, cross[reminder])
                if len(path) > 0:
                    self.paths.append(path)
                    busy_ants.add(ant_loc)
                    tar.add(cross[reminder])
                    
                        

        for ant_loc in self.roles['peasants']:
            if ant_loc not in busy_ants:
                foods = []
                for food_loc in ants.food():
                    if food_loc not in tar and food_loc in self.reachable:
                        dist = ants.distance(ant_loc, food_loc)
                        foods.append((dist, food_loc))
                foods.sort()
                for dist, food_loc in foods:
                    path = self.do_move_location(ants, ant_loc, food_loc)
                    if len(path) > 0:
                        self.paths.append(path)
                        busy_ants.add(ant_loc)
                        tar.add(food_loc)
                        break
  
 

        for ant_loc in self.roles['peasants']:            
            if ant_loc not in busy_ants:
                for unseen_loc in self.border:
                    if unseen_loc not in tar:
                        path = self.do_move_location(ants, ant_loc, unseen_loc)
                        if len(path) > 0:
                            self.paths.append(path)
                            busy_ants.add(ant_loc)
                            tar.add(unseen_loc)
                            break                

        self.make_moves(ants)

        return

        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in self.orders.values():
                for direction in ('s', 'e', 'w', 'n'):
                    if self.do_move_direction(ants, hill_loc, direction):
                        break

        
    
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
