from typing import Callable, Any, List, Tuple

class scheduler:
    def __init__(self) -> None:
        self.tasks_frame: List[Tuple[Callable, tuple, float]] = []
        self.tasks_schedule: List[Tuple[Callable, tuple, float]] = []

    def cancel_all(self) -> None:
        """cancels all scheduled tasks on both the frame and update threads."""
        self.tasks_frame.clear()
        self.tasks_schedule.clear()
    
    def update_frame(self, dt: float) -> None:
        """updates the frame scheduler, executing any tasks that are due and updating the time left for the remaining tasks.

        Args:
            dt (float): the time in seconds since the last update. The scheduler uses this to determine how much time has passed and whether any tasks are due to be executed.
        """
        next_tasks = []
        tasks_to_execute = []
        for func, args, time_left in self.tasks_frame:
            if time_left <= 0:
                tasks_to_execute.append((func, args))
            else:
                next_tasks.append((func, args, time_left - 60*dt))
        for func, args in tasks_to_execute:
            func(*args)
        self.tasks_frame = next_tasks

    def update_schedule(self, dt: float) -> None:
        """updates the scheduler, executing any tasks that are due and updating the time left for the remaining tasks.

        Args:
            dt (float): the time in seconds since the last update. The scheduler uses this to determine how much time has passed and whether any tasks are due to be executed.
        """
        next_tasks = []
        tasks_to_execute = []
        for func, args, time_left in self.tasks_schedule:
            if time_left <= 0:
                tasks_to_execute.append((func, args))
            else:
                next_tasks.append((func, args, time_left - 60*dt))
        for func, args in tasks_to_execute:
            func(*args)
        self.tasks_schedule = next_tasks

    def schedule_frame(self, Func: Callable, Delay: float, Args: tuple = ()) -> None:
        """schedules a function call on the frame thread after a certain delay in ticks (1/60th of a second).

        Args:
            Func (Callable): the function to call
            Delay (float): delay in ticks (1/60th of a second) before calling the function
            Args (tuple, optional): the argument to the function. Defaults to ().
        """
        self.tasks_frame.append((Func, Args, Delay))

    def schedule_update(self, Func: Callable, Delay: float, Args: tuple = ()) -> None:
        """schedules an function call on the update thread after a certain delay in ticks (1/60th of a second).

        Args:
            Func (Callable): the function to call
            Delay (float): delay in ticks (1/60th of a second) before calling the function
            Args (tuple, optional): the argument to the function. Defaults to ().
        """
        self.tasks_schedule.append((Func, Args, Delay))

    def cancel_frame(self, Func: Callable) -> Tuple[Callable, tuple, float]:
        """cancels a scheduled function call on the frame thread.

        Args:
            Func (Callable): the function to cancel

        Returns:
            Tuple[Callable, tuple, float]: the cancelled function, its arguments, and the time left until it would have been called. Returns None if no such function was found.
        """
        for i, (F, Args, TimeLeft) in enumerate(self.tasks_frame):
            if F == Func:
                del self.tasks_frame[i]
                return (F, Args, TimeLeft)
        return None

    def cancel_schedule(self, Func: Callable) -> Tuple[Callable, tuple, float]:
        """cancels a scheduled function call on the update thread.

        Args:
            Func (Callable): the function to cancel

        Returns:
            Tuple[Callable, tuple, float]: the cancelled function, its arguments, and the time left until it would have been called. Returns None if no such function was found.
        """
        for i, (F, Args, TimeLeft) in enumerate(self.tasks_schedule):
            if F == Func:
                del self.tasks_schedule[i]
                return (F, Args, TimeLeft)
        return None