#ifndef BOT_H_
#define BOT_H_
#include <map>
#include <set>
#include "State.h"

/*
    This struct represents your bot in the game of Ants
*/

const int KILL = 0;
const int SAFE = 1;
const int EQUAL = 2;
const int DIE = 3;

const int HILLS = 1;
const int ENEMIES = 2;
const int EXPLORE = 3;

typedef std::pair<int, int> point;
struct Bot
{
    State state;
  double max_value;
  
  std::vector<std::vector<double> > last_seen;
  std::map<std::string, std::vector<std::vector<double> >* > agents;
  std::map<std::pair<int, int>, std::vector<std::pair<int, int> > > neighbours;
  std::set<point> m_enemy_hills;
  std::set<point> m_enemy_ants;
  std::map<point, std::vector<std::vector<point>* > > incoming;
  std::map<point, point> outgoing;
  std::vector<std::vector<point>* > paths;
  std::set<point> my_ants;
  std::set<point> orders;
  std::vector<point> standing;
  std::map<int, std::map<point, int> > enemies;
  std::map<point, int> fighting;
  std::map<point, int> tiles;
  std::vector<std::vector<int> > total;
  std::map<point, double> closest_enemy;
  int searches;
    Bot();

    void playGame();    //plays a single game of Ants
  void do_setup();
  void clear();
  void bfs(std::vector<point>& start_list, int type);
  void recalculate_scents();
  double diffuse_hills(point loc);
  double diffuse_ants(point loc);
  double diffuse_explore(point loc);
  double diffuse(point loc, std::string goal);
  std::vector<point>* find_goal(point loc, std::string goal);
  void make_move(std::vector<point>* path);
  void topological_sort();
  bool valid_path(std::vector<point>* path);
  std::vector<point>* find_path(point from, point to);
  void print_path(std::vector<point>* path);
  void print_loc(point p);
  void issue_order(point from, point to);
  void calculate_influence();
  double distance(point& a, point& b);
  std::pair<bool, point> try_action(point ant_loc, int action);
  void explore_food(std::set<point>& targets, std::set<point>& busy_ants);
  int passable(point& loc);
    void do_turn();   //makes moves for a single turn
    void endTurn();     //indicates to the engine that it has made its moves
};

#endif //BOT_H_
