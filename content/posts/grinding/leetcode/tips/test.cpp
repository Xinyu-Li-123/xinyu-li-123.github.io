
#include <iostream>
#include <queue>
#include <vector>
#include <algorithm>

using namespace std;

struct Log {
    char user;
    int ts;
};

// Obtain K earliest logs from an unsorted vector of logs
vector<Log> earliestKLogs(vector<Log> logs, int k) {
    auto logCmp = [](const Log& a, const Log& b) {
        // if a has smaller timestamp than b, Compare(a, b) return true
        // priority queue will output b before a
        // b will be popped before a
        return a.ts < b.ts;
    };
    priority_queue<Log, vector<Log>, decltype(logCmp)> maxHeap(logCmp);

    for (const auto&log : logs) {
        maxHeap.push(log);
        if (maxHeap.size() > k) {
            maxHeap.pop();
        }
    }

    vector<Log> result;
    result.reserve(k);
    while (!maxHeap.empty()) {
        result.push_back(maxHeap.top());
        maxHeap.pop();
    }
    reverse(result.begin(), result.end());
    return result;
}

void customCmpDemo() {
    auto logs = vector<Log>{
        Log{'A', 3},
        Log{'B', 1},
        Log{'C', 2},
        Log{'D', 4},
        Log{'E', 0},
    };

    auto result = earliestKLogs(logs, 3);

    for (const auto& log : result) {
        cout << log.user << ", " << log.ts << endl;
    }
}

void minHeapDemo() {
    priority_queue<int, vector<int>, greater<int>> minHeap;

    minHeap.push(40);
    minHeap.push(20);
    minHeap.push(30);
    minHeap.push(10);

    while (!minHeap.empty()) {
        // 10, 20, 30, 40 
        cout << minHeap.top() << ", ";
        minHeap.pop();
    }
    cout << endl;
}

int main() {

    // minHeapDemo();
    customCmpDemo();

    return 0;
}