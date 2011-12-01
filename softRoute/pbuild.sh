cp * build/
cd build
g++ -g -Wall -c MyThread.cpp
g++ -g -Wall -c InterfaceInput.cpp
g++ -g -Wall -c InterfaceOutput.cpp
g++ -g -Wall -c ArpTable.cpp
g++ -g -Wall -c softRoute.cpp
g++ -g -Wall -lpcap -lpthread -o softRoute MyThread.o ArpTable.o InterfaceInput.o InterfaceOutput.o softRoute.o
