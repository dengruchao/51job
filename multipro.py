from threading import Thread, Lock
from Queue import Queue

queue = Queue() #thread pool
lock = Lock()

def Request(url, callback):
    queue.put((url, callback))

class DownloadWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url, callback = self.queue.get()
            if url is None:
                break
            print 'Downloading:', url
            callback(url)
            self.queue.task_done()

