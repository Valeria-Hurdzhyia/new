#include <Windows.h>
#include <fstream>
#include <sstream>
#include <string>
using namespace std;
int main() {
	system("wmic bios get biosversion > tmp.txt");
	int n = 30;
	char* buffer = new char[n + 1];
	ifstream file;
	file.open("tmp.txt");
	string data;
	if (file.is_open()) {
		ostringstream a;
		a << file.rdbuf();
		data = a.str();
	}
	system("del tmp.txt");
	string deta1 = "d";
	size_t found = data.find("VMWare");
	if (found == string::npos) {
		MessageBox(0, L"Hello kitty!", L"laba_3", MB_OK);
	}
	return 0;
}
