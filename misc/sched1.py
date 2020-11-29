
import subprocess,logging,datetime


DEBUG=True
DEBUG=False

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


LOG_STDOUT=False
#LOG_STDOUT=True

def wparse():
    whop = subprocess.Popen(['w', '-sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = whop.communicate()
    if stderr:
        logging.error('Error: %s', stderr)
        return False
    # print('Stdout:')
    bLiveConnection = False
    bRecentCommand = False
    bTopCommand = False
    for line in stdout.decode("utf-8").splitlines():
        # print(line)
        user = line[:8].strip()
        if user.startswith('mmasenl'): continue
        from_ = line[18:35].strip()
        idle = line[35:42].strip()
        cmd = line[42:]
        if user.startswith('tmux('):
            if 'nvidia-' in cmd: bTopCommand = True
            if cmd.strip().startswith('htop') or cmd.strip().startswith('top'): bTopCommand = True
            continue
        bLiveConnection = True
        if 'd' in idle:
            pass
        elif 'm' in idle:
            # print(idle[:-1],'minutes idle')
            h_m = idle[:-1].split(':')
            minutes = int(h_m[0])*60 + int(h_m[1])
            if minutes < 150: bRecentCommand = True
        else:
            bRecentCommand = True
        if 'nvidia-' in cmd: bTopCommand = True
        if cmd.strip().startswith('htop') or cmd.strip().startswith('top'): bTopCommand = True

    logging.debug('wparse() bLiveConnection: %s, bRecentCommand: %s, bTopCommand: %s', str(bLiveConnection),
                  str(bRecentCommand), str(bTopCommand))
    if not bLiveConnection: return True
    if bRecentCommand: return False
    if not bTopCommand: return True
    tt = datetime.datetime.now()
    if tt.hour > 23 or tt.hour < 7: return True

def main():
    # if DEBUG or LOG_STDOUT:
    #     # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    #     logging.basicConfig(filename='debug.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    # else:
    #     logging.basicConfig(filename='sched.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    logging.basicConfig(filename='debug.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

    logging.info('Starting')
    procs = Procs()
    wait_secs = 23
    last_quiet = False
    bEvent = False
    cnt = 97

    while True:
        try:
            if bEvent:
                logging.debug('Event: %s, last_quiet: %s, wait_secs: %d', str(bEvent),
                              str(last_quiet), wait_secs)
            procs.check()
            # who_cmd = ['sh', '-c', 'w -sh|grep -v \'tmux(\'|grep -v mmas|awk \'{print $4}\'|grep -v days|grep -v m']
            # whop = subprocess.Popen(who_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # stdout,stderr = whop.communicate()
            # logging.debug('stdout: %s, stderr: %s', stdout, stderr)
            quiet = wparse()
            if quiet != last_quiet:
               logging.info('Quiet: %s, last_quiet: %s, wait_secs: %d, event: %s, cnt: %d', str(quiet),
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
            logging.debug('Quiet: %s, last_quiet: %s, wait_secs: %d, event: %s, cnt: %d', str(quiet), str(last_quiet), wait_secs, str(bEvent), cnt)
        except Exception as e:
            logging.error("sched_onoff(who)->Exception: %s", str(e))
            quiet = False
        if procs.not_all() and quiet: # and datetime.datetime.now().hour < 5:
            logging.info('sched_onoff: starting processes')
            procs.start()
        elif procs.some() and not quiet:
            logging.info('sched_onoff: about to stop processes')
            procs.stop()
            logging.info('ched_onoff: terminating processes')
        inotifywait_cmd = ['inotifywait', '-e', 'access', '-t', str(wait_secs), '/dev/pts']
        inop = subprocess.Popen(inotifywait_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        stdout, _ = inop.communicate()
        bEvent = not not stdout

if __name__ == '__main__':
    main()
