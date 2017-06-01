"""Yarn pool module."""

from threading import Thread
from time import sleep
from knit import Knit
from .remotepool import RemotePool, RemoteWorker


class YarnPool(RemotePool):
    """The Yarn Pool mananger."""

    def __init__(self, processes=None, port=0, authkey=None):
        super(YarnPool, self).__init__(processes=processes,
                                       port=port,
                                       authkey=authkey,
                                       workerscript=None)
        self.stopping = False
        self.k = Knit(autodetect=True)

        cmd = ('python remoteworker.py --port {} --key {}'
               .format(self.s.address[1], self.authkey))
        self.app_id = self.k.start(cmd,
                                   num_containers=self._processes,
                                   files=['joblibhadoop/yarn/remoteworker.py', ])
        self.t = Thread(target=self._monitor_appid)
        self.t.deamon = True
        self.t.start()

    def _start_remote_worker(self, pid):
        remote_worker = RemoteWorker(pid)
        self._pool.append(remote_worker)

    def _monitor_appid(self):
        while not self.stopping:
            try:
                status = self.k.status()
                yarn_state = status['app']['state']
                print("YARN application is {}".format(yarn_state))
            except:
                pass
            sleep(1)

    def terminate(self):
        self.stopping = True
        super(YarnPool, self).terminate()

        self.k.kill(self.app_id)
