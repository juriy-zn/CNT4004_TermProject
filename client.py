# ==================================================== file = client.py ========
#   Application layer protocol for sharing stock values                        =
#     - Client side                                                            =
# ==============================================================================
#   Execute: python client.py <server IP>                                      =
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

import select
import socket
import sys

# ---- Global variables --------------------------------------------------------

BUFFER_SIZE = 4096
MAXIMUM_ATTEMPTS = 3
PORT = 1050
TIMEOUT = 5

# ---- Functions ---------------------------------------------------------------

# ==============================================================================
#   Function to print the information about how to use the client program      =
# -----------------------------------------------------------------------------=
#   Inputs: -                                                                  =
#   Returns: -                                                                 =
# ==============================================================================
def printInstruction():
    print()
    print("Usage:")
    print("  COMMAND,parameter[,parameterX,parameterY,parameterZ];")
    print()
    print("Commands for server:")
    print("  REG,<username>;")
    print("  : register <username>")
    print("  UNR,<username>;")
    print("  : unregister <username>")
    print("  QUO,<username>,<stock1>,<stock2>,...;")
    print("  : request <stock1>,<stock2>,... using <username>")
    print()
    print("Commands for managing client:")
    print("  I")
    print("  : print this information again")
    print("  R")
    print("  : repeat previous command for server")
    print("  Q")
    print("  : quit the program")
    print()

# ==== Main program ============================================================

try:
#   {
    # Instructions
    printInstruction()

    # Get server IP from parameter or set to default (127.0.0.1)
    if len(sys.argv) < 2:
        print("WARNING: Missing an IP address, using: 127.0.0.1")
        HOST = "127.0.0.1"
    else:
        print("INFO: Connecting to server: " + sys.argv[1])
        HOST = sys.argv[1]

    connection = (HOST, PORT)

    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(0)
    except OSError as error:
        print("ERROR: Failed to create socket")
        print("  Reason: " + str(error))
        sys.exit()

    # Clear previous message to server
    previous_message_to_server = ""

    # Utility class to break out of outside loop
    class InnerLoopError(Exception): pass

    # Start talking to server
    while 1:
    #   {
        user_input = input("(Get Stock) >>> ")
        if not user_input:
            continue
        elif user_input.upper() == 'Q':
            print("Exiting...")
            print()
            break
        elif user_input.upper() == 'I':
            printInstruction()
            continue
        elif user_input.upper() == 'R':
            if previous_message_to_server:
                message_to_server = previous_message_to_server
            else:
                print("WARNING: No previous message to server")
                continue
        else:
            message_to_server = user_input
            previous_message_to_server = message_to_server

        attempts = 0
        try:
        #   {
            while attempts < MAXIMUM_ATTEMPTS:
                try:
                    print("INFO: Sending to server [" + HOST + "]: \'" +
                            message_to_server + "\'")
                    s.sendto(message_to_server.encode(), connection)
                except OSError as error:
                    print("ERROR: Failed to send data")
                    print("  Reason: " + str(error))
                    raise InnerLoopError()

                # Set timeout for getting the data from server
                ready_received_data = select.select([s], [], [], TIMEOUT)
                if ready_received_data[0]:
                    try:
                        received_data = s.recvfrom(BUFFER_SIZE)
                        break
                    except OSError as error:
                        print("ERROR: Failed to receive data")
                        print("  Reason: " + str(error))
                        raise InnerLoopError()

                attempts += 1
                print("WARNING: Timeout (attempt " + str(attempts) + " of " +
                        str(MAXIMUM_ATTEMPTS) + ") on message: \'" +
                        message_to_server + "\'")
        #   }
        # Handle the error that may happen in the nested loop above
        except InnerLoopError:
            continue

        if attempts == MAXIMUM_ATTEMPTS:
            print("ERROR: No response from server on message: \'" +
                    message_to_server + "\'")
            continue

        message_from_server = received_data[0]
        address_server = received_data[1]
        print("INFO: Received from server [" + address_server[0] + "]: \'" +
                message_from_server.decode() + "\'")
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
