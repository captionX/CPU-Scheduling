class Process:
    """
    Represents a process with attributes needed for scheduling algorithms.
    """
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        """
        Initialize a new process.
        
        Args:
            pid (int): Process ID
            arrival_time (int): Time at which process arrives in the ready queue
            burst_time (int): Total execution time required by the process
            priority (int, optional): Priority of the process (lower value means higher priority)
        """
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time  # For preemptive algorithms
        self.start_time = -1  # Will be set during scheduling
        self.completion_time = -1  # Will be set during scheduling
        self.waiting_time = -1  # Will be calculated
        self.turnaround_time = -1  # Will be calculated
        self.response_time = -1  # Will be calculated

    def __str__(self):
        """String representation of the process."""
        return f"Process {self.pid} (Arrival: {self.arrival_time}, Burst: {self.burst_time}, Priority: {self.priority})"

    def is_completed(self):
        """Check if process has completed execution."""
        return self.remaining_time <= 0

    def execute(self, time_quantum=None):
        """
        Execute the process for a given time quantum.
        
        Args:
            time_quantum (int, optional): Time for which process executes (for RR)
                                         If None, process runs to completion
        
        Returns:
            int: Time for which the process executed
        """
        if time_quantum is None or time_quantum >= self.remaining_time:
            executed_time = self.remaining_time
            self.remaining_time = 0
        else:
            executed_time = time_quantum
            self.remaining_time -= time_quantum
            
        return executed_time

    def reset(self):
        """Reset the process state for a new scheduling simulation."""
        self.remaining_time = self.burst_time
        self.start_time = -1
        self.completion_time = -1
        self.waiting_time = -1
        self.turnaround_time = -1
        self.response_time = -1
