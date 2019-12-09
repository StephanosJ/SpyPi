import socket

#Defines the SpyPi server
server = socket.socket()
host = "192.168.2.184"
port = 7777

try:
    #tries to connect to the SpyPi server
    server.connect((host, port))
    #Simple print statement letting the user now its client connected with the raspberry pi
    print("Beep Boop! Client connected to the raspberry pi!")
    while True:
        print("How long do you want to record to? (in seconds): ", end='')
        #input from the user, has to be in seconds.
        recordingseconds = input().encode()
        #Error handeling if the user input is not a int it would notify the user it's not an int also when the int is negative. This in is later used for how long an user wants to record with the pi
        try:
            int(recordingseconds)
            if int(recordingseconds) <= 0:
                print("The integer can not be lower than 0")
            else:
                break
        except ValueError:
            print("Sorry but this is not an integer")
    #sends the packet the the SpyPi server
    server.sendall(recordingseconds)
    print("The SpyPi will record " + recordingseconds.decode() + " seconds")
    while True:
        #Gets the response from the SpyPi server
        server_response = server.recv(2048)
        server_response = server_response.decode() 
        print(server_response)
        #When the server_response is not an int it should be at packet saying it has been saved and been notified by the user
        if server_response != "That's not an int!":
            break
    print("The SpyPi client program is closing")
except Exception as error:
    #when the client can't connect to the SpyPi server it prints out an error statement
    print("connecting socket failed:\n" + str(error))
    server.close()
