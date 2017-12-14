#include "parser.hh"


#define ERR_NOACTOR -1
// read line by line
// ignore comments
// first four non-comment lines are numbers
// str,num = actor/salary
// num,str = scene/actor


// String trimming: https://stackoverflow.com/a/217605
// trim from start (in place)
static inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int ch) {
                return !std::isspace(ch);
            }));
}

// trim from end (in place)
static inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch) {
                return !std::isspace(ch);
            }).base(), s.end());
}

// trim from both ends (in place)
static inline void trim(std::string &s) {
    ltrim(s);
    rtrim(s);
}

// Read an integer constant, skipping comments.  raise an exception on
// end-of-string, or non-integer first character (excluding white
// space).
int read_constant(std::istream &inputs) {
    std::string token;
    while(std::getline(inputs, token)) {
        trim(token);
        if(token.length() < 1 || token[0] == '#') {
            //cout << "Ignoring comment! " << token << std::endl;
            continue;
        }

        int value;
        std::stringstream(token) >> value;
        if(value == 0) {
            throw std::string("Invalid integer token: ") + token;
        }
        return value;
    }
    throw std::string("Token error: file ended before I could read a single integer!");

}

std::tuple<std::string, int> read_actor_salary(std::istream &inputs) {
    //cout << "Reading actor" << std::endl;

    std::string token;
    while(std::getline(inputs, token)) {
        trim(token);
        if(token.length() < 1 || token[0] == '#') {
            //cout << "Ignoring comment! " << token << std::endl;
            continue;
        }
        std::vector<std::string> results;
        boost::split(results, token, [](char c){return c == ',';});

        if(results.size() != 2) {
            throw std::string("Invalid actor token: ") + token;
        }

        try {
            int salary = std::stoi(results[1]);
            std::string name(results[0]);
            trim(name);
            return std::tuple<std::string, int>(name, salary);
        } catch(std::invalid_argument) {
            throw std::string("Invalid salary for line: ") + token;
        }
    }
    throw std::string("Token error: file ended before I could read an actor!");



}

std::tuple<int, std::vector<std::string>> read_scene_actors(std::istream &inputs) {
    //cout << "Reading scene" << std::endl;

    std::string token;
    while(std::getline(inputs, token)) {
        trim(token);
        if(token.length() < 1 || token[0] == '#') {
            //cout << "Ignoring comment! " << token << std::endl;
            continue;
        }

        std::vector<std::string> results;
        boost::split(results, token, [](char c){return c == ',';});

        if(results.size() < 2) {
            //cout << "Invalid scene token! : " << token;
            throw std::string("Invalid scene token: ") + token;
        }

        try {
            int sceneNo = std::stoi(results[0]);

            std::vector<std::string> actors(results.begin() + 1, results.end());

            for(auto &actorS : actors) {
                trim(actorS);
            }

            return std::tuple<int, std::vector<std::string>>(sceneNo, actors);


        } catch(std::invalid_argument) {
            throw std::string("Invalid scene number for line: ") + token;
        }

    }
    throw std::string("Token error: file ended before I could read a scene!");
}


int str_position(std::string target, std::vector<std::tuple<std::string, int>> vec) {
    int n = 0;
    for(auto a : vec) {
        if(target == std::get<0>(a)) return n;
        n++;
    }

    return ERR_NOACTOR;

}



SceneAllocInstance::SceneAllocInstance(int _maxNumDays, int _maxScenesPerDay,
                                       std::vector<std::tuple<std::string, int>> _actors,
                                       std::vector<std::vector<int>> _scenes)
    : maxNumDays(_maxNumDays), maxScenesPerDay(_maxScenesPerDay),
      actors(_actors), scenes(_scenes)
{
    // well, this is just an empty container.
}

SceneAllocInstance SceneAllocInstance::from_file(std::string fileName) {
    std::ifstream in(fileName);
    int numScenes = read_constant(in);
    int maxDays = read_constant(in);
    int maxScenesPerDay = read_constant(in);
    int numActors = read_constant(in);

    // Read actors
    std::vector<std::tuple<std::string, int>> parsed_actors;
    for (int i = 0; i < numActors; i++) {
        parsed_actors.push_back(read_actor_salary(in));
    }

    // Read scenes
    std::vector<std::tuple<int, std::vector<std::string>>> parsed_scenes;
    for (int i = 0; i < numScenes; i++) {
        parsed_scenes.push_back(read_scene_actors(in));
    }

    std::vector<std::vector<int>> _scenes(numScenes);

    for(auto scene : parsed_scenes) {
        int scene_id = std::get<0>(scene) - 1;
        std::vector<int> scene_actors;
        //_scenes[scene_id - 1]
        for(auto actor_name : std::get<1>(scene)) {
            int actor_id = str_position(actor_name, parsed_actors);
            if(actor_id == ERR_NOACTOR) throw(std::string("No such actor: ")
                                              + '"' + actor_name + '"');

            scene_actors.push_back(actor_id);
        }

        _scenes[scene_id] = scene_actors;
    }

    return SceneAllocInstance(maxDays,
                              maxScenesPerDay,
                              parsed_actors,
                              _scenes);

}

void SceneAllocInstance::print(std::ostream& os) const {
    os << "Max days: " << maxNumDays << std::endl;
    os << "Max scenes per day: " << maxScenesPerDay << std::endl;
    os << "Actors: " << std::endl;
    for (unsigned int i = 0; i < actors.size(); i++) {
        os << "[" << i + 1 << "] " << std::get<0>(actors[i]) << ", salary=" <<
            std::get<1>(actors[i]) << std::endl;
    }
    os << "Scenes: " << std::endl;
    for (unsigned int i = 0; i < scenes.size(); i++) {
        os << "[" << i + 1 << "] " << "actors: ";
        for(auto actor : scenes[i]) {
            os << actor + 1 << " ";
        }
        os << std::endl;
    }
}
