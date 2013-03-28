#!/usr/bin/env python

import multiprocessing
from workflow import State


def dummyrunner(namespace, *a, **k):
    namespace.state = State.done


class Job(object):
    def __init__(self, name, runner=None):
        self.name = name
        self.runner = runner or dummyrunner  # dummyrunner does nothing.
        self.parents = []
        self.children = []

        self.mp_mgr = multiprocessing.Manager()
        self.mp_namespace = self.mp_mgr.Namespace()
        self.mp_namespace.state = State.not_started
        self.mp_namespace.msg = ''
        self._old_msg = self.mp_namespace.msg
        self._old_state = self.mp_namespace.state

    @property
    def state(self):
        return self.mp_namespace.state

    @property
    def msg(self):
        return self.mp_namespace.msg

    @property
    def msg_changed(self):
        if self._old_msg != self.msg:
            self._old_msg = self.msg
            return True
        return False

    @property
    def state_changed(self):
        if self._old_state != self.state:
            self._old_state = self.state
            return True
        return False

    @property
    def parents_done(self):
        return all([p.state == State.done for p in self.parents])

    @property
    def runnable(self):
        if self.mp_namespace.state in (State.not_started, State.running):
            if not self.parents:
                return True
            if self.parents_done:
                return True
        return False

    def work(self, *a, **k):
        if self.mp_namespace.state == State.not_started:
            # first run!
            self.mp_namespace.state = State.running
            self.mp_process = multiprocessing.Process(
                target=self.runner,
                args=(self.mp_namespace,))
            self.mp_process.start()

        if self.mp_namespace.state in (State.done, State.aborted):
            self.mp_process.join()

    def add_child(self, job):
        if job not in self.children:
            self.children.append(job)

    def add_parent(self, job):
        if job not in self.parents:
            self.parents.append(job)

    def __str__(self):
        return self.name
    __repr__ = __str__
