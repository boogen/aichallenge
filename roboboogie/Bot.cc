#include "Bot.h"
#include <queue>
#include <algorithm>
#include <cmath>
using namespace std;

//constructor
Bot::Bot()
{

};

//plays a single game of Ants.
void Bot::playGame()
{
    //reads the game parameters and sets up
    cin >> state;
    state.setup();
    endTurn();
    do_setup();
    //continues making moves while the game is not over
    while(cin >> state)
    {
        state.updateVisionInformation();

        do_turn();
        endTurn();
    }
}

void Bot::bfs(std::vector<point>& start_list, int type) {
  std::set<point> marked;
  std::queue<point> open_list;

  for (size_t i = 0; i < start_list.size(); ++i) {
    marked.insert(start_list.at(i));
    open_list.push(start_list.at(i));
  }

  double scent = 1.0;
  while (!open_list.empty()) {
    point loc = open_list.front();
    open_list.pop();
    
    if (type == HILLS) {
      scent = diffuse_hills(loc);
    }
    else if (type == ENEMIES) {
      scent = diffuse_ants(loc);
    }
    else if (type == EXPLORE) {
      scent = diffuse_explore(loc);
    }
    //    std::map<std::pair<int, int>, std::vector<std::pair<int, int> > >::iterator it = neighbours.find(loc);
    if (scent >= 1) {
      for (size_t i = 0; i < 4; ++i) {
	Location _loc = state.getLocation(Location(loc.first, loc.second), i);
	point new_loc(_loc.row, _loc.col);
	if (marked.find(new_loc) == marked.end()) {
	  open_list.push(new_loc);
	  marked.insert(new_loc);
	}
      }
    }
  }
}

void Bot::recalculate_scents() {
  clear();


  m_enemy_hills.clear();
  std::vector<point> enemy_hills;
  for (size_t i = 0; i < state.enemyHills.size(); ++i) {
    point loc(state.enemyHills.at(i).row, state.enemyHills.at(i).col);
    enemy_hills.push_back(loc);
    m_enemy_hills.insert(loc);
  }

  bfs(enemy_hills, HILLS);

  m_enemy_ants.clear();
  std::vector<point> enemy_ants;
  for (size_t i = 0; i < state.enemyAnts.size(); ++i) {
    point loc(state.enemyAnts.at(i).row, state.enemyAnts.at(i).col);
    enemy_ants.push_back(loc);
    m_enemy_ants.insert(loc);
  }

  bfs(enemy_ants, ENEMIES);

  std::vector<point> unseen;
  for (size_t i = 0; i < state.grid.size(); ++i) {
    for (size_t j = 0; j < state.grid.at(i).size(); ++j) {
      std::pair<int, int> loc(i, j);
      int v = state.grid.at(i).at(j).isVisible; 
      if (v == 0 && passable(loc)) {
	for (size_t k = 0; k < neighbours.at(loc).size(); ++k) {
	  point n = neighbours.at(loc).at(k);
	  if (state.grid.at(n.first).at(n.second).isVisible > 0) {
	    unseen.push_back(loc);
	    break;
	  }
	}
      }
    }
  }
  bfs(unseen, EXPLORE);
}

double Bot::diffuse_hills(point loc) {
  if (passable(loc) == 0) {
    agents.at("hills")->at(loc.first).at(loc.second) = 0;
    return 0;
  }

  if (state.grid.at(loc.first).at(loc.second).isVisible == 0) {
    agents.at("hills")->at(loc.first).at(loc.second) = 0;
    return 0;
  }

  if (m_enemy_hills.find(loc) != m_enemy_hills.end()) {
    agents.at("hills")->at(loc.first).at(loc.second) = max_value;
    return max_value;
  }
  else {
    return diffuse(loc, "hills");
  }
}

double Bot::diffuse_ants(point loc) {
  if (passable(loc) == 0) {
    agents.at("enemy")->at(loc.first).at(loc.second) = 0;
    return 0.;
  }
  if (state.grid.at(loc.first).at(loc.second).isVisible == 0) {
    agents.at("enemy")->at(loc.first).at(loc.second) = 0;
    return 0.;
  }

  if (m_enemy_ants.find(loc) != m_enemy_ants.end()) {
    agents.at("enemy")->at(loc.first).at(loc.second) = max_value;
    return max_value;
  }
  else {
    return diffuse(loc, "enemy");
  }
}

double Bot::diffuse_explore(point loc) {
  if (passable(loc) == 0) {
    agents.at("explore")->at(loc.first).at(loc.second) = 0;
    return 0.;
  }

  /*  if (state.grid.at(loc.first).at(loc.second).ant >= 0) {
    agents.at("explore")->at(loc.first).at(loc.second) = 0;
    return 0.;
    }*/
  if (state.grid.at(loc.first).at(loc.second).isVisible == 0) {
    agents.at("explore")->at(loc.first).at(loc.second) = max_value; // - last_seen.at(loc.first).at(loc.second);
    return  max_value - last_seen.at(loc.first).at(loc.second);
  }
  else {
    return diffuse(loc, "explore");
  }
}

double Bot::diffuse(point loc, std::string goal) {
  double value = 0;

  for (size_t i = 0; i < 4; ++i) {
    Location _loc = state.getLocation(Location(loc.first, loc.second), i);
    point n(_loc.row, _loc.col);
    value += 0.25 * agents.at(goal)->at(n.first).at(n.second);
  }
  agents.at(goal)->at(loc.first).at(loc.second) = value;
  return value;
}

std::vector<point>* Bot::find_goal(point ant_loc, std::string goal) {
  double maximum = 0;
  point dest = ant_loc;
  for (size_t k = 0; k < neighbours.at(ant_loc).size(); ++k) {
    point neighbour = neighbours.at(ant_loc).at(k);  
    if (agents.at(goal)->at(neighbour.first).at(neighbour.second) > maximum) {
      maximum = agents.at(goal)->at(neighbour.first).at(neighbour.second);
	 dest = neighbour;
    }
  }  
  std::vector<point>* result = new std::vector<point>();
  result->push_back(ant_loc);
  if (dest != ant_loc) {
	result->push_back(dest);
  }
	
  return result;
  
}

void Bot::make_move(std::vector<point>* path) {
  if (path->size() > 1) {
    if (incoming.find(path->at(1)) == incoming.end()) {
      incoming.insert(std::make_pair(path->at(1), std::vector<std::vector<point>* >()));
    }
    incoming[path->at(1)].push_back(path);
    outgoing[path->at(0)] = path->at(1);
  }

}

void Bot::issue_order(point start, point end) {
	Location from(start.first, start.second);
	
        for(int d=0; d<TDIRECTIONS; d++)
        {
	  Location loc = state.getLocation(from, d);
	  if (loc.row == end.first && loc.col == end.second) {	    
	    state.makeMove(from, d);
	    return;
	  }
	}
}

void Bot::topological_sort() {
  orders.clear();

  std::queue<std::vector<point>*> L;
  std::set<point> marked;
  for (size_t i = 0; i < paths.size(); ++i) {
    std::vector<point>* path = paths.at(i);
    std::map<point, point>::iterator it = outgoing.find(path->at(0));
    if (it != outgoing.end() && outgoing.find(it->second) == outgoing.end()) {
      L.push(path);
      marked.insert(path->at(0));
    }
  }

  std::vector<std::vector<point>*> sorted;
  
  while (!L.empty()) {
    std::vector<point>* path = L.front();
    L.pop();
    sorted.push_back(path);
    std::map<point, std::vector<std::vector<point>* > >::iterator it = incoming.find(path->at(0));
    if (it != incoming.end()) {
      for (size_t i = 0; i < it->second.size(); ++i) {
	std::vector<point>* p = it->second.at(i);
	if (marked.find(p->at(0)) == marked.end() && p != path) {
	  L.push(p);
	  marked.insert(p->at(0));
	}
      }
    }
  }
  
  int actions[3] = {KILL, SAFE, EQUAL};
  for (size_t i = 0; i < standing.size(); ++i) {   
    std::pair<bool, point> action = std::make_pair(false, standing.at(i));
    for (size_t j = 0; j < sizeof(actions) / sizeof(int) && !action.first; ++j) {
      action = try_action(standing.at(i), actions[j]);
      if (action.first) {
	orders.insert(action.second);
	issue_order(standing.at(i), action.second);
      }
    }
  }

  for (size_t i = 0; i < sorted.size(); ++i) {
    std::vector<point>* path = sorted.at(i);
    if (path->size() > 1) {
      std::pair<bool, point> action = try_action(path->at(0), KILL);
      
      if (action.first) {
	orders.insert(action.second);
	issue_order(path->at(0), action.second);
	if (path->at(1) == action.second) {
	  path->erase(path->begin());
	}
      }
      else if (tiles[path->at(1)] == SAFE && orders.find(path->at(1)) == orders.end()) {
	orders.insert(path->at(1));
	issue_order(path->at(0), path->at(1));
	path->erase(path->begin());
      }
      else {
	int actions[2] = {SAFE, EQUAL};
	
	for (size_t j = 0; j < sizeof(actions) / sizeof(int) && !action.first; ++j) {
	  action = try_action(path->at(0), actions[j]);
	  if (action.first) {
	    orders.insert(action.second);
	    issue_order(path->at(0), action.second);
	    if (path->at(1) == action.second) {
	      path->erase(path->begin());
	    }
	  }
	}
      }
    }
  }
  
}

std::pair<bool, point> Bot::try_action(point ant_loc, int action) {
  std::vector<point> possible_moves = neighbours.at(ant_loc);
  possible_moves.push_back(ant_loc);
  
  if (action != KILL) {
    for (size_t k = 0; k < possible_moves.size(); ++k) {
      point n = possible_moves.at(k);  
      if (passable(n) == 1 && orders.find(n) == orders.end() && tiles[n] == action) {
	return std::make_pair(true, n);
      }
    }
  }
  else {
    std::vector<std::pair<double, point> > good_moves;
    for (size_t k = 0; k < possible_moves.size(); ++k) {
      point n = possible_moves.at(k);  
      if (passable(n) == 1 && orders.find(n) == orders.end() && tiles[n] == action) {
	good_moves.push_back(std::make_pair(closest_enemy[n], n));
      }
    }    

    if (good_moves.size()) {
      std::sort(good_moves.begin(), good_moves.end());
      return std::make_pair(true, good_moves.at(0).second);
    }
  }

  return std::make_pair(false, ant_loc);
}


void Bot::do_setup() {
  agents.insert(std::make_pair("explore", new std::vector<std::vector<double> >()));
  agents.insert(std::make_pair("hills", new std::vector<std::vector<double> >()));
  agents.insert(std::make_pair("enemy", new std::vector<std::vector<double> >()));

  max_value = 2000000000;
  for (size_t i = 0; i < state.rows; ++i) {
    last_seen.push_back(std::vector<double>());
    total.push_back(std::vector<int>());
    agents["explore"]->push_back(std::vector<double>());
    agents["hills"]->push_back(std::vector<double>());
    agents["enemy"]->push_back(std::vector<double>());
    for (size_t j = 0; j < state.cols; ++j) {
      last_seen.at(i).push_back(0);
      total.at(i).push_back(0);
      agents["explore"]->at(i).push_back(0.);
      agents["hills"]->at(i).push_back(0.);
      agents["enemy"]->at(i).push_back(0.);
    }
  }

  for (size_t i = 0; i < state.rows; ++i) {
    for (size_t j = 0; j < state.cols; ++j) {
      Location loc(i, j);
      std::vector<std::pair<int, int> > nbrs;
      for (size_t k = 0; k < 4; ++k) {
	Location n = state.getLocation(loc, k);
	nbrs.push_back(std::make_pair(n.row, n.col));
      }
      neighbours.insert(std::make_pair(std::make_pair(i, j), nbrs));
     }
  }

}

int Bot::passable(point& loc) {
  return 1 - state.grid.at(loc.first).at(loc.second).isWater;
}

void Bot::clear() {
  for (size_t i = 0; i < state.grid.size(); ++i) {
    for (size_t j = 0; j < state.grid.at(i).size(); ++j) {
      std::pair<int, int> loc(i, j);
       if (state.grid.at(i).at(j).isVisible > 0) {
	 last_seen.at(i).at(j) = max_value;	
      }
       else if (last_seen.at(i).at(j) > 0) {
	last_seen.at(i).at(j) -= 1;
      }
       for (std::map<std::string, std::vector<std::vector<double> >* >::iterator it = agents.begin();
	   it != agents.end(); ++it) {
	 it->second->at(i).at(j) = 0.;
	
       }
    }
  }
}

bool Bot::valid_path(std::vector<point>* path) {
  if (path->size() <= 1) {
    delete path;
    return false;
  }
  if (passable(path->at(path->size() - 1)) == 0) {
    delete path;
    return false;
  }
  if (my_ants.find(path->at(0)) == my_ants.end()) {
    delete path;
    return false;
  }

  return true;
  
}

std::vector<point>* Bot::find_path(point from, point to) {
  std::set<point> marked;
  std::queue<point> open_list;
  std::map<point, point> parent;
  
  marked.insert(from);
  open_list.push(from);

  while (!open_list.empty()) {
    point loc = open_list.front();
    open_list.pop();
    if (loc == to) {
      std::vector<point>* result = new std::vector<point>();
      point p = to;
      while (p != from) {
	result->push_back(p);
	p = parent[p];
      }
      result->push_back(from);
      std::reverse(result->begin(), result->end());
      return result;
    }
    std::map<std::pair<int, int>, std::vector<std::pair<int, int> > >::iterator it = neighbours.find(loc);
    for (size_t i = 0; i < it->second.size(); ++i) {
      point new_loc = it->second.at(i);
      if (state.grid.at(new_loc.first).at(new_loc.second).isVisible == 1  && passable(new_loc) == 1 && marked.find(new_loc) == marked.end()) {
	parent.insert(std::make_pair(new_loc, loc));
	open_list.push(new_loc);
	marked.insert(new_loc);
      }
    }    
  }

  return new std::vector<point>();
}

void Bot::print_path(std::vector<point>* path) {
  state.bug << "path: " << std::endl;
  for (size_t i = 0; i < path->size(); ++i) {
    state.bug << "(" << path->at(i).first << "," << path->at(i).second << ")\n";
  }
}

void Bot::print_loc(point p) {
  state.bug << "(" << p.first << "," << p.second << ")";
}

void Bot::calculate_influence() {
  std::map<int, std::map<point, int> > influence;

  for (size_t i = 0; i < state.grid.size(); ++i) {
    for (size_t j = 0; j < state.grid.at(i).size(); ++j) {
      total.at(i).at(j) = 0;
    }
  }

  std::vector<Location> all_ants = state.enemyAnts;
  for (size_t i = 0; i < state.myAnts.size(); ++i) {
    all_ants.push_back(state.myAnts.at(i));
  }

  std::set<int> owners;

  for (size_t i = 0; i < all_ants.size(); ++i) {
    Location _loc = all_ants.at(i);
    point ant(_loc.row, _loc.col);
    int owner = state.grid.at(_loc.row).at(_loc.col).ant;
    owners.insert(owner);
    if (influence.find(owner) == influence.end()) {
      influence.insert(std::make_pair(owner, std::map<point, int>()));
    }

    std::vector<point> possible_moves = neighbours.at(ant);
    possible_moves.push_back(ant);
    std::set<point> influenced;

    for (size_t j = 0; j < possible_moves.size(); ++j) {
      point ant_loc = possible_moves.at(j);
      std::queue<point> open_list;
      std::set<point> marked;
      open_list.push(ant_loc);
      marked.insert(ant_loc);
      while (!open_list.empty()) {
	point loc = open_list.front();
	open_list.pop();
	influenced.insert(loc);
	for (size_t k = 0; k < neighbours.at(loc).size(); ++k) {
	  point n = neighbours.at(loc).at(k);	
	  if (marked.find(n) == marked.end() && distance(ant_loc, n) <= state.attackradius) {
	    marked.insert(n);
	    open_list.push(n);
	  }
	}
      }
    }

    for (std::set<point>::iterator it = influenced.begin(); it != influenced.end(); ++it) {
      if (influence[owner].find(*it) == influence[owner].end()) {
	influence[owner].insert(std::make_pair(*it, 0));
      }
      influence[owner][*it] += 1;
      total.at((*it).first).at((*it).second) += 1;
    }
  }

  enemies.clear();
  for (std::set<int>::iterator it = owners.begin(); it != owners.end(); ++it) {
    enemies.insert(std::make_pair(*it, std::map<point, int>()));
    for (size_t r = 0; r < state.grid.size(); ++r) {
      for (size_t c = 0; c < state.grid.at(r).size(); ++c) {
	point loc(r, c);
	enemies[*it].insert(std::make_pair(loc, total.at(loc.first).at(loc.second)));
	if (influence.find(*it) != influence.end() && influence[*it].find(loc) != influence[*it].end()) {
	  enemies[*it][loc] -= influence[*it][loc];
	}
      }
    }
  }

  fighting.clear();

  std::set<point> bazinga;
  for (size_t i = 0; i < state.myAnts.size(); ++i) {
    point ant_loc(state.myAnts.at(i).row, state.myAnts.at(i).col);
    bazinga.insert(ant_loc);
    for (size_t k = 0; k < neighbours.at(ant_loc).size(); ++k) {
      point n = neighbours.at(ant_loc).at(k);	    
      bazinga.insert(n);  
    }
  }

  for (std::set<point>::iterator it = bazinga.begin(); it != bazinga.end(); ++it) {
    point some_loc = *it;
    if (enemies[0][*it] == 0) {
      continue;
    }
    for (size_t j = 0; j < all_ants.size(); ++j) {
      point foe_loc(all_ants.at(j).row, all_ants.at(j).col);
      int owner = state.grid.at(foe_loc.first).at(foe_loc.second).ant;
      if (owner != 0 && distance(some_loc, foe_loc) <= state.attackradius * 2 ) {
	std::vector<point> possible_moves = neighbours.at(foe_loc);
	possible_moves.push_back(foe_loc);
	int max_enemies = 0;
	for (size_t k = 0; k < possible_moves.size(); ++k) {
	  point enemy_loc = possible_moves.at(k);
	  if (distance(some_loc, enemy_loc) <= state.attackradius && enemies[owner][enemy_loc] > max_enemies) {
	    max_enemies = enemies[owner][enemy_loc];
	    closest_enemy[some_loc] = distance(some_loc, enemy_loc);
	  }
	}

	if (max_enemies > 0 && (fighting.find(some_loc) == fighting.end() || max_enemies < fighting.at(some_loc))) {
	  if (fighting.find(some_loc) == fighting.end()) {
	    fighting.insert(std::make_pair(some_loc, max_enemies));
	  }
	  else {
	    fighting.at(some_loc) = max_enemies;
	  }
	}
      }      
    }

    

    if (fighting.find(some_loc) == fighting.end()) {
      fighting.insert(std::make_pair(some_loc, 0));
    }

  }

  tiles.clear();

  for (std::set<point>::iterator it = bazinga.begin(); it != bazinga.end(); ++it) {
    point loc = *it;
    int value;
    //    print_loc(loc);
    //state.bug << " - > ";
    if (enemies[0][loc] == 0) {
      value = SAFE;
      //state.bug << " SAFE\n";
    }
    else if (enemies[0][loc] < fighting[loc]) {
      value = KILL;
      //state.bug << " KILL\n";
    }
    else if (enemies[0][loc] == fighting[loc]) {
      value = EQUAL;
      //state.bug << "EQUAL\n";
    }
    else {
      value = DIE;
      //state.bug << " DIE\n";
    }
    tiles.insert(std::make_pair(loc, value));
  }
}

double Bot::distance(point& a, point& b) {
  return sqrt(static_cast<double>((a.first - b.first) * (a.first - b.first) + (a.second - b.second) * (a.second - b.second)));
}

void Bot::explore_food(std::set<point>& targets, std::set<point>& busy_ants) {
  /*  for (std::set<point>::iterator it = my_ants.begin(); it != my_ants.end(); ++it) {
    point ant_loc = *it;
    if (busy_ants.find(ant_loc) == busy_ants.end()) {
      std::vector<std::pair<double, point> > food;
      for (size_t i = 0; i < state.food.size(); ++i) {
	point food_loc(state.food.at(i).row, state.food.at(i).col);
	if (targets.find(food_loc) == targets.end()) {	
	    double dist = state.distance(Location(ant_loc.first, ant_loc.second), state.food.at(i));
	    food.push_back(std::make_pair(dist, ant_loc));	  
	}
      }

      std::sort(food.begin(), food.end());
      
      for (size_t j = 0; j < food.size(); ++j) {
	  if (state.timer.getTime() >= 0.9 * state.turntime) {
	    return;
	  }
	  std::vector<point>* path = find_path(ants.at(j).second, food_loc);
	  if (path->size() > 0) {
	    paths.push_back(path);
	    busy_ants.insert(ants.at(j).second);
	    targets.insert(food_loc);
	    break;
	  }	
      }
    }
  }
*/

    for (size_t i = 0; i < state.food.size(); ++i) {
      point food_loc(state.food.at(i).row, state.food.at(i).col);
      if (targets.find(food_loc) == targets.end()) {
	std::vector<std::pair<double, point> > ants;
	for (std::set<point>::iterator it = my_ants.begin(); it != my_ants.end(); ++it) {
	  point ant_loc = *it;
	  if (busy_ants.find(ant_loc) == busy_ants.end()) {
	    double dist = state.distance(Location(ant_loc.first, ant_loc.second), state.food.at(i));
	    ants.push_back(std::make_pair(dist, ant_loc));
	  }
	}
      

	std::sort(ants.begin(), ants.end());

	for (size_t j = 0; j < ants.size(); ++j) {
	  if (state.timer.getTime() >= 0.8 * state.turntime) {
	    return;
	  }
	  std::vector<point>* path = find_path(ants.at(j).second, food_loc);
	  if (path->size() > 0) {
	    paths.push_back(path);
	    busy_ants.insert(ants.at(j).second);
	    targets.insert(food_loc);
	    break;
	  }
	}      
      }
      
    }
  
}
//makes the bots moves for the turn
void Bot::do_turn()
{
    state.bug << "turn " << state.turn << ":" << endl;
    //    state.bug << state << endl;

    recalculate_scents();

    calculate_influence();
 


    my_ants.clear();
    for (size_t i = 0; i < state.myAnts.size(); ++i) {
      point loc = std::make_pair(state.myAnts.at(i).row, state.myAnts.at(i).col);
	my_ants.insert(loc);
      }
    incoming.clear();
    outgoing.clear();

    std::vector<std::vector<point>* > new_paths;
    for (size_t i = 0; i < paths.size(); ++i) {
      if (valid_path(paths.at(i))) {
	new_paths.push_back(paths.at(i));
      }
    }

    paths = new_paths;

    std::set<point> targets;
    std::set<point> busy_ants;

    for (size_t i = 0; i < paths.size(); ++i) {
      std::vector<point>* path = paths.at(i);
      if (path->size() > 1) {
	targets.insert(path->at(path->size() - 1));
	busy_ants.insert(path->at(0));
      }
    }

    explore_food(targets, busy_ants);

    for (size_t i = 0; i <  state.myAnts.size(); ++i) {
      point ant_loc(state.myAnts.at(i).row, state.myAnts.at(i).col);
      if (busy_ants.find(ant_loc) == busy_ants.end()) {
	std::vector<point>* path = find_goal(ant_loc, "hills");
	if (path->size() > 1) {
	  paths.push_back(path);
	}
	else {
	  delete path;
	  path = find_goal(ant_loc, "enemy");
	  if (path->size() > 1) {
	    paths.push_back(path);
	  }
	  else {
	    delete path;
	    path = find_goal(ant_loc, "explore");
	    if (path->size() > 1) {
	      paths.push_back(path);
	    }
	  
	  }
	}
      }
    }

    for (size_t i = 0; i < paths.size(); ++i) {
      std::vector<point>* path = paths.at(i);
      make_move(path);
    }

    std::set<point> assigned;
    for (size_t i = 0; i < paths.size(); ++i) {
      assigned.insert(paths.at(i)->at(0));
    }
    standing.clear();
       for (size_t i = 0; i < state.myAnts.size(); ++i) {
      Location loc = state.myAnts.at(i);
      if (assigned.find(std::make_pair(loc.row, loc.col)) == assigned.end()) {
	standing.push_back(std::make_pair(loc.row, loc.col));
      }
    }
       
    for (size_t i = 0; i < paths.size(); ++i) {
      std::vector<point>* path = paths.at(i);
      if (path->size() > 1 && outgoing.find(path->at(1)) != outgoing.end() && outgoing[path->at(1)] == path->at(0)) {
	std::vector<std::vector<point>* > incoming_paths = incoming.at(path->at(0));
	for (size_t j = 0; j < incoming_paths.size(); ++j) {
	  std::vector<point>* p = incoming_paths.at(j);
	  if (path->at(1) == p->at(0)) {
	    path->erase(path->begin());
	    p->erase(p->begin());
	    break;
	  }
	}
      }
    }
    topological_sort();
    //picks out moves for each ant


    state.bug << "time taken: " << state.timer.getTime() << "ms" << endl << endl;
};

//finishes the turn
void Bot::endTurn()
{
    if(state.turn > 0)
        state.reset();
    state.turn++;

    cout << "go" << endl;
};
