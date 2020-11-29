
import subprocess,datetime,select,time,logging,threading
from systemd import journal


DEBUG=True
# DEBUG=False

class Procs:
    def __init__(self):
        self.procs = [None, None]
        self.quarantines = [0, 0]
        self.debug_on = False

    def launch(self, command):
        try:
            proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.error('Procs::launch(%s)->Exception: %s', str(command), str(e))
            proc = None
        return proc

    def terminate(self,i):
        try:
            logging.debug('About to terminate(%d)', i)
            self.procs[i].terminate()
            logging.debug('Done terminate(%d)', i)
        except Exception as e:
            logging.error('Procs::terminate(%d)->Exception: %s', i, str(e))
        self.procs[i] = None

    def start(self):
        if DEBUG:
            self.debug_on = True
            return
        if self.procs[0] is None:
            if self.quarantines[0] <= 0:
                self.procs[0] = self.launch(['python3','run1.py'])
            else:
                self.quarantines[0] -= 1
        if self.procs[1] is None:
            if self.quarantines[1] <= 0:
                self.procs[1] = self.launch(['./dls2_1', ])
            else:
                self.quarantines[1] -= 1

    def stop(self):
        if self.procs[0]: self.terminate(0)
        if self.procs[1]: self.terminate(1)
        self.debug_on = False

    def check(self):
        for i in range(len(self.procs)):
            if self.procs[i]:
                res = self.procs[i].poll()
                if res is not None:
                    logging.warning('procs.check()->proc[%d].poll(): %s', i, str(res))
                    self.procs[i] = None
                    self.quarantines[i] = 3

    def some(self):
        if DEBUG: return self.debug_on
        return self.procs[0] or self.procs[1]

    def not_all(self):
        if DEBUG: return not self.debug_on
        return self.procs[0] is None or self.procs[1] is None


class TimeTask(threading.Thread):
    def run(self):
        while True:
            tz = TimeZones()
            if not tz.isWhite():
                import os
                os._exit(0)
            time.sleep(93)

class Task:
    def run(self):
        if DEBUG:
            while True:
                time.sleep(3)
                print("From Task::run() hola")
        else:
            from nuxhash.daemon import main
            main()

    def start(self):
        import threading
        th = threading.Thread(target=self.run)
        th.daemon = True
        th.start()

class TimeZones:
    zw = (0,500)
    zb = (800,1700)
    def __init__(self):
        self.dt_now = datetime.datetime.now()
    def isin(self,tzi):
        return ((self.dt_now.hour * 100 + self.dt_now.minute) > tzi[0]) and (
                    (self.dt_now.hour * 100 + self.dt_now.minute) < tzi[1])
    def isWhite(self):
        return self.isin(self.zw)
    def isBlack(self):
        return self.isin(self.zb) and self.dt_now.weekday() < 5

def main3():
    while True:
        tz = TimeZones()
        if tz.isWhite():
            break
        time.sleep(97)
    TimeTask().start()
    if DEBUG:
        while True:
            time.sleep(3)
            print("From main3() hola")
    else:
        from nuxhash.daemon import main
        main()

def main2():
    if DEBUG:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(filename='sched.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    logging.debug('sched_onoff::main2() init')
    task = None
    while True:
        tz = TimeZones()
        if task:
            if not tz.isWhite():
                logging.info('sched_onoff::main2() about to stop')
                import os
                os._exit(0)
        elif tz.isWhite():
            logging.info('sched_onoff::main2() starting task')
            task = Task()
            task.start()
        time.sleep(97)

def listen_who(wait_max_secs):
    j = journal.Reader()
    j.seek_tail()
    j.log_level(journal.LOG_INFO)
    j.add_match(_SYSTEMD_UNIT="ssh.service")
    p = select.poll()
    p.register(j, j.get_events())
    return p.poll(wait_max_secs * 1000)

def main():
    inith = 18
    if DEBUG:
        inith = 0
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(filename='sched.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    logging.info('Starting (Inith: %d)', inith)
    procs = Procs()
    wait_secs = 23
    last_quiet = False
    bEvent = False
    cnt = 97

    while True:
        dt_now = datetime.datetime.now()
        try:
            if bEvent and (last_quiet or DEBUG):
                logging.info('Event: %s, hour: %d, last_quiet: %s, wait_secs: %d', str(bEvent), dt_now.hour,
                              str(last_quiet), wait_secs)
            procs.check()
            who_cmd = ['sh', '-c', 'who | grep -v tmux | grep -v mmas']
            if DEBUG: who_cmd = ['sh', '-c', 'who | grep -v tmux | grep isil']
            whop = subprocess.Popen(who_cmd, stdout=subprocess.PIPE)
            stdout,_ = whop.communicate()
            quiet = not stdout
            if quiet != last_quiet:
                logging.info('Quiet: %s, hour: %d, last_quiet: %s, wait_secs: %d, event: %s, cnt: %d', str(quiet), dt_now.hour,
                              str(last_quiet), wait_secs, str(bEvent), cnt)
            last_quiet = quiet
            if bEvent and quiet:
                wait_secs = 1
                cnt = 1
            elif quiet and cnt < 97:
                wait_secs = 1
                cnt += 1
            else:
                wait_secs = 23
            logging.debug('Quiet: %s, hour: %d, last_quiet: %s, wait_secs: %d, event: %s, cnt: %d', str(quiet), dt_now.hour, str(last_quiet), wait_secs, str(bEvent), cnt)
        except Exception as e:
            logging.error("sched_onoff(who)->Exception: %s", str(e))
            quiet = False
        #if procs.not_all() and ((dt_now.hour >= 23 or dt_now.hour < 7) or (quiet and (dt_now.hour >= inith or dt_now.hour < 8 or dt_now.weekday() > 4))):
        # if procs.not_all() and quiet and (dt_now.hour >= inith or dt_now.hour < 8 or dt_now.weekday() > 4):
        if procs.not_all() and ((dt_now.hour > 0 and dt_now.hour < 5) or (quiet and (dt_now.hour >= inith or dt_now.hour < 8 or dt_now.weekday() > 4))):
            logging.info('sched_onoff: starting processes')
            procs.start()
        # elif procs.some() and not quiet: # and (dt_now.hour > 6 and dt_now.hour < 23):
        elif procs.some() and not quiet and (dt_now.hour > 4 or dt_now.hour < 1):
            logging.info('sched_onoff: about to stop processes')
            procs.stop()
            logging.info('ched_onoff: terminating processes')
        bEvent = listen_who(wait_secs)


if __name__ == '__main__':
    main()