from threading import Thread, Lock
import time

class Node: 
    def __init__(self, item, _id):
        self.item = item
        self._id = _id
    def toString(self): 
        return "{ id: " + str(self._id) + ", item: " + str(self.item) +" }"

class Queue:
    nodes = []
    currentId = 0
    orph = []
    lock = Lock()

    def put(self, item):
        self.lock.acquire()
        self.currentId += 1
        self.nodes.insert(0, Node(item, self.currentId))
        self.lock.release()
        return self.currentId
    
    def pop(self):
        self.lock.acquire()
        if len(self.nodes) > 0:
            node = self.nodes.pop()
        else: 
            node = None

        if node is not None: 
            self.orph.append(node)
        self.lock.release()

        return node

    def commit(self, node):
        return self.removeOrph(node)

    def rollback(self, node):
        if self.removeOrph(node): 
            self.nodes.insert(0, node)
            return True
        return False
            
    def removeOrph(self, node):
        self.lock.acquire()
        isSuc = False
        try:
            if node is not None and self.orph.index(node) > 0:
                self.orph.remove(node)
                isSuc = True
        except ValueError:
            pass
        finally:
            self.lock.release()
            return isSuc
        
    def getorph(self): 
        return self.orph
    
    def size(self):
        return len(self.nodes)

    def sizeOrph(self): 
        return len(self.orph)
    
    def toString(self):
        nodes = []
        for node in self.nodes and self.orph.index(node) > 0:
            nodes.append(node.toString())
        return str(nodes)

    def toOrphString(self):
        nodes = []
        for node in self.orph:
            nodes.append(node.toString())
        return str(nodes)

    def getIds(self):
        ids = []
        for node in self.nodes:
            ids.append(node._id)
        return ids

# ========= TEST ========

_queue = Queue()

commitCount = 0
def commit():
    for k in range(0, 102400):
        for node in _queue.orph:
            global commitCount 
            if _queue.commit(node):
                commitCount += 1

rollbackCount = 0
def rollback():
    for k in range(0, 102400):
        for node in _queue.orph:
            global rollbackCount 
            if _queue.rollback(node):
                rollbackCount += 1

def put():
    for k in range(0, 102400):
        _queue.put(k)

def pop(): 
    for k in range(0, 102400):
        _queue.pop()


if __name__ == '__main__':
    ts = []
    for k in range(0, 2): 
        ts.append(Thread(target=put, args=()))
        ts.append(Thread(target=pop, args=()))
        ts.append(Thread(target=commit, args=()))
        ts.append(Thread(target=rollback, args=()))

    for t in ts: 
        t.start()
    
    for t in ts: 
        t.join()

    count = _queue.size()
    sizeOrph = _queue.sizeOrph()
    
    print(commitCount)
    print(rollbackCount)
    print(count)
    print(sizeOrph)
    print(count + sizeOrph)
    