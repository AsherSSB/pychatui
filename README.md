## To setup server
Simply run the server using `python server.py` while in the same directory as the server.py folder
Note this program does require python the be installed, for port 8181 to be open

## To setup CLI client
Start the client using `python client.py`
At any point, you may close the application and any connections you have with any chat servers by typing `CLOSE`
You may also go back to any previous steps by typing `BACK`
Connect to a server using the address and port input fields
If successfully connected, you will then be prompted to enter a username
After entering a username, connect to a listed room, or type `-1` to create a new room
If creating a new room, you will be prompted to enter a name for your new room
Once you enter a room, you may send and receive messages between you and other connected users until you decide to `BACK` out of the room or `CLOSE` the application

## To setup TUI client
First, you must install `textual`, a python library used to create TUI applications in python

**If you would like to install this libaray in a test environment**
Create a new directory
Move the parent directory of this README and the source code into the new directory
Enter this new directory
Create a python virtual environment using `pip -m venv .`
Activate the virtual environment using `source bin/activate`
Install textual into the virtual environment using `./bin/python bin/pip install textual`

**If you would like to install textual to your system packages**
With most system with python and pip installed, you may use `pip install textual`
If you are unable to install python packages onto your system this way, consult your system's package manager documentation
For example on arch, you may need to use `sudo pacman -Sy python-textual`
Or on ubuntu `sudo apt install python3-textual`
Some linux distrobutions may not have a way to safely install textual without breaking system packages
In these cases, it is best to refer to the first method and use a virtual environment

**Once textual is installed in a virtual environment or in system packages**
`cd` into the TUI directory
Run the program using `python main.py`
To exit at any point use `CTRL+q`
Follow the prompts to connect to or create a new chat room
