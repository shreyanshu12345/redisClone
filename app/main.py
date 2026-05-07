import socket
import threading
import datastore
import fileop
import argparse
import handlereplica

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
    
    if(res[0] == "OK"):
        return {"command": "+OK", "args": None}

    res = res[1:]
    print({"command": res[0].upper(), "arg": res[1:len(res)] if(len(res) >= 2) else None})
    return {"command": res[0].upper(), "arg": res[1:len(res)] if(len(res) >= 2) else None}

def handle_client(soc):
    client_soc = soc
    while(True):
        req = client_soc.recv(1024)
        request = req

        if(len(request) == 0):
            continue
        
        print("message: ", type(request))
        dic = parser(str(req, "utf-8"))
        handlereplica.sendAll(req)
        print("dic: ", dic)
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
            
            # elif(dic["command"] == "REPLCONF" and dic["arg"][0] == "listening-port"):
            #     dic = {"ip": "127.0.0.1", "port": dic["arg"][1], "sentok": False}
            #     handlereplica.addrep(dic)
            #     client_soc.sendall(b"+OK\r\n")
            
            # elif(dic["command"] == "+OK"):
            
            
            elif(dic["command"] == "SAVE"):
                datastore.write()
                client_soc.sendall(b"+OK\r\n")

            else:
                client_soc.sendall(b"-ERR unknown command\r\n")
            



        except Exception as e:
            print("Error:", e)
            
def handle_replica(replica_socket):
        
        while(True):
            req = replica_socket.recv(1024)
            request = req

            if(len(request) == 0):
                continue
            
            print("message: ", type(request))
            dic = parser(str(req, "utf-8"))
            print("dic: ", dic)
            if(dic["command"] == "REPLCONF" and dic["arg"][0] == "listening-port"):
                dic = {"ip": "127.0.0.1", "port": dic["arg"][1], "rep_socket": replica_socket, "sentok": False}
                handlereplica.addrep(dic)
                replica_socket.sendall(b"+OK\r\n")
            elif(dic["command"] == '+OK'):
                print("setting true")
                handlereplica.sentok(replica_socket)


            
            # dic = parser(str(req, "utf-8"))
            # print("dic: ", dic)


def connect_client(server_socket):      
        while True:        
            client_socket, addr = server_socket.accept()
            print("got a connection from: ", addr, " ", client_socket)            
            thread = threading.Thread(target=handle_client, args=(client_socket, ))
            thread.start()

def connect_replicas(server_socket):
    while True:        
            replica_socket, addr = server_socket.accept()
            print("got a connection from: ", addr, " ", replica_socket)            
            thread = threading.Thread(target=handle_replica, args=(replica_socket, ))
            thread.start()


def main():
    print("Logs from your program will appear here!")
    
    fileop.getinfo()
    print(fileop.dic['port'])
    server_socket = socket.create_server(("localhost", int(fileop.dic['port'])), reuse_port=True)
    server_socket.listen()
    # no_client_connect = 0    
    print("client socket listening")

    server_socket2 = socket.create_server(("localhost", 6380), reuse_port=True)
    server_socket2.listen()
    # no_rep_connect = 0

    thread1 = threading.Thread(target=connect_client, args=(server_socket, ))
    thread2 = threading.Thread(target=connect_replicas, args=(server_socket2, ))
    thread1.start()
    thread2.start()

    

        
        
        
            

if __name__ == "__main__":
    main()
