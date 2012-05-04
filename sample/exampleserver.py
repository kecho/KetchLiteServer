#!/usr/bin/python

#Python server example for KetchLiteServer

import imp

KetchLiteServer = imp.load_source('KetchLiteServer', '../src/KetchLiteServer.py')

class TestClass:
   def func(self,a,b,c,d):
       print(a + b + c + d)
       val = int(a)+int(b)+int(c)+int(d)
       return {"normal":val, "double":2*val, "array":range(10)}

   def noargsfun(self):
       print("callign a function with no arguments! and returning None")

if (__name__ == "__main__"):
    PORT = 8080
    print ("Starting server in port: %d" % (PORT))
    print ("Access this server's rpc calls via http. For example: http://localhost:%d/rpc/func?a=1&b=2&c=3&d=4" % (PORT))
    print ("Access normal html files or even this source via http. For example http://localhost:%d/exampleserver.py" % (PORT))
    KetchLiteServer.StartServer(TestClass, PORT)
    #KetchLiteServer.Shutdown() call this in another thread to shutdown the server
