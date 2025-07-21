#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <sstream>
#include <map>

using namespace std;

#define TEST 1
#ifndef TEST
#define TEST 0
#endif

/**
 * Win the water fight by controlling the most territory, or out-soak your opponent!
 **/

class Entity{
    public:
        int x, y;
        Entity(int x=-1, int y=-1){
            this->x = x;
            this->y = y;
        }

        int dist(Entity E){
            return abs(E.x - this->x) + abs(E.y - this->y);
        }

        int pythagore_dist(Entity E){
            return sqrt(pow(E.x - this->x, 2) + pow(E.y - this->y, 2));
        }

        string desc(void){
            stringstream str;
            str << this->x << " " << this->y;
            return str.str();
        }

        void update_coord(int x, int y){
            this->x = x;
            this->y = y;
        }

        bool operator == (const Entity & B)const{
            return this->x == B.x && this->y == B.y;
        }

        friend ostream& operator << (ostream& O, Entity A){
            return O << A.x << " " << A.y;
        }


};

class Rect{
    public:
        int left;
        int right;
        int top;
        int bottom;

    Rect(Entity A, Entity B){
        this->left = min(A.x, B.x);
        this->right = max(A.x, B.x);
        this->top = min(A.y, B.y);
        this->bottom = max(A.y, B.y);
    }

    bool isEntityInsideMe(Entity & A){
        return A.x >= this->left and A.x <= this->right and A.y >= this->top and A.y <= this->bottom; 
    } 

    friend ostream& operator << (ostream & O, Rect R){
        return O << "Rect: "<< R.top<< " "<< R.right << " "<< R.bottom<< " "<<R.left;
    }

};


class Block: public Entity{
    public:
        int height;
        Block(int x, int y, int height):Entity(x, y){
            height = height;
        }
};

class Agent:public Entity{
    public:
        int agent_id;
        int optimal_range;
        int soaking_power;
        int shoot_cooldown;
        int splash_bombs;
        int wetness;
  
        Agent(){}

        Agent(int agent_id, int shoot_cooldown, int optimal_range, int soaking_power, int splash_bombs):Entity(){
            this->agent_id=agent_id;
            this->optimal_range=optimal_range;
            this->soaking_power=soaking_power;
            this->shoot_cooldown=shoot_cooldown;
            this->splash_bombs=splash_bombs;
        }

        void update_agent(int x, int y, int wetness, int cooldown, int splash_bombs){
            update_coord(x, y);
            this->shoot_cooldown=cooldown;
            this->splash_bombs=splash_bombs;
            this->wetness=wetness;
        }

};


class Squad{
    public:
    map <int, Agent> agents;

    Squad(){
    }

    void addAgent(Agent & agent){
        this->agents[agent.agent_id] = agent;
    }

    bool isAgentInMySquad(int agent_id){
        return this->agents.find(agent_id) != agents.end();
    }

    const Agent get(int agent_id){
        if (isAgentInMySquad(agent_id)){
            return agents[agent_id];
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
        exit(1);
    }

    void updateAgentCoord(int agent_id, int x, int y){
        if(isAgentInMySquad(agent_id)){
            this->agents[agent_id].update_coord(x, y);
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
        exit(1);
    }

    void deleteAgent(int agent_id){
        if(isAgentInMySquad(agent_id)){
            this->agents.erase(this->agents.find(agent_id));
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
    }


};



int main()
{
    if(TEST){
        Entity A(0, 0);
        Entity B(0, 0);
        Entity C(10, 10);
        Entity D(5, 11);
        cout << (A == B) <<endl;

        Rect canvas(A, C);
        cout << "Is inside me = " << canvas.isEntityInsideMe(D)<<endl;
        cout << canvas << endl;

        Agent A1(0, 0, 0, 0, 0);
        A1.update_coord(65, 97);
        cout << A1 << endl;
        
        Squad my_team;
        my_team.addAgent(A1);
        my_team.addAgent(A1);
        A1.update_coord(65, 90);
        cout << (my_team.get(0)==A1) << endl;
    


        cout<<endl;
        exit(0);
    }
    int my_id; // Your player id (0 or 1)
    cin >> my_id; cin.ignore();
    int agent_data_count; // Total number of agents in the game
    cin >> agent_data_count; cin.ignore();
    for (int i = 0; i < agent_data_count; i++) {
        int agent_id; // Unique identifier for this agent
        int player; // Player id of this agent
        int shoot_cooldown; // Number of turns between each of this agent's shots
        int optimal_range; // Maximum manhattan distance for greatest damage output
        int soaking_power; // Damage output within optimal conditions
        int splash_bombs; // Number of splash bombs this can throw this game
        cin >> agent_id >> player >> shoot_cooldown >> optimal_range >> soaking_power >> splash_bombs; cin.ignore();
        Agent A(agent_id, shoot_cooldown, optimal_range, soaking_power, splash_bombs);        

    }
    int width; // Width of the game map
    int height; // Height of the game map
    cin >> width >> height; cin.ignore();
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            int x; // X coordinate, 0 is left edge
            int y; // Y coordinate, 0 is top edge
            int tile_type;
            cin >> x >> y >> tile_type; cin.ignore();
        }
    }

    // game loop
    while (1) {
        int agent_count; // Total number of agents still in the game
        cin >> agent_count; cin.ignore();
        for (int i = 0; i < agent_count; i++) {
            int agent_id;
            int x;
            int y;
            int cooldown; // Number of turns before this agent can shoot
            int splash_bombs;
            int wetness; // Damage (0-100) this agent has taken
            cin >> agent_id >> x >> y >> cooldown >> splash_bombs >> wetness; cin.ignore();
        }
        int my_agent_count; // Number of alive agents controlled by you
        cin >> my_agent_count; cin.ignore();
        for (int i = 0; i < my_agent_count; i++) {

            // Write an action using cout. DON'T FORGET THE "<< endl"
            // To debug: cerr << "Debug messages..." << endl << endl;


            // One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"
            cout << "HUNKER_DOWN" << endl;
        }
    }
}