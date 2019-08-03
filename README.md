# GroupMeStats
A command-line utility for retrieving basic statistics for groups and/or chats in which your account is a part of. The program uses command line options to select a specific group or chat to search, as well as for saving messages retrieved for faster processing if desired. This retrieves messages using GroupMe's [REST API](https://dev.groupme.com/docs/v3). The program outputs the results as a csv file named 'groupme_stats.csv'. The program will only return a conglomeration of data, sorted by user, so if multiple result files are desired, the program will need to be ran multiple times and the previous file moved or renamed to avoid overwriting. 

## Getting Started
In order to run the program, certain requirements must be met in terms of its runtime environment.

### Prerequisites
This program was developed in Python 3.7.1 and requires a version of Python 3 to be installed in some form in order to run. Python downloads are available [here](https://www.python.org/downloads/).

### Python Dependencies
A few Python modules are used as part of this program and must be installed. Some may already be included with the standard installation of Python; however, a comprehensive list is provided here in the event this is not the case. [Pip](https://pip.pypa.io/en/stable/) can be used to install the modules and is included with Python versions 3.4 or newer.
The complete list of modules used in this program are as follows:
 * [argparse](https://docs.python.org/3/library/argparse.html)
 * [csv](https://docs.python.org/3/library/csv.html)
 * [json](https://docs.python.org/3/library/json.html)
 * [pickle](https://docs.python.org/3/library/pickle.html)
 * [requests](https://2.python-requests.org/en/master/)
 * [sys](https://docs.python.org/3/library/sys.html)
 * [time](https://docs.python.org/3/library/time.html)
 
 
The following libraries can be installed with pip using the following syntax (using argparse as an example):
```
pip3 install argparse
```

## Use
Once all dependencies are accounted for, the program can then be ran. The program can be opened from the command line using the following command, which assumes the terminal is currently in the directory/folder in which the file resides and that python has been added to the global path variable.
```
python GroupMeStats.py
```

### GroupMe Token
A valid GroupMe token is required for the program to run, as this is how GroupMe authenticates a specific account and retrieves its data specifically. One method by which this can be obtained is by logging into [GroupMe Developers](https://dev.groupme.com/) with your GroupMe account credentials and pressing the "Access Token" button on the page. 
This token can either be supplied when running the program via the command line, discussed in the following section, or by placing it in a file 'token.txt' (the filename must match exactly) located in the same directory as the program when running it. Only one option (command line or file) is required.

### Command-Line Arguments
A list of command line arguments can be obtained by running the program with the help argument (-h or --help) as shown below.
```
python GroupMeStats.py --help
```
The list of command line arguments are:
 * **--t TOKEN** or **--token TOKEN**  &nbsp; - &nbsp;  where TOKEN is your GroupMe account access token.
    ```
    python GroupMeStats.py --token TOKEN
    ```
 * **--c** or **--chat**  &nbsp; - &nbsp;  use to only analyze chats (direct messages)
    ```
    python GroupMeStats.py --chat
    ```
 * **--g** or **--group** &nbsp; - &nbsp; use to only analyze group messages
    ```
    python GroupMeStats.py --group
    ```
    * Note: The **--chat** and **--group** commands can both be used to analyze both direct messages and group messages
      ```
      python GroupMeStats.py --chat --group
      ```
    * For the program to retrieve any data with any of the commands below, one/both of the group and/or chat argument(s) must be provided.
 * **--i** or **--id** &nbsp; - &nbsp; use to only retrieve names and ids of group and direct message threads of which the account is part of without retrieving any messages.
 
 * **--s ID_SELECT** or **--id_select ID_SELECT** &nbsp; - &nbsp; use to retrieve one specific chat or group ID. Currently only supports retrieval of one message thread at a time (Although if both the **chat** and **group** parameters are provided, the program will analyze the respective thread of each type. This is more a side-effect than a feature). The ID_SELECT parameter to pass is the number in the leftmost '#' column beside the Person/Group Name of the thread.
 
 * **--a** or **--all_users** &nbsp; - &nbsp; List all users in the output statistics file, regardless of whether they are in the subset of message threads or message thread type selected. 
 
 * **--l** or **--load** &nbsp; - &nbsp; opt to load messages from a file rather than retrieving from the GroupMe API. Each time the program is ran, the results of the query are stored in either a direct messages or group messages file (depending on which one, or both, were selected in the previous run of the program). If you are looking to continuously run the program on the same set of data (such as well looking to test the program when adding a new feature), this mode may be useful. 
 
 * **-e ENCODING_TYPE** or **--encoding_type ENCODING_TYPE** &nbsp;- &nbsp; select encoding type between JSON and pickle. If not specified, JSON is the default. This parameter can be set when storing (which is done automatically when the API is queried) or loading from a previously saved file. Valid options for **ENCODING_TYPE** are 'json' or 'pkl'.
 
 ## Author
* **Arvind Draffen**
