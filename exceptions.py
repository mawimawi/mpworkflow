class ParentError(Exception):
    pass


class WorkflowError(Exception):
    pass


class NoSingleStartPointError(WorkflowError):
    pass

class NoSingleEndPointError(WorkflowError):
    pass
