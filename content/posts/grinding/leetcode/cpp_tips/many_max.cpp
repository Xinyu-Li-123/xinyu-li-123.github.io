#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

int main() {
    vector<int> vec = {10, 20, 5, 30, 40, -50};

    // max of vec
    cout << *max_element(vec.begin(), vec.end()) << endl;

    // max of vec[1: 4]
    cout << *max_element(vec.begin()+1, vec.begin()+4) << endl;

    // max of abs val, use of anonymous fn
    int ans = *max_element(vec.begin(), vec.end(), [](int a, int b) {
        return abs(a) < abs(b);
    });
    cout << ans << endl;

    cout << max({10, 20, 30}) << endl;

    return 0;
}