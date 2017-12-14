#include "parser.hh"

using namespace std;

int main(int argc, char *argv[])
{
    try {
        SceneAllocInstance sa = SceneAllocInstance::from_file(argv[1]);
        sa.print(std::cout);
    } catch(std::string error) {
        cout << error << endl;
    }

    return 0;
}
