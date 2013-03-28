from unittest import TestCase

from job import Job
from .workflow import Workflow, State
from .exceptions import NoSingleStartPointError, NoSingleEndPointError


class StandardCase(TestCase):
    def test_01_morning(self):
        aufstehen = Job('Aufstehen')
        kaffee = Job('Kaffee kochen')
        duschen = Job('Duschen')
        anziehen = Job('Anziehen')
        fruehstueck = Job('Kaffee trinken')
        raus = Job('Wohnung verlassen')

        w = Workflow(aufstehen, kaffee, duschen, anziehen, fruehstueck, raus)
        w.set_children(aufstehen, [kaffee, duschen])
        w.set_children(kaffee, [fruehstueck, ])
        w.set_children(duschen, [anziehen, ])
        w.set_children(anziehen, [fruehstueck, ])
        w.set_children(fruehstueck, [raus, ])

        w.structure
        self.assertEqual(True, w.run())

    def test_04_from_child_to_parent(self):
        j1 = Job("Job One")
        j2 = Job("Job Two")
        w = Workflow(j1, j2)
        w.set_parents(j2, (j1,))
        self.assertEqual(True, w.run())

    def test_05_add_children(self):
        j1 = Job("Job One")
        j2 = Job("Job Two")
        j3 = Job("Job Three")
        w = Workflow(j1, j2, j3)
        w.add_children(j1, [j2])
        w.add_children(j2, [j3])
        self.assertEqual(True, w.run())

    def test_06_no_single_start_point(self):
        j1 = Job("Job One")
        j2 = Job("Job Two")
        j3 = Job("Job Three")
        w = Workflow(j1, j2, j3)
        w.add_children(j2, [j3])
        w.add_children(j1, [j3])
        self.assertRaises(NoSingleStartPointError, w.run)

    def test_07_no_single_end_point(self):
        j1 = Job("Job One")
        j2 = Job("Job Two")
        j3 = Job("Job Three")
        w = Workflow(j1, j2, j3)
        w.add_children(j1, [j2, j3])
        self.assertRaises(NoSingleEndPointError, w.run)

    def test_08_aborted_process(self):
        def failrunner(namespace, *a, **k):
            namespace.state = State.aborted
        j1 = Job("Job One")
        j2 = Job("Job Two", runner=failrunner)
        j3 = Job("Job Three")
        w = Workflow(j1, j2, j3)
        w.add_children(j1, [j2])
        w.add_children(j2, [j3])
        self.assertEqual(False, w.run())

    def test_09_many_processes(self):
        def slowmprunner(namespace, *a, **k):
            namespace.msg = "slow 1"
            res = 0.0
            for x in range(1, 1000):
                for y in range(1, 1000):
                    res += x
                    res = res / y
                namespace.msg = "x is {}".format(x)
            namespace.msg = "phew. that was hard work!"
            namespace.state = State.done

        midjobs = [Job("Job {}".format(x), runner=slowmprunner) for x in range(20)]
        j0 = Job("Job Zero")
        j3 = Job("Job Three")
        alljobs = [j0] + midjobs + [j3]
        w = Workflow(*alljobs)
        w.set_children(j0, midjobs)
        w.set_parents(j3, midjobs)
        result = w.run(show_summary=True)
        self.assertEqual(True, result[0])
        for x in range(20):
            self.assertIn('Job {}: Done'.format(x), result[1])
