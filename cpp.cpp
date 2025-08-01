#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <sstream>
#include <map>

using namespace std;

#define TEST 0
#ifndef TEST
#define TEST 0
#endif

/**
 * Win the water fight by controlling the most territory, or out-soak your opponent!
 **/

class Entity{
    public:
        int x, y;
        Entity(int X=-1, int Y=-1){
            x = X;
            y = Y;
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

        Entity& operator=(const Entity E) {
            if (this != &E) {
                this->x = E.x;
                this->y = E.y;
                // Deep copy any dynamically allocated members
            }
            return *this;
        }

        bool operator == (const Entity & B)const{
            return this->x == B.x && this->y == B.y;
        }

        friend ostream& operator << (ostream& O, Entity A){
            return O << A.x << " " << A.y;
        }

        bool operator < (Entity & B){
            Entity reference(0,0);
            return this->dist(reference) < B.dist(reference);
        }

};

class Rect{
    private:
        Rect(){};
        friend class MyEngine;
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
        Agent(const Agent &E){
            this->x=E.x;
            this->y=E.y;
            this->agent_id=E.agent_id;
            this->optimal_range=E.optimal_range;
            this->soaking_power=E.soaking_power;
            this->shoot_cooldown=E.shoot_cooldown;
            this->splash_bombs=E.splash_bombs;
        }
        Agent(int agent_id, int shoot_cooldown, int optimal_range, int soaking_power, int splash_bombs):Entity(){
            this->agent_id=agent_id;
            this->optimal_range=optimal_range;
            this->soaking_power=soaking_power;
            this->shoot_cooldown=shoot_cooldown;
            this->splash_bombs=splash_bombs;
        }

        void update_agent(int x, int y, int wetness, int cooldown, int splash_bombs){
            update_coord(x, y);
            this->wetness=wetness;
            this->shoot_cooldown=cooldown;
            this->splash_bombs=splash_bombs;
        }

        const Rect getDomain(int domain_size=-1){
            if(domain_size < 0)domain_size = this->optimal_range * 2;
            return Rect(Entity(this->x - domain_size, this->y - domain_size), Entity(this->x + domain_size, this->y + domain_size));
        }

        friend ostream& operator << (ostream & O, const Agent & A){
            return O << "AgentId {"<<A.agent_id<<"} "<< "["<<A.x << ", "<<A.y<<"]";
        }

        Agent & operator=(const Agent E){
            if(this != &E){
                this->x=E.x;
                this->y=E.y;
                this->agent_id=E.agent_id;
                this->optimal_range=E.optimal_range;
                this->soaking_power=E.soaking_power;
                this->shoot_cooldown=E.shoot_cooldown;
                this->splash_bombs=E.splash_bombs;
            }
            return *this;
        }

};


class Squad{
    public:
    map <int, Agent> agents;

    Squad(){
        // this->agents = *(new map<int, Agent>);
    }

    void addAgent(const Agent agent){
        // cerr << "Add agent "<< agent<<endl;
        this->agents[agent.agent_id] = agent;
        // this->agents.insert(make_pair(agent.agent_id, agent));
    }

    bool isAgentInMySquad(int agent_id){
        return this->agents.find(agent_id) != this->agents.end();
    }

    Agent & get(int agent_id){
        if (isAgentInMySquad(agent_id)){
            return agents[agent_id];
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
        exit(1);
    }

    void updateAgentCoord(int agent_id, int x, int y){
        if(isAgentInMySquad(agent_id)){
            this->agents[agent_id].update_coord(x, y);
            return;
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
        exit(1);
    }

    void deleteAgent(int agent_id){
        if(isAgentInMySquad(agent_id)){
            this->agents.erase(this->agents.find(agent_id));
            return;
        }
        cerr << "Agent "<< agent_id << "not found in squad" << endl;
        exit(1);
    }

    map<string, Agent> getOrthoPeripheral(){
        // return top right bottom left
        int minX;
        int maxX;
        int minY;
        int maxY;
        minX=maxX=minY=maxY=-1;
        Agent top,left,right,bottom;

        int X,Y;
        for(const auto& [agent_id, agent]: this->agents){
            X = agent.x;
            Y = agent.y;
            if(minX < 0 || minX > X){
                minX = X;
                left=agent;
            }
            if(maxX < 0 || maxX < X){
                maxX = X;
                right=agent;
            }
            if(minY < 0 || minY > Y){
                minY = Y;
                top=agent;
            }
            if(maxY < 0 || maxY < Y){
                maxY = Y;
                bottom=agent;
            }
        }    

        return {{"top", top}, {"right", right}, {"bottom", bottom}, {"left", left}};
    }

};


class MyEngine{
    private:
        MyEngine();
    public:
        static Rect canvas;
        static vector <Entity> cover;

        static int decomposeMinDistance(int D){
            // get other half like if 6 -> 3 and the other part will be computed ulterially
            int N = sqrt(D);
            for (N; N > 0; N--){
                if(D%N == 0){
                    return N;
                }
            }
            return 1;
        }

        static Entity getTargetNearEntity(Entity & reference, vector <Entity> & places){
            Entity res = places[0];
            for(Entity & entity:places){
                if(reference.dist(entity) < reference.dist(res)){
                    res = entity;
                }
            }
            return res;
        }

        static vector <Entity> computeNotControlledZone(Rect zone, map<string, Agent> bluePeripheral, map<string, Agent> redPeripheral){
            vector <Entity> res;
            for(int y=zone.top; y < zone.bottom+1; y++){
                for(int x=zone.left; x < zone.right+1; x++){
                    Entity entity(x, y);
                    vector <int> blue_distance;
                    for(map <string, Agent>::iterator iter=bluePeripheral.begin(); iter != bluePeripheral.end(); iter++){
                        blue_distance.push_back(iter->second.dist(entity));
                    }
                    vector <int> red_distance;
                    for(map <string, Agent>::iterator iter=redPeripheral.begin(); iter != redPeripheral.end(); iter++){
                        red_distance.push_back(iter->second.dist(entity));
                    }
                    
                    if(*min_element(blue_distance.begin(), blue_distance.end()) >= *min_element(red_distance.begin(), red_distance.end())){
                        res.push_back(entity);
                    }
                    // cerr<<y<<" "<<res.size() <<endl;
                }
                // cerr<<y<<" "<<res.size() <<endl;
            }
            return res;
            
        }

        static vector <Entity> substractZoneFromRect(Rect & A, vector <Rect> & zones){
        // this is not used xD
            vector <Entity> available_places;
            for(int y=A.top; y < A.bottom+1; y++){
                for(int x=A.left; x < A.right+1; x++){
                    Entity entity(x, y);
                    bool available = true;
                    for(Rect & zone:zones){
                        if (zone.isEntityInsideMe(entity)){
                            available = false;
                            break;
                        }
                    }
                    if (available){
                        available_places.push_back(entity);
                    }
                }
            }
            return available_places;
        }



        static vector<vector<Entity>> dividePlaces(int agentCount, vector <Entity> places){
            // this will be an arrow shape (not good or maybe it could be good)
            // we should form Rect corner and divide the square
            vector <Entity> temp = places;
            sort(begin(temp), end(temp));
            int S = temp.size()/agentCount;
            if(S*agentCount < temp.size())S++; // get the remaining

            vector <vector <Entity>> res;
            for(int i = 0;i < agentCount;i++){
                vector <Entity> T;
                for(int j=0; (j < S) && ((i*S + j) < temp.size()); j++){
                    T.push_back(temp[i*S+j]);
                }
                res.push_back(T);
            }
            return res;
        }

};

Rect MyEngine::canvas;
vector <Entity> MyEngine::cover;

int main()
{
    if(TEST){
        Entity A(0, 0);
        Entity B(0, 0);
        Entity C(20, 20);
        Entity D(5, 11);
        cerr << (A == B) <<endl;

        Rect canvas(A, C);
        cerr << "Is inside me = " << canvas.isEntityInsideMe(D)<<endl;
        cerr << canvas << endl;

        Agent A1(0, 0, 0, 0, 0);
        A1.update_coord(65, 97);
        cerr << A1 << endl;
        
        Squad my_team;
        my_team.addAgent(A1);
        my_team.addAgent(A1);
        cerr << "My Squad size = "<<my_team.agents.size()<<endl;
        A1.update_coord(65, 90);
    
        MyEngine::canvas = canvas;
        cerr << "Test MyEngine Canvas = "<<MyEngine::canvas<<endl;

        int W,H;
        int agent_count = 60;
        W = MyEngine::decomposeMinDistance(agent_count);
        H = agent_count/W;
        cerr <<"DecomposeMinDistance : "<< W << " " << H << endl;


        // test available places
        vector <Entity> places;
        int height,width;
        height = 2;
        width = 3;
        for(int i = 0; i < height; i++){
            for(int j =0; j < width; j++){
                places.push_back(Entity(j, i));
            }
        }
        cerr << "Delete a places {";
        cerr << "   "<<places.size()<<endl;
        places.pop_back();
        cerr << "   "<<places.size()<<endl;
        cerr<< "}";

        vector <vector <Entity>> res = MyEngine::dividePlaces(3, places);
        for(int i = 0;i < res.size(); i++){
            cerr << "Place {"<<i<<"} :";
            for(int j = 0; j < res[i].size();j++)cerr << "["<<res[i][j] <<"] ";
            cerr << endl;
        }
        cerr << endl;

        // create agent
        Squad BLUE_TEAM;
        Agent BLUE1(0, 0, 0, 0, 0);
        BLUE1.update_coord(0,1);
        Agent BLUE2(1, 0, 0, 0, 0);
        BLUE2.update_coord(0,3);
        Agent BLUE3(2, 0, 0, 0, 0);
        BLUE3.update_coord(0,4);
        Agent BLUE4(8, 0, 0, 0, 0);
        BLUE4.update_coord(3,5);
        Agent BLUE5(99, 0, 0, 0, 0);
        
        BLUE_TEAM.addAgent(BLUE1);
        BLUE_TEAM.addAgent(BLUE2);
        BLUE_TEAM.addAgent(BLUE3);
        BLUE_TEAM.addAgent(BLUE4);
        BLUE_TEAM.addAgent(BLUE5);
        BLUE_TEAM.deleteAgent(1);
        cerr << "Deleted Agent BLUE_TEAM BLUE1[1]"<<endl;        
        cerr << "BLUE TEAM CHECK" <<endl;
        for(map <int, Agent>::iterator iter=BLUE_TEAM.agents.begin(); iter != BLUE_TEAM.agents.end(); iter++){
            cerr << iter->second<<endl;
        }        
        cerr << "Blue team size"<<BLUE_TEAM.agents.size()<<endl;
        Squad RED_TEAM;
        
        Agent RED1(3, 0, 0, 0, 0);
        RED1.update_coord(8,1);
        Agent RED2(4, 0, 0, 0, 0);
        RED2.update_coord(8,3);
        Agent RED3(5, 0, 0, 0, 0);
        RED3.update_coord(8,4);
        RED_TEAM.addAgent(RED1);
        RED_TEAM.addAgent(RED2);
        RED_TEAM.addAgent(RED3);
        
        vector<Entity> available_places = MyEngine::computeNotControlledZone(MyEngine::canvas, BLUE_TEAM.getOrthoPeripheral(), RED_TEAM.getOrthoPeripheral());
        cerr << "A = "<<available_places.size()<<endl;
        vector <vector <Entity>> plots = MyEngine::dividePlaces(BLUE_TEAM.agents.size(), available_places);
        cerr << "PLOTS = "<<plots.size()<<endl;
        cerr << "MYAGENTS_COUNT = "<<BLUE_TEAM.agents.size()<<endl;

        int counter = 0;
        cerr << "Available places : "<<available_places.size() << endl;
        for (map<int, Agent>::iterator iter=BLUE_TEAM.agents.begin(); iter != BLUE_TEAM.agents.end(); iter++) {
            Entity target = MyEngine::getTargetNearEntity(iter->second, plots[counter]);
            // Write an action using cerr. DON'T FORGET THE "<< endl"
            // To debug: cerr << "Debug messages..." << endl << endl;


            // One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"
            cerr << "; MOVE "<<target;
            cerr << "; HUNKER_DOWN" << endl;
        }


        cerr << "TEST PASSED !!"<<endl;
        cerr<<endl;
        exit(0);
    }
    
    int my_id; // Your player id (0 or 1)
    cin >> my_id; cin.ignore();
    int agent_data_count; // Total number of agents in the game
    cin >> agent_data_count; cin.ignore();

    Squad my_squad;
    Squad ennemy_squad;

    vector <int> isAlive(agent_data_count);

    for (int i = 0; i < agent_data_count; i++) {
        int agent_id; // Unique identifier for this agent
        int player; // Player id of this agent
        int shoot_cooldown; // Number of turns between each of this agent's shots
        int optimal_range; // Maximum manhattan distance for greatest damage output
        int soaking_power; // Damage output within optimal conditions
        int splash_bombs; // Number of splash bombs this can throw this game
        cin >> agent_id >> player >> shoot_cooldown >> optimal_range >> soaking_power >> splash_bombs; cin.ignore();
        Agent A(agent_id, shoot_cooldown, optimal_range, soaking_power, splash_bombs);
        isAlive[agent_id] = 1;

        if(player == my_id){
            my_squad.addAgent(A);
        }
        else{
            ennemy_squad.addAgent(A);
        }
    }
    int width; // Width of the game map
    int height; // Height of the game map
    cin >> width >> height; cin.ignore();
    MyEngine::canvas = Rect(Entity(0, 0), Entity(width-1, height-1));

    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            int x; // X coordinate, 0 is left edge
            int y; // Y coordinate, 0 is top edge
            int tile_type;
            cin >> x >> y >> tile_type; cin.ignore();
            if(tile_type != 0){
                Block B(x, y, tile_type);
                MyEngine::cover.push_back(B);
            }
        }
    }

    // game loop
    while (1) {
        int agent_count; // Total number of agents still in the game
        cin >> agent_count; cin.ignore();
        vector <int> checking_survival(isAlive.size());
        for (int i = 0; i < agent_count; i++) {
            int agent_id;
            int x;
            int y;
            int cooldown; // Number of turns before this agent can shoot
            int splash_bombs;
            int wetness; // Damage (0-100) this agent has taken
            cin >> agent_id >> x >> y >> cooldown >> splash_bombs >> wetness; cin.ignore();

            checking_survival[agent_id] = 1;

            if(my_squad.isAgentInMySquad(agent_id)){
                my_squad.get(agent_id).update_agent(x, y, wetness, cooldown, splash_bombs);
            }
            else{
                ennemy_squad.get(agent_id).update_agent(x, y, wetness, cooldown, splash_bombs);
            }
        }


        int my_agent_count; // Number of alive agents controlled by you
        cin >> my_agent_count; cin.ignore();

        // update squad check survivor
        for(int agent_id = 0;agent_id < isAlive.size(); agent_id++){
            if(isAlive[agent_id] && !(checking_survival[agent_id])){
                isAlive[agent_id] = 0;
                if(my_squad.isAgentInMySquad(agent_id)){
                    my_squad.deleteAgent(agent_id);
                }
                else{
                    ennemy_squad.deleteAgent(agent_id);
                }
            }
        }

        // Check my_squads
        cerr << "My SQUAD CHECK" <<endl;
        for(map <int, Agent>::iterator iter=my_squad.agents.begin(); iter != my_squad.agents.end(); iter++){
            cerr << iter->second<<endl;
        }



        vector<Entity> available_places = MyEngine::computeNotControlledZone(MyEngine::canvas, my_squad.getOrthoPeripheral(), ennemy_squad.getOrthoPeripheral());
        cerr << "A = "<<available_places.size()<<endl;
        vector <vector <Entity>> plots = MyEngine::dividePlaces(my_agent_count, available_places);

        cerr << "PLOTS = "<<plots.size()<<endl;
        cerr << "MYAGENTS_COUNT = "<<my_squad.agents.size()<<endl;
        
        int counter = 0;
        cerr << available_places.size() << endl << plots.size()<<endl;
        for (map<int, Agent>::iterator iter=my_squad.agents.begin(); iter != my_squad.agents.end(); iter++) {
            Entity target = MyEngine::getTargetNearEntity(iter->second, plots[counter++]);
            // Write an action using cout. DON'T FORGET THE "<< endl"
            // To debug: cerr << "Debug messages..." << endl << endl;


            // One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"
            cout << iter->first;
            cout << "; MOVE "<<target;
            cout << "; HUNKER_DOWN" << endl;
        }
    }
}