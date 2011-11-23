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
        self.peasants = []
        self.targets = set([])
        self.ordered = set([])
        self.paths = []
        self.reachable = set(ants.my_hills())
        
        self.border = []

        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))        
        
    

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
            self.paths.append(returnpath)
            return True

        return False
                    
                    

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
                        path.pop(0)                
                        mademoves.add(path[0])
                    else:
                        dest = ants.destination(path[0], dir)

                        for p in self.paths:
                            if p[0] not in mademoves and path[0] and p[0] == dest and p[1] == path[0]:
                                p.pop(0)
                                path.pop(0)
                                mademoves.add(p[0])
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


    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):

        self.orders = {}
        self.ordered = set([])        



        for path in self.paths:
            if len(path) <= 1:
                self.paths.remove(path)
            elif not ants.passable(path[-1]):
                self.paths.remove(path)
            elif path[0] not in ants.my_ants():
                self.paths.remove(path)


        tar = set([])
        busy_ants = set([])
        for path in self.paths:
            tar.add(path[-1])
            busy_ants.add(path[0])


        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.seen.add(loc)
                self.unseen.remove(loc)

        self.compute_border(ants)

        #for hill_loc, hill_owner in ants.enemy_hills():
        #    if hill_loc not in self.hills:
        #        ant = random.choice(ants.my_ants())
        #        if self.do_move_location(ants, ant, hill_loc):
        #            busy_ants = []
        #            paths = []
        #            self.hills.append(hill_loc)
 #       ant_dist = []
 #       for hill_loc in self.hills:
 #               for ant_loc in ants.my_ants():
 #                   if ant_loc not in busy_ants:
 #                       if self.do_move_location(ants, ant_loc, hill_loc):                            
 #                           busy_ants.add(ant_loc)
 #                           tar.add(hill_loc)
 #                           break
                        

        for food_loc in ants.food():
            if food_loc not in tar and food_loc in self.reachable:                
                for ant_loc in ants.my_ants():
                    if ant_loc not in busy_ants:
                        if self.do_move_location(ants, ant_loc, food_loc):
                            busy_ants.add(ant_loc)
                            tar.add(food_loc)
                            break
          

        
        for ant_loc in ants.my_ants():            
            if ant_loc not in busy_ants:
                unseen_dist = []
                for unseen_loc in self.border:
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                unseen_dist.sort()                
                for dist, unseen_loc in unseen_dist:
                    if unseen_loc not in tar and self.do_move_location(ants, ant_loc, unseen_loc):
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
