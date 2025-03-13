## To setup server
Simply run the server using `python server.py` while in the same directory as the server.py folder

Note this program does require python the be installed, for port 8181 to be open

## To setup CLI client
1. Start the client using `python client.py`

   - At any point, you may close the application and any connections you have with any chat servers by typing `CLOSE`

   - You may also go back to any previous steps by typing `BACK`

2. Connect to a server using the address and port input fields

3. If successfully connected, you will then be prompted to enter a username

4. After entering a username, connect to a listed room, or type `-1` to create a new room

   - If creating a new room, you will be prompted to enter a name for your new room

6. Once you enter a room, you may send and receive messages between you and other connected users until you decide to `BACK` out of the room or `CLOSE` the application

## To setup TUI client
First, you must install `textual`, a python library used to create TUI applications in python

**If you would like to install this libaray in a test environment**

1. Create a new directory

2. Move the parent directory of this README and the source code into the new directory

3. Enter this new directory

4. Create a python virtual environment using `pip -m venv .`

5. Activate the virtual environment using `source bin/activate`

6. Install textual into the virtual environment using `./bin/python bin/pip install textual`

**If you would like to install textual to your system packages**

With most system with python and pip installed, you may use `pip install textual`

If you are unable to install python packages onto your system this way, consult your system's package manager documentation

For example on arch, you may need to use `sudo pacman -Sy python-textual`

Or on ubuntu `sudo apt install python3-textual`

Some linux distrobutions may not have a way to safely install textual without breaking system packages

In these cases, it is best to refer to the first method and use a virtual environment

**Once textual is installed in a virtual environment or in system packages**

1. `cd` into the TUI directory

2. Run the program using `python main.py`

   - To exit at any point use `CTRL+q`

3. Follow the prompts to connect to or create a new chat room
