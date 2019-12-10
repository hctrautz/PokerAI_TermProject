# PyPokerEngine MonteCarlo Agent 

<h2> Contributors </h2> 

*Hunter Trautz and Gabriel Aponte*

<h2> Prerequisites </h2> 

* [PyCharm](https://www.jetbrains.com/pycharm/)
* [Python 3.7](https://www.python.org/downloads/release/python-370/)

<h2> Installation </h2> 

1. Download the source code from Github and unzip the folder. 
2. Open the PokerAI_TermProject-master folder in PyCharm by clicking File -> Open and then selecting the folder. 
3. Ensure that the project interpreter is set to Python 3.7 in File -> Settings -> Project: PokerAI_TermProject-master -> Project Interpreter
4. Also in Project Interpreter Settings, install the PyPokerEngine and PyPokerGUI packages by clicking the "+" button. 
5. PyPokerGUI has an exisiting bug that does not allow it to run with Python 3.7, so we have to now edit one file so that our pojrect can work.
6. Navigate to venv(library root)/Lib/site-packages/pypokergui/server/templates/round_state.html
7. Under the "seats-upper-row row-center" div replace "{% for idx, player in zip(range(len(round_state['seats']))[:len(round_state['seats'])/2], round_state['seats']) %}" with "{% for idx, player in zip(range(len(round_state['seats']))[:int(len(round_state['seats'])/2)], round_state['seats']) %}"
8. Lastly, under the "seats-lower row row-center" div replace "{% for idx, player in zip(range(len(round_state['seats']))[len(round_state['seats'])/2:], round_state['seats'][len(round_state['seats'])/2:]) %}" with "{% for idx, player in zip(range(len(round_state['seats']))[int(len(round_state['seats'])/2):], round_state['seats'][int(len(round_state['seats'])/2):]) %}"

![Interpreter](https://i.imgur.com/at7r1nM.png)

<h2> Steps to run </h2>

1. After completing all of the installation steps, open the Terminal inside of PyCharm located in the bottom left corner.
2. Type: "pypokergui serve poker_conf.yaml --port 8000 --speed moderate" and then press enter.
3. The program will open in your default browser.
4. Enter your name in the "Register Me" textbox and then press register. 
5. Press "Start Poker". 

![Example](https://i.imgur.com/2US3QVK.png)

<h2> Resources Used in Development </h2> 

* [PyPokerEngine](https://github.com/ishikota/PyPokerEngine)
* [PyPokerGUI](https://github.com/ishikota/PyPokerGUI)
