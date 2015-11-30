# ==================================================== file = server.py ========
#   Application layer protocol for sharing stock values                        =
#     - Server side                                                            =
# ==============================================================================
#   Execute: python server.py                                                  =
# -----------------------------------------------------------------------------=
#   Notes: requires Python 3                                                   =
# -----------------------------------------------------------------------------=
#   Author:                                                                    =
#      Yuriy Zaynulin                                                          =
#      University of South Florida                                             =
#      WWW: https://github.com/juriy-zn/                                       =
#      Email: yuriyz@mail.usf.edu                                              =
# -----------------------------------------------------------------------------=
#   History:                                                                   =
#      YZ (11/11/15) - Init                                                    =
#      YZ (11/20/15) - Sockets outline                                         =
#      YZ (11/29/15) - Finish, polish                                          =
# ==============================================================================

# ---- Include files -----------------------------------------------------------

import socket
import sys

# ---- Global variables --------------------------------------------------------

BUFFER_SIZE = 4096
HOST = ''
PORT = 1050

RESPONSE_CODES = \
{
    "Request OK"          : "ROK",
    "Invalid Command"     : "INC",
    "Invalid Parameters"  : "INP",
    "Invalid Username"    : "INU",
    "User Already Exists" : "UAE",
    "User Not Registered" : "UNR"
}

COMMANDS = \
{
    "Register"       : "REG",
    "Unregister"     : "UNR",
    "Request Stocks" : "QUO"
}

# ---- Functions ---------------------------------------------------------------

# ==============================================================================
#   Function to parse the message from client,                                 =
#               perform error checking                                         =
# -----------------------------------------------------------------------------=
#   Inputs: (string) message                                                   =
#   Returns: (RESPONSE_CODES) code[,stock values]                              =
# ==============================================================================
def processMessage(message):
#   {
    # Separate the message
    command = message[:-1].split(sep=',')[0]
    parameters = message[:-1].split(sep=',')[1:]
    terminator = message[-1]

    print("INFO: Processing client message:")
    print("Command:    \"" + command + "\"")
    print("Parameters: \"" + str(parameters) + "\"")
    print("Terminator: \"" + terminator + "\"")

    # Check if terminator is there
    if terminator != ';':
        return RESPONSE_CODES["Invalid Command"]

    # Check if command is valid
    if command not in COMMANDS.values():
        return RESPONSE_CODES["Invalid Command"]

    # Check if parameters are valid
    if not parameters:
        return RESPONSE_CODES["Invalid Parameters"]

    # Register command parsing
    if command == COMMANDS['Register']:
        if len(parameters) > 1:
            return RESPONSE_CODES["Invalid Parameters"]
        elif parameters[0].strip() == '':
            return RESPONSE_CODES["Invalid Parameters"]
        elif len(parameters[0]) > 32:
            return RESPONSE_CODES["Invalid Username"]
        elif not parameters[0].isalnum():
            return RESPONSE_CODES["Invalid Username"]
        else:
            return addUsername(parameters[0])
    # Unregister command parsing
    elif command == COMMANDS['Unregister']:
        if len(parameters) > 1:
            return RESPONSE_CODES["Invalid Parameters"]
        elif parameters[0].strip() == '':
            return RESPONSE_CODES["Invalid Parameters"]
        elif len(parameters[0]) > 32:
            return RESPONSE_CODES["Invalid Username"]
        elif not parameters[0].isalnum():
            return RESPONSE_CODES["Invalid Username"]
        else:
            return removeUsername(parameters[0])
    # Request Stocks command parsing
    elif command == COMMANDS['Request Stocks']:
        if len(parameters) < 2:
            return RESPONSE_CODES["Invalid Parameters"]
        elif parameters[0].strip() == '':
            return RESPONSE_CODES["Invalid Parameters"]
        elif len(parameters[0]) > 32:
            return RESPONSE_CODES["Invalid Username"]
        elif not parameters[0].isalnum():
            return RESPONSE_CODES["Invalid Username"]
        else:
            return processStocks(parameters[0], parameters[1:])
#   }

# ==============================================================================
#   Function to add new user to registered users list                          =
# -----------------------------------------------------------------------------=
#   Inputs: (string) username                                                  =
#   Returns: (RESPONSE_CODES) code "User Already Exists" or code "Request OK"  =
# ==============================================================================
def addUsername(username):
    with open("usernames", "r") as file_usernames:
        for line in file_usernames:
            if line.lower() == (username.lower() + "\n"):
                return RESPONSE_CODES["User Already Exists"]

    with open("usernames", "a") as file_usernames:
        file_usernames.write(username + "\n")

    return RESPONSE_CODES["Request OK"]

# ==============================================================================
#   Function to remove a user from registered users list                       =
# -----------------------------------------------------------------------------=
#   Inputs: (string) username                                                  =
#   Returns: (RESPONSE_CODES) code "User Not Registered" or code "Request OK"  =
# ==============================================================================
def removeUsername(username):
    size_file_usernames = 0
    new_file_usernames = []

    with open("usernames", "r") as file_usernames:
        for line in file_usernames:
            if line.lower() != (username.lower() + "\n"):
                new_file_usernames.append(line)
            size_file_usernames += 1

    if size_file_usernames == len(new_file_usernames):
        return RESPONSE_CODES['User Not Registered']

    with open("usernames", "w") as file_usernames:
        for line in new_file_usernames:
            file_usernames.write(line)

    return RESPONSE_CODES["Request OK"]

# ==============================================================================
#   Function to retrieve requested stock values                                =
# -----------------------------------------------------------------------------=
#   Inputs: (string) username, (list) stocks                                   =
#   Returns: (RESPONSE_CODES) code "User Not Registered" or code "Request OK", =
#            followed by comma separated values of stocks, not found stocks'   =
#            values are set to -1                                              =
# ==============================================================================
def processStocks(username, stocks):
    size_file_usernames = 0
    response = ""
    with open("usernames", "r") as file_usernames:
        for line in file_usernames:
            if line.lower() == (username.lower() + "\n"):
                size_file_usernames = 1

    if not size_file_usernames:
        return RESPONSE_CODES['User Not Registered']

    stocks_dictionary = {}
    with open("stocks", "r") as file_stocks:
        for line in file_stocks:
            stocks_dictionary[line.split()[0].lower()] = line.split()[1].lower()

    for stock in stocks:
        if stock.lower() in stocks_dictionary.keys():
            response = response + "," + stocks_dictionary[stock.lower()]
        else:
            response += ",-1"

    return RESPONSE_CODES["Request OK"] + response

# ==== Main program ============================================================

try:
#   {
    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as error:
        print("ERROR: Failed to create socket")
        print("  Reason: " + str(error))
        sys.exit()

    # Bind socket
    try:
        s.bind((HOST, PORT))
    except OSError as error:
        print("ERROR: Bind failed")
        print("  Reason: " + str(error))
        s.close()
        sys.exit()

    # Information
    print("INFO: Server is running")

    # Start talking to clients
    while 1:
    #   {
        try:
            received_data = s.recvfrom(BUFFER_SIZE)
        except OSError as error:
            print("ERROR: Failed to receive data")
            print("  Reason: " + str(error))
            continue

        message_from_client = received_data[0]
        address_client = received_data[1]
        print("INFO: Received from client [" + address_client[0] + "]: \'" +
                message_from_client.decode() + "\'")

        try:
            response = processMessage(message_from_client.decode()) + ";"
        except Exception as error:
            print("ERROR: Failed to process message: \'" +
                    message_from_client.decode() + "\'")
            print("  Reason: " + str(error))
            continue

        try:
            print("INFO: Sending to client [" + address_client[0] + "]: \'" +
                    response + "\'")
            s.sendto(response.encode(), address_client)
        except OSError as error:
            print("ERROR: Failed to send data")
            print("  Reason: " + str(error))
            continue
    #   }

    s.close()
#   }
# Handle exit with ^C
except KeyboardInterrupt:
#   {
    print()
    print("Exiting...")
    print()
    s.close()
    sys.exit()
#   }
