from typing import Callable, Any, List, Tuple

class Scheduler:
    def __init__(self) -> None:
        self.tasks_frame: List[Tuple[Callable, tuple, int]] = []
        self.Tasks_schedule: List[Tuple[Callable, tuple, int]] = []

    def update_frame(self) -> None:
        NextTasks = []
        TasksToExecute = []
        for Func, Args, TimeLeft in self.tasks_frame:
            if TimeLeft <= 0:
                TasksToExecute.append((Func, Args))
            else:
                NextTasks.append((Func, Args, TimeLeft - 1))
        for Func, Args in TasksToExecute:
            Func(*Args)
        self.tasks_frame = NextTasks

    def update_schedule(self) -> None:
        NextTasks = []
        TasksToExecute = []
        for Func, Args, TimeLeft in self.Tasks_schedule:
            if TimeLeft <= 0:
                TasksToExecute.append((Func, Args))
            else:
                NextTasks.append((Func, Args, TimeLeft - 1))
        for Func, Args in TasksToExecute:
            Func(*Args)
        self.Tasks_schedule = NextTasks

    def schedule_frame(self, Func: Callable, Delay: int, Args: tuple = ()) -> None:
        self.tasks_frame.append((Func, Args, Delay))

    def schedule_update(self, Func: Callable, Delay: int, Args: tuple = ()) -> None:
        self.Tasks_schedule.append((Func, Args, Delay))

    def cancel_frame(self, Func: Callable) -> Tuple[Callable, tuple, int]:
        for i, (F, Args, TimeLeft) in enumerate(self.tasks_frame):
            if F == Func:
                del self.tasks_frame[i]
                return (F, Args, TimeLeft)
        return None

    def cancel_schedule(self, Func: Callable) -> Tuple[Callable, tuple, int]:
        for i, (F, Args, TimeLeft) in enumerate(self.Tasks_schedule):
            if F == Func:
                del self.Tasks_schedule[i]
                return (F, Args, TimeLeft)
        return None