### How to run

- start a venv `python3 -m venv venv` (assuming you have venv)
- activate it: `source venv/bin/activate` (for mac)
- install requirements: `pip install -r requirements.txt`
- run test (has current main): `python3 test.py`

### Note:
- There is an empty Jupyter Notebook. I really believe thats the way to go with this project especially if we are using matplotlib. Otherwise we have to switch out of ide and click through the graphs. Jupyter will make it easier to see the graphs and edit the code simultaneously. Also this wouldnt require us to do much, just implement the strategies and plotting in a jupyter. the pft.py can remain all portfolio class functions.

- pft.py is the class file. It has the functions for how a portfolio can behave. Im not sure its 100%

- There are probably errors in the strategies, and theres alot. All in strategies.py some are pretty useless however. I would get rid of them though, instead I would find a better way to store and implement different strategies. this way gets kinda messy, or just use multiple files



