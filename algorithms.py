from collections import deque
from process import Process
from typing import List, Dict, Any, Tuple

def fcfs(processes: List[Process]) -> Tuple[List[Dict[str, Any]], List[Process]]:
    """
    First Come First Serve scheduling algorithm.
    
    Args:
        processes (List[Process]): List of processes to schedule
        
    Returns:
        Tuple containing:
        - List of execution timeline dictionaries
        - List of scheduled processes with calculated metrics
    """
    # Create a copy of the processes to avoid modifying the original
    processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    current_time = 0
    timeline = []
    
    for process in processes:
        # If there's a gap between processes, add idle time
        if current_time < process.arrival_time:
            if current_time > 0:  # Don't add idle at the beginning
                timeline.append({
                    'pid': None,
                    'start_time': current_time,
                    'end_time': process.arrival_time,
                    'duration': process.arrival_time - current_time
                })
            current_time = process.arrival_time
        
        # Set process start time if it's the first time it's running
        if process.start_time == -1:
            process.start_time = current_time
        
        # Execute the process
        execution_time = process.execute()
        
        # Add to timeline
        timeline.append({
            'pid': process.pid,
            'start_time': current_time,
            'end_time': current_time + execution_time,
            'duration': execution_time
        })
        
        # Update current time
        current_time += execution_time
        
        # Set completion time
        process.completion_time = current_time
        
        # Calculate metrics
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        process.response_time = process.start_time - process.arrival_time
    
    return timeline, processes

def sjf_non_preemptive(processes: List[Process]) -> Tuple[List[Dict[str, Any]], List[Process]]:
    """
    Shortest Job First (Non-preemptive) scheduling algorithm.
    
    Args:
        processes (List[Process]): List of processes to schedule
        
    Returns:
        Tuple containing:
        - List of execution timeline dictionaries
        - List of scheduled processes with calculated metrics
    """
    # Create a copy of the processes to avoid modifying the original
    processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    current_time = 0
    timeline = []
    remaining_processes = processes.copy()
    completed_processes = []
    
    while remaining_processes:
        # Find available processes
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes:
            # No process available, move time to next process arrival
            next_arrival = min(p.arrival_time for p in remaining_processes)
            if current_time < next_arrival:
                timeline.append({
                    'pid': None,
                    'start_time': current_time,
                    'end_time': next_arrival,
                    'duration': next_arrival - current_time
                })
            current_time = next_arrival
            continue
        
        # Select process with shortest burst time
        selected_process = min(available_processes, key=lambda p: p.burst_time)
        
        # Set process start time if it's the first time it's running
        if selected_process.start_time == -1:
            selected_process.start_time = current_time
        
        # Execute the process
        execution_time = selected_process.execute()
        
        # Add to timeline
        timeline.append({
            'pid': selected_process.pid,
            'start_time': current_time,
            'end_time': current_time + execution_time,
            'duration': execution_time
        })
        
        # Update current time
        current_time += execution_time
        
        # Set completion time
        selected_process.completion_time = current_time
        
        # Calculate metrics
        selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
        selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
        selected_process.response_time = selected_process.start_time - selected_process.arrival_time
        
        # Move process from remaining to completed
        remaining_processes.remove(selected_process)
        completed_processes.append(selected_process)
    
    return timeline, completed_processes

def sjf_preemptive(processes: List[Process]) -> Tuple[List[Dict[str, Any]], List[Process]]:
    """
    Shortest Job First (Preemptive) / Shortest Remaining Time First scheduling algorithm.
    
    Args:
        processes (List[Process]): List of processes to schedule
        
    Returns:
        Tuple containing:
        - List of execution timeline dictionaries
        - List of scheduled processes with calculated metrics
    """
    # Create a copy of the processes to avoid modifying the original
    processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    current_time = 0
    timeline = []
    remaining_processes = processes.copy()
    completed_processes = []
    
    # Track the previously running process
    current_process = None
    
    while remaining_processes:
        # Find available processes
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes:
            # No process available, move time to next process arrival
            next_arrival = min(p.arrival_time for p in remaining_processes)
            if current_time < next_arrival:
                timeline.append({
                    'pid': None,
                    'start_time': current_time,
                    'end_time': next_arrival,
                    'duration': next_arrival - current_time
                })
            current_time = next_arrival
            current_process = None
            continue
        
        # Select process with shortest remaining time
        selected_process = min(available_processes, key=lambda p: p.remaining_time)
        
        # Check if we're switching processes
        if current_process != selected_process:
            # Set process start time if it's the first time it's running
            if selected_process.start_time == -1:
                selected_process.start_time = current_time
            current_process = selected_process
        
        # Find next arrival or completion event
        next_event_time = float('inf')
        for p in remaining_processes:
            if p.arrival_time > current_time and p.arrival_time < next_event_time:
                next_event_time = p.arrival_time
        
        # If no new arrivals before completion, process runs until completion
        if next_event_time == float('inf'):
            execution_time = selected_process.remaining_time
        else:
            # Execute until next event
            execution_time = min(selected_process.remaining_time, next_event_time - current_time)
        
        # Update remaining time
        selected_process.remaining_time -= execution_time
        
        # Add to timeline
        timeline.append({
            'pid': selected_process.pid,
            'start_time': current_time,
            'end_time': current_time + execution_time,
            'duration': execution_time
        })
        
        # Update current time
        current_time += execution_time
        
        # Check if process completed
        if selected_process.remaining_time == 0:
            selected_process.completion_time = current_time
            selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
            selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
            selected_process.response_time = selected_process.start_time - selected_process.arrival_time
            
            # Move process from remaining to completed
            remaining_processes.remove(selected_process)
            completed_processes.append(selected_process)
            current_process = None
    
    return timeline, completed_processes

def priority_scheduling(processes: List[Process], preemptive=False) -> Tuple[List[Dict[str, Any]], List[Process]]:
    """
    Priority Scheduling algorithm (can be preemptive or non-preemptive).
    
    Args:
        processes (List[Process]): List of processes to schedule
        preemptive (bool): Whether to use preemptive scheduling
        
    Returns:
        Tuple containing:
        - List of execution timeline dictionaries
        - List of scheduled processes with calculated metrics
    """
    # Create a copy of the processes to avoid modifying the original
    processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    current_time = 0
    timeline = []
    remaining_processes = processes.copy()
    completed_processes = []
    
    # Track the previously running process
    current_process = None
    
    while remaining_processes:
        # Find available processes
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes:
            # No process available, move time to next process arrival
            next_arrival = min(p.arrival_time for p in remaining_processes)
            if current_time < next_arrival:
                timeline.append({
                    'pid': None,
                    'start_time': current_time,
                    'end_time': next_arrival,
                    'duration': next_arrival - current_time
                })
            current_time = next_arrival
            current_process = None
            continue
        
        # Select process with highest priority (lowest priority number)
        selected_process = min(available_processes, key=lambda p: p.priority)
        
        # For non-preemptive, if a process is already running, continue with it
        if not preemptive and current_process and current_process in available_processes:
            selected_process = current_process
        
        # Check if we're switching processes
        if current_process != selected_process:
            # Set process start time if it's the first time it's running
            if selected_process.start_time == -1:
                selected_process.start_time = current_time
            current_process = selected_process
        
        if preemptive:
            # Find next arrival event
            next_event_time = float('inf')
            for p in remaining_processes:
                if p.arrival_time > current_time and p.arrival_time < next_event_time:
                    next_event_time = p.arrival_time
            
            # If no new arrivals before completion, process runs until completion
            if next_event_time == float('inf'):
                execution_time = selected_process.remaining_time
            else:
                # Execute until next event
                execution_time = min(selected_process.remaining_time, next_event_time - current_time)
        else:
            # Non-preemptive: run to completion
            execution_time = selected_process.remaining_time
        
        # Update remaining time
        selected_process.remaining_time -= execution_time
        
        # Add to timeline
        timeline.append({
            'pid': selected_process.pid,
            'start_time': current_time,
            'end_time': current_time + execution_time,
            'duration': execution_time
        })
        
        # Update current time
        current_time += execution_time
        
        # Check if process completed
        if selected_process.remaining_time == 0:
            selected_process.completion_time = current_time
            selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
            selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
            selected_process.response_time = selected_process.start_time - selected_process.arrival_time
            
            # Move process from remaining to completed
            remaining_processes.remove(selected_process)
            completed_processes.append(selected_process)
            current_process = None
    
    return timeline, completed_processes

def round_robin(processes: List[Process], time_quantum: int) -> Tuple[List[Dict[str, Any]], List[Process]]:
    """
    Round Robin scheduling algorithm.
    
    Args:
        processes (List[Process]): List of processes to schedule
        time_quantum (int): Time quantum for execution
        
    Returns:
        Tuple containing:
        - List of execution timeline dictionaries
        - List of scheduled processes with calculated metrics
    """
    # Create a copy of the processes to avoid modifying the original
    processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    current_time = 0
    timeline = []
    
    # Create ready queue
    ready_queue = deque()
    remaining_processes = processes.copy()
    completed_processes = []
    
    # Find first arrival time
    if remaining_processes:
        current_time = remaining_processes[0].arrival_time
    
    while remaining_processes or ready_queue:
        # Add newly arrived processes to ready queue
        while remaining_processes and remaining_processes[0].arrival_time <= current_time:
            ready_queue.append(remaining_processes.pop(0))
        
        if not ready_queue:
            # No process in ready queue, move time to next arrival
            if remaining_processes:
                next_arrival = remaining_processes[0].arrival_time
                if current_time < next_arrival:
                    timeline.append({
                        'pid': None,
                        'start_time': current_time,
                        'end_time': next_arrival,
                        'duration': next_arrival - current_time
                    })
                current_time = next_arrival
            continue
        
        # Get next process from ready queue
        process = ready_queue.popleft()
        
        # Set process start time if it's the first time it's running
        if process.start_time == -1:
            process.start_time = current_time
        
        # Execute for time quantum or until completion
        execution_time = min(time_quantum, process.remaining_time)
        process.remaining_time -= execution_time
        
        # Add to timeline
        timeline.append({
            'pid': process.pid,
            'start_time': current_time,
            'end_time': current_time + execution_time,
            'duration': execution_time
        })
        
        # Update current time
        current_time += execution_time
        
        # Add newly arrived processes to ready queue (again, after time has passed)
        while remaining_processes and remaining_processes[0].arrival_time <= current_time:
            ready_queue.append(remaining_processes.pop(0))
        
        # Check if process is completed
        if process.remaining_time > 0:
            ready_queue.append(process)
        else:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            process.response_time = process.start_time - process.arrival_time
            completed_processes.append(process)
    
    return timeline, completed_processes
