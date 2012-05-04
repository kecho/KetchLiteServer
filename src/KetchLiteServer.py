#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
import inspect
import json
import sys

__static_rpc_worker_instance = None
__static_rpc_worker_functions_spec = None

def _SetRpcWorkerInstance(RpcWorkerClass):
    global __static_rpc_worker_instance 
    global __static_rpc_worker_functions_spec
    __static_rpc_worker_instance = RpcWorkerClass()
    #cash arguments, we use [1:] not to include the self argument
    __static_rpc_worker_functions_spec = {
             el: inspect.getargspec(getattr(__static_rpc_worker_instance, el)).args[1:] #skipping self argument 
             for el in dir(__static_rpc_worker_instance) 
             if (type(getattr(__static_rpc_worker_instance,el)).__name__ == 'instancemethod')
             }

def _GetCachedInstanceFuncsArgs(funcName):
    global __static_rpc_worker_functions_spec
    return __static_rpc_worker_functions_spec[funcName]

def _GetArgList(method, rawArguments):
    argList = _GetCachedInstanceFuncsArgs(method.im_func.func_name)
    rawArgMap = {v[0] : v[1] for v in [el.split("=") for el in rawArguments.strip(" &").split("&")] if (len(v) == 2 and (v[0] in argList))}
    return [rawArgMap[k] for k in argList] if (len(rawArgMap) == len(argList)) else None
    

def _GetRpcWorker():
    return __static_rpc_worker_instance

def _PerformRpcCall(funName, argStringRequest):
    instance = _GetRpcWorker()
    try:
        if (hasattr(instance, funName)):
            method = getattr(instance, funName) 
            argList = _GetArgList(method, argStringRequest)
            if (argList != None):
                return (0, method(*argList))
        return(-1, None)
    except:
        print("Exception: ", sys.exc_info()[0])
        return(-2,None)

class KetchLiteServerRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if (self.path.startswith("/rpc/")):
            argumentList = self.path.strip()[len("/rpc/"):].strip("/").split("?")  
            methodName = argumentList[0]
            argList = "" if len(argumentList) != 2 else argumentList[1]
            (status, returnValue) = _PerformRpcCall(methodName,argList)
            if (status == 0):
                self.send_response(200)     
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(json.dumps(returnValue))
            elif (status == -1):
                self.send_error(404,"Invalid ws call")  
            elif (status == -2):
                self.send_error(404,"Internal Exception")  
                
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)

__server = None

def StartServer(RpcWorkerClass, port):
    _SetRpcWorkerInstance(RpcWorkerClass)
    requestHandler = KetchLiteServerRequestHandler
    __server = SocketServer.TCPServer(("",port),requestHandler);
    try:
        __server.serve_forever()
    except KeyboardInterrupt:
        __server.shutdown()
    
def Shutdown():
    if (__server != None):
        __server.shutdown()
