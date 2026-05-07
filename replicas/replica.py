import socket
import datastore
import fileop
import threading

def parser(strs):
    print(type(strs))
    # strs = strs.decode("utf-8")
    print((strs))
    lst = strs.split("\r")[:-1]
    print(strs.split("\r")[:-1])

    res = []
    step = 2

    for i in range(0, len(lst), step):
        res.append(lst[i][1:])

    print(res)
    print(res[0] == "OK")
    if(res[0] == "OK"):
        return {"command": "+OK", "args": None}
    
    res = res[1:]
    
    print({"command": res[0].upper(), "arg": res[1:len(res)] if(len(res) >= 2) else None})
    return {"command": res[0].upper(), "arg": res[1:len(res)] if(len(res) >= 2) else None}


def handleclient(client_soc):
    while True:
        data = client_soc.recv(1024)
        if(not data):
            continue
        print("recieved data from client : ", data.decode())
        dic = parser(str(data, "utf-8"))
        try:
            if(dic["command"] == "PING"):
                client_soc.sendall(b"+PONG\r\n")

            elif (dic["command"] == "ECHO"):
                res = "$" + str(len(dic["arg"][0])) + "\r" + "\n" + dic["arg"] + "\r\n"
                client_soc.sendall(res.encode("utf-8"))

            elif(dic["command"] == "GET"):
                data = datastore.retrive(dic["arg"][0])
                if(data is None):
                    data = ""
                data = "$" + str(len(data)) + "\r" + "\n" + data + "\r\n"
                client_soc.sendall(data.encode("utf-8"))

            elif(dic["command"] == "CONFIG" and dic["arg"] == ["GET", "dir"]):
                dir = fileop.getpath()
                dir = "*2\r\n$3\r\ndir\r\n" + "$" + str(len(dir)) + "\r\n" + dir + "\r\n" 
                client_soc.sendall(dir.encode("utf-8"))
            
            elif(dic["command"] == "CONFIG" and dic["arg"] == ["GET", "dbfilename"]):
                fname = fileop.getfilename()
                fname = "*2\r\n$8\r\nfilename\r\n" + "$" + str(len(fname)) + "\r\n" + fname + "\r\n" 
                client_soc.sendall(fname.encode("utf-8"))
            
            elif(dic["command"] == "KEYS" and dic["arg"][0] == "*"):
                print("got it")
                keys = datastore.get_all_keys()
                res = "*" + str(len(keys)) +"\r\n"
                for i in keys:
                    res += "$" + str(len(i)) + "\r\n" + i + "\r\n"
                client_soc.sendall(res.encode("utf-8"))
            
            else:
                client_soc.sendall(b"-ERR unknown command\r\n")
        except Exception as e:
            print("Error:", e)
        

def handlemaster(client_soc):
    print("running master")
    while True:
        data = client_soc.recv(1024)
        if not data:
            continue
        print("Received from master:", data.decode())
        dic = parser(str(data, "utf-8"))
        try:
            # RESP format: *1\r\n$4\r\nPING\r\n
            if(dic["command"] == "PING"):
                client_soc.sendall(b"+PONG\r\n")

            elif (dic["command"] == "ECHO"):
                res = "$" + str(len(dic["arg"][0])) + "\r" + "\n" + dic["arg"] + "\r\n"
                client_soc.sendall(res.encode("utf-8"))

            elif(dic["command"] == "SET"):
                ttl = -1
                for i in range(len(dic["arg"])):
                    if(dic["arg"][i].upper() == "EX"):
                        print(dic["arg"][i], dic["arg"][i + 1])
                        ttl = float(dic["arg"][i + 1])
                        print(ttl)
                datastore.set(dic["arg"][0], dic["arg"][1], ttl)
                client_soc.sendall(b"+OK\r\n")

            elif(dic["command"] == "GET"):
                data = datastore.retrive(dic["arg"][0])
                if(data is None):
                    data = ""
                data = "$" + str(len(data)) + "\r" + "\n" + data + "\r\n"
                client_soc.sendall(data.encode("utf-8"))

            elif(dic["command"] == "CONFIG" and dic["arg"] == ["GET", "dir"]):
                dir = fileop.getpath()
                dir = "*2\r\n$3\r\ndir\r\n" + "$" + str(len(dir)) + "\r\n" + dir + "\r\n" 
                client_soc.sendall(dir.encode("utf-8"))
            
            elif(dic["command"] == "CONFIG" and dic["arg"] == ["GET", "dbfilename"]):
                fname = fileop.getfilename()
                fname = "*2\r\n$8\r\nfilename\r\n" + "$" + str(len(fname)) + "\r\n" + fname + "\r\n" 
                client_soc.sendall(fname.encode("utf-8"))
            
            elif(dic["command"] == "KEYS" and dic["arg"][0] == "*"):
                print("got it")
                keys = datastore.get_all_keys()
                res = "*" + str(len(keys)) +"\r\n"
                for i in keys:
                    res += "$" + str(len(i)) + "\r\n" + i + "\r\n"
                client_soc.sendall(res.encode("utf-8"))
            
            elif(dic["command"] == "+OK"):
                client_soc.sendall(b"+OK\r\n")
            
            elif(dic["command"] == "SAVE"):
                datastore.write()
                client_soc.sendall(b"+OK\r\n")

            else:
                client_soc.sendall(b"-ERR unknown command\r\n")         

        except Exception as e:
            print("Error:", e)
    

def connect_client(server_socket):      
        while True:        
            client_socket, addr = server_socket.accept()
            print("got a connection from: ", addr, " ", client_socket)            
            thread = threading.Thread(target=handleclient, args=(client_socket, ))
            thread.start()

client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_soc.connect(('localhost', 6380))

replconf = b"*2\r\n$7\r\nREPLCONF\r\n$4\r\nlistening-port\r\n$4\r\n6390\r\n"
client_soc.sendall(replconf)
thread2 = threading.Thread(target=handlemaster, args=(client_soc, ))
thread2.start()
server_socket = socket.create_server(("localhost", 6390), reuse_port=True)
server_socket.listen()
thread1 = threading.Thread(target=connect_client, args=(server_socket, ))

thread1.start()
            



