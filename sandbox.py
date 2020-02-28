import clr

import time



clr.AddReference("System")
from System.Collections.Generic import List

clr.AddReference("System.Drawing")
from System.Drawing import *

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

#generate pseudorandom numbers as nodeID - import random is not available within dynamo
def pseudorandomid():
    time.sleep(0.025)
    _pseudo = str(int(round(time.time() * 1000)))
    _pseudo = _pseudo[-7:]
    _pseudo = str(hex(int(_pseudo)))

    return _pseudo

pseudorandomid()

from collections import MutableMapping

class warlock(MutableMapping):
    def __init__(self,debug=0):
        self.map = {} #map ids and user-defined name
        self.objects = {} #objects
        self.relations = [] #relationships [ ..., [parent, child], ...]

        self.containerid = pseudorandomid()

        self.debug = debug

        if debug:
            print('debugoutput enabled.')
            print('dbg: spawned container {}'.format(self.containerid))

    def __getitem__(self, _name):
        if self.map[_name]:

            if self.debug:
                print('dbg: __getitem__: _name:{0}; return {1}, {2}, {3}'.format(_name, self.objects[self.map[_name]], self.parents(_name), self.children(_name)))

            return self.objects[self.map[_name]], self.parents(_name), self.children(_name)
        else:
            raise Exception('{} does not exists!'.format(_name))

    def __delitem__(self, key):
        value = self[key]
        del self.objects[key]
        self.pop(value, None)
    def __setitem__(self, key, value):
        self.objects[key] = value
    def __iter__(self):
        return iter(self.objects)
    def __len__(self):
        return len(self.objects)
    def __repr__(self):
        return ({type(self).__name__},({self.objects}))

    def add(self,_name,_object,_parent='none'):
        if _name in self.map:
            raise Exception('{0} already exists in container {1}!'.format(_name,self.containerid))
        else:
            _objectid = pseudorandomid()
            if _objectid in self.objects:
                _objectid = pseudorandomid()
            else:
                self.map[_name] = _objectid

            self.objects[self.map[_name]] = _object

            if _parent == 'none':
                self.relations.append([self.containerid,self.map[_name]])
            elif _parent in self.map:
                self.relations.append([self.map[_parent], self.map[_name]])
            else:
                raise Exception('parentobject {} does not exists!'.format(_parent))

            if self.debug:
                print('dbg: spawned object {0} alias {1}, type: {2}, parent: {3}'.format(self.map[_name], _name, type(self.objects[self.map[_name]]), _parent))

    def myparents(self,_name):
        if _name in self.map:
            pass
            # if self.map[_name] in self.relations.values():
            #     print(self.map[_name])

    def parents(self, _child):  #get parents of object
        if self.map[_child]:
            for _parent,_c in self.relations:
                if _c == self.map[_child]:
                    return _parent
        else:
            raise Exception('no parent object found for {}!'.format(_child))

    def children(self, _parent):  #get children of object
        if self.map[_parent]:
            _children = []
            for _p,_child in self.relations:
                if _p == self.map[_parent]:
                    _children.append(_child)
            if _children:
                return _children
        else:
            raise Exception('no parent object found called {}!'.format(_name))

    def info(self,_name):
        if self.map[_name]:
            print('container: {0} > object {1} alias \'{2}\', child of: {3} | parent of: {4} '.format(self.containerid,self.map[_name],_name,self.parents(_name),self.children(_name)))
        else:
            raise Exception('{} does not exists!'.format(_name))

    def showall(self):
        if self.objects:
            print('---')
            print('showall')
            for _index, _containers in enumerate(self.map):
                self.info(_containers)
            print('{0} objects in container {1}'.format(_index+1,self.containerid))
            print('self.objects: {}'.format(self.objects))
            print('self.map: {}'.format(self.map))
            print('self.relations: {}'.format(self.relations))
            print('---')
        else:
            print('---')
            print('0 objects in container {}'.format( self.containerid))
            print('self.objects: {}'.format(self.objects))
            print('self.map: {}'.format(self.map))
            print('self.relations: {}'.format(self.relations))
            print('---')



_test = warlock(debug=1)
_test.add('f2oo', 'q')
_test.add('f3oo', 'abc', 'f2oo')
_test.add('f4oo', 'abc', 'f2oo')
_test.add('f5oo', 'abc', 'f3oo')
_test.add('f6oo', 'abc')
_test.add('f7oo', 'abc', 'f2oo')

_test.showall()

_test2 = warlock(debug=1)
_test2.showall()


#_test.info('f2oo')
#_test.info('f3oo')
#_test.parents('f3oo')

#print(_test.children('f2oo'))

#print(_test['f2oo'])
#print(_test.relations)

#_a =_test['f2oo']
#print(_a[0])




_window = Form()
_window.Text = 'foobar'

_tree = TreeView()

def recursivetree(_datasource):
    for _node in _datasource:
        if isinstance(_node, dict):
            _key = _node.keys()[0]
            if isinstance(_node[_key], list):
                print(_key)
                recursivetree(_node[_key])
            else:
                print(_node[_key])
        elif isinstance(_node, list):
            if isinstance(_item, dict):
                print(_item)
                recursivetree(_item)
            else:
                print(_item)
        elif isinstance(_node, str):
            print(_node)

# print(_nodesource[0].keys()[0])
#recursivetree(_nodesource)

# # _nodesource=[{'SESSIONS':[{'2019-12-1914:32:21$27334417user1':[{0:'0.0.0.0"client.network.local"'},{0:'201820181011_1500(x64)'},{0:'C:\\Users\\user1\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0459.txt'}]},{'2019-12-2007:34:38$6f58511duser2':[{1:'0.0.0.0"client.network.local"'},{1:'201820190510_1515(x64)'},{1:'C:\\Users\\user2\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.1612.txt'}]},{'2019-12-2008:20:25$adead140user3':[{2:'0.0.0.0"client.network.local"'},{2:'201820190510_1515(x64)'},{2:'C:\\Users\\user3\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0448.txt'}]},{'2019-12-2008:34:28$9cc4b776user4':[{3:'0.0.0.0"client.network.local"'},{3:'201820181011_1500(x64)'},{3:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0240.txt'}]},{'2019-12-2009:21:02$19cf14c8user5':[{4:'0.0.0.0"client.network.local"'},{4:'201820190510_1515(x64)'},{4:'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0148.txt'}]},{'2019-12-2009:58:43$b812a7c5user5':[{5:'0.0.0.0"client.network.local"'},{5:'201820190510_1515(x64)'},{5:'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0149.txt'}]},{'2019-12-2014:36:26$94f1d542user5':[{6:'0.0.0.0"client.network.local"'},{6:'201820190510_1515(x64)'},{6:'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0149.txt'}]},{'2019-12-2016:59:34$0a669c43user4':[{7:'0.0.0.0"client.network.local"'},{7:'201820181011_1500(x64)'},{7:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0242.txt'}]},{'2019-12-2106:20:12$a5018e04user1':[{8:'0.0.0.0"client.network.local"'},{8:'201820181011_1500(x64)'},{8:'C:\\Users\\user1\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0461.txt'}]},{'2019-12-2107:47:39$b280cd0auser2':[{9:'0.0.0.0"client.network.local"'},{9:'201820190510_1515(x64)'},{9:'C:\\Users\\user2\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.1616.txt'}]},{'2019-12-2108:58:55$ea76f65auser4':[{10:'0.0.0.0"client.network.local"'},{10:'201820181011_1500(x64)'},{10:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0243.txt'}]},{'2019-12-2109:00:57$0bca6298user5':[{11:'0.0.0.0"client.network.local"'},{11:'201820190510_1515(x64)'},{11:'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0150.txt'}]},{'2019-12-2111:47:44$7c83d5ccuser6':[{12:'0.0.0.0"client.network.local"'},{12:'201820190510_1515(x64)'},{12:'D:\\Users\\user6\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0669.txt'}]},{'2019-12-2114:16:40$bcf01571user4':[{13:'0.0.0.0"client.network.local"'},{13:'201820181011_1500(x64)'},{13:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}]},{'2019-12-2114:27:54$60e0791euser4':[{14:'0.0.0.0"client.network.local"'},{14:'201820181011_1500(x64)'},{14:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}]},{'2019-12-2118:11:12$fbe65beauser4':[{15:'0.0.0.0"client.network.local"'},{15:'201820181011_1500(x64)'},{15:'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}]}]}]
# _nodesource = [
#     {'2019-12-1914:32:21$27334417user1': [
#         {0: '0.0.0.0"client.network.local"'}, {0: '201820181011_1500(x64)'},
#         {0: 'C:\\Users\\user1\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0459.txt'}
#     ]}, {'2019-12-2007:34:38$6f58511duser2': [
#         {1: '0.0.0.0"client.network.local"'}, {1: '201820190510_1515(x64)'},
#         {1: 'C:\\Users\\user2\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.1612.txt'}
#     ]}, {'2019-12-2008:20:25$adead140user3': [
#         {2: '0.0.0.0"client.network.local"'}, {2: '201820190510_1515(x64)'},
#         {2: 'C:\\Users\\user3\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0448.txt'}
#     ]}, {'2019-12-2008:34:28$9cc4b776user4': [
#         {3: '0.0.0.0"client.network.local"'}, {3: '201820181011_1500(x64)'},
#         {3: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0240.txt'}
#     ]}, {'2019-12-2009:21:02$19cf14c8user5': [
#         {4: '0.0.0.0"client.network.local"'}, {4: '201820190510_1515(x64)'},
#         {4: 'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0148.txt'}
#     ]}, {'2019-12-2009:58:43$b812a7c5user5': [
#         {5: '0.0.0.0"client.network.local"'}, {5: '201820190510_1515(x64)'},
#         {5: 'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0149.txt'}
#     ]}, {'2019-12-2014:36:26$94f1d542user5': [
#         {6: '0.0.0.0"client.network.local"'}, {6: '201820190510_1515(x64)'},
#         {6: 'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0149.txt'}
#     ]}, {'2019-12-2016:59:34$0a669c43user4': [
#         {7: '0.0.0.0"client.network.local"'}, {7: '201820181011_1500(x64)'},
#         {7: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0242.txt'}
#     ]}, {'2019-12-2106:20:12$a5018e04user1': [
#         {8: '0.0.0.0"client.network.local"'}, {8: '201820181011_1500(x64)'},
#         {8: 'C:\\Users\\user1\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0461.txt'}
#     ]}, {'2019-12-2107:47:39$b280cd0auser2': [
#         {9: '0.0.0.0"client.network.local"'}, {9: '201820190510_1515(x64)'},
#         {9: 'C:\\Users\\user2\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.1616.txt'}
#     ]}, {'2019-12-2108:58:55$ea76f65auser4': [
#         {10: '0.0.0.0"client.network.local"'}, {10: '201820181011_1500(x64)'},
#         {10: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0243.txt'}
#     ]}, {'2019-12-2109:00:57$0bca6298user5': [
#         {11: '0.0.0.0"client.network.local"'}, {11: '201820190510_1515(x64)'},
#         {11: 'C:\\Users\\user5\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0150.txt'}
#     ]}, {'2019-12-2111:47:44$7c83d5ccuser6': [
#         {12: '0.0.0.0"client.network.local"'}, {12: '201820190510_1515(x64)'},
#         {12: 'D:\\Users\\user6\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0669.txt'}
#     ]}, {'2019-12-2114:16:40$bcf01571user4': [
#         {13: '0.0.0.0"client.network.local"'}, {13: '201820181011_1500(x64)'},
#         {13: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}
#     ]}, {'2019-12-2114:27:54$60e0791euser4': [
#         {14: '0.0.0.0"client.network.local"'}, {14: '201820181011_1500(x64)'},
#         {14: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}
#     ]}, {'2019-12-2118:11:12$fbe65beauser4': [
#         {15: '0.0.0.0"client.network.local"'}, {15: '201820181011_1500(x64)'},
#         {15: 'C:\\Users\\user4\\AppData\\Local\\Autodesk\\Revit\\AutodeskRevit2018\\Journals\\journal.0244.txt'}
#     ]},
#     {'SYNCTOCENTRAL': {'0': 'synclist'}}
# ]
#
# # _nodesource=[
# ##'sessions',
# # {'sessions0':
# # [{'session0.0':"value0.0"},
# # {'session0.1':"value0.1"}]
# # },
# # {'syncs1':
# # [{'sync1.0':"value1.0"},
# # {'sync1.1':[
# # {'sync1.1.0':"value1.1.0"},
# # {'sync1.1.1':"value1.1.1"}
# # ]},
# # {'sync1.2':"value1.2"}]
# # },
# # {'crashes2':
# # [{"crash2.0":"value2.0"}]
# # },
# # {'empty3':''},#TODO:oneliner
# ##['list','of','things'],
# # 'string'
# # ]
#
# # _nodesource=[{'dummy0':'dummy0v'}]
# # for_itemin_nodesource:
# # print(_item)
