import time
from .exceptions import NoSingleStartPointError, NoSingleEndPointError


class State(object):
    not_started = 'Not yet started'
    running = 'Running'
    done = 'Done'
    aborted = 'Aborted'


class Workflow(object):
    def __init__(self, *jobs):
        self.jobs = {}
        for j in jobs:
            self.jobs[j] = j

    def set_parents(self, obj, parents=[]):
        self.jobs[obj].parents = parents
        for p in parents:
            self.jobs[p].add_child(obj)

    def add_parents(self, obj, parents=[]):
        for p in parents:
            self.jobs[obj].add_parent(p)
            self.jobs[p].add_child(obj)

    def add_parent(self, obj, parent):
        self.add_parents(obj, parents=[parent])

    def set_children(self, obj, children=[]):
        self.jobs[obj].children = children
        for c in children:
            self.jobs[c].add_parent(obj)

    def add_children(self, obj, children=[]):
        for c in children:
            self.jobs[obj].add_child(c)
            self.jobs[c].add_parent(obj)

    def add_child(self, obj, child):
        self.add_children(obj, children=[child])

    def _get_endpoints(self):
        firsts = [x for x in self.jobs.keys() if not x.parents]
        if len(firsts) != 1:
            raise NoSingleStartPointError("We don't have a single start point")
        self.first = firsts[0]
        lasts = [x for x in self.jobs.keys() if not x.children]
        if len(lasts) != 1:
            raise NoSingleEndPointError("We don't have a single end point")
        self.last = lasts[0]

    @property
    def structure(self):
        self._get_endpoints()
        output = "Structure\n=========\n"
        output += "First: {}\n".format(self.first)
        output += "Last: {}\n".format(self.last)
        return output

    @property
    def runnables(self):
        return [x for x in self.jobs.keys() if x.runnable]

    def sleeper(self):
        """We assume that a job takes just a short time. If not, then we'll
        wait for a little longer. The max waittime will be 5 seconds"""
        for waittime in (.01, .02, .05, .1, .2, .5):
            yield waittime
        while True:
            waittime = min(waittime + .2, 5)
            yield waittime

    def summary(self):
        result = ''
        for j in self.jobs.keys():
            # if j.state_changed or j.msg_changed:
            result += "{}: {} ({})\n".format(j.name, j.state, j.msg)
        return result

    def run(self, show_summary=False):
        self._get_endpoints()
        sleeper = self.sleeper()
        oldrunnables = self.runnables
        while not all([j.state == State.done for j in self.jobs.keys()]):
            for job in self.runnables:
                job.work()
            if any([j.state == State.aborted for j in self.jobs.keys()]):
                if show_summary:
                    return (False, self.show_summary())
                else:
                    return False
            time.sleep(sleeper.next())
            if oldrunnables != self.runnables:
                oldrunnables = self.runnables
                sleeper = self.sleeper()
            if show_summary:
                print self.summary()
        if show_summary:
            return (True, self.summary())
        return True
