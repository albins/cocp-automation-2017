#ifndef __PARSER_H_INCLUDED__
#define __PARSER_H_INCLUDED__

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <fstream>
#include <boost/algorithm/string.hpp>

class SceneAllocInstance {
    public:
    void print(std::ostream& input) const;
    static SceneAllocInstance from_file(std::string fileName);
    SceneAllocInstance(int _maxNumDays, int _maxScenesPerDay,
                       std::vector<std::tuple<std::string, int>> _actors,
                       std::vector<std::vector<int>> _scenes);
    const int maxNumDays;
    const int maxScenesPerDay;
    const std::vector<std::tuple<std::string, int>> actors;
    const std::vector<std::vector<int>> scenes;
};

#endif // __PARSER_H_INCLUDED__
