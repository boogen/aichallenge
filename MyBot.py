#!/usr/bin/env python
from ants import *
from collections import deque
from sets import Set


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
        self.unseen = []
        self.peasants = []
        self.targets = set([])
        self.ordered = set([])
        self.paths = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
    

    def do_move_location(self, ants, loc, dest):
        parents = {}
        queue = deque([])
        queue.append(loc)
        parents[loc] = loc
        visited = set([loc])
        directions = ('n', 'e', 's', 'w')

        while len(queue) > 0:
            node = queue.popleft()         
            if node == dest:
                path = []
                start = node
                path.append(start)
                while parents[start] != loc:
                    path.append(parents[start])
                    start = parents[start]

                path.append(loc)
                path.reverse()
                self.paths.append(path)                            
                return True

            for direction in directions:
                new_loc = ants.destination(node, direction)                    
                if ants.passable(new_loc) and new_loc not in visited:
                    visited.add(new_loc)
                    parents[new_loc] = node
                    queue.append(new_loc)                        

        return False

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
        for path in self.paths:
            if len(path) > 1:                    
                dirs = ants.direction(path[0], path[1])
                for dir in dirs:
                    if self.do_move_direction(ants, path[0], dir):
                        path.pop(0)
                        break
                    else:
                        self.paths.remove(path)
                        break
                            
    

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        self.orders = {}
        self.ordered = set([])        

        for path in self.paths:
            if len(path) <= 1:
                self.paths.remove(path)
            elif path[-1] not in ants.food():
                self.paths.remove(path)



        tar = set([])
        busy_ants = set([])
        for path in self.paths:
            tar.add(path[-1])
            busy_ants.add(path[0])


        for food_loc in ants.food():
            if food_loc not in tar:                
                for ant_loc in ants.my_ants():
                    if ant_loc not in busy_ants:
                        if self.do_move_location(ants, ant_loc, food_loc):
                            busy_ants.add(ant_loc)
                            tar.add(food_loc)
                            break

   
          
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        ant_dist = []
        for hill_loc in self.hills:
            if hill_loc not in tar:
                for ant_loc in ants.my_ants():
                    if ant_loc not in busy_ants:
                        if self.do_move_location(ants, ant_loc, hill_loc):                            
                            busy_ants.add(ant_loc)
                            tar.add(hill_loc)
                            break
                        

        
        
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.unseen.remove(loc)
        for ant_loc in ants.my_ants():            
            if ant_loc not in busy_ants:
                unseen_dist = []
                for unseen_loc in self.unseen:
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
