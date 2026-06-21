import socket 
replica = []

def addrep(dic):    
    replica.append(dic)
    print(replica)


def sendAll(msg):
    if(len(replica) > 0):
        for i in replica:
            try:
                if(True):
                    i["rep_socket"].sendall(msg)
            except Exception as e:
                continue
    print("done")



def sentok(soc):
    print(soc)
    for i in replica:
        if(soc == i["rep_socket"]):
            print("match found")
            i["sentok"] = True
    print(replica)
