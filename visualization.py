from typing import List, Dict, Any
from tabulate import tabulate
import random

def generate_gantt_chart(timeline: List[Dict[str, Any]], processes_count: int) -> str:
    """
    Generate a text-based Gantt chart with colors for web display.
    
    Args:
        timeline (List[Dict]): List of execution timelines
        processes_count (int): Total number of processes
    
    Returns:
        str: Text-based Gantt chart representation
    """
    if not timeline:
        return "No timeline data available."
    
    # Calculate total timeline length
    end_time = max(segment['end_time'] for segment in timeline)
    
    # Create chart header
    chart = ""
    
    # Create time scale
    time_scale = " " * 3  # Indent for alignment
    for i in range(0, end_time + 1, 1):
        time_scale += f"{i:<3}"
    chart += time_scale + "\n"
    
    # Create divider
    chart += " " * 3 + "-" * (len(time_scale) - 3) + "\n"
    
    # Generate fixed colors for processes
    process_colors = {}
    color_list = [
        "#4285F4", "#EA4335", "#FBBC05", "#34A853",  # Google colors
        "#00BFFF", "#FF6347", "#32CD32", "#FF69B4", "#9370DB", "#FF8C00",
        "#20B2AA", "#8A2BE2", "#FF00FF", "#1E90FF", "#7CFC00"
    ]
    
    # Assign a unique color to each process ID
    for segment in timeline:
        if segment['pid'] is not None and segment['pid'] not in process_colors:
            process_colors[segment['pid']] = color_list[segment['pid'] % len(color_list)]
    
    # Create process execution bar
    chart += "CPU|"
    
    current_time = 0
    for segment in sorted(timeline, key=lambda x: x['start_time']):
        # Add idle time if there's a gap
        if segment['start_time'] > current_time:
            gap = segment['start_time'] - current_time
            chart += f"{'▒' * (gap * 3)}"
        
        # Add process execution block
        duration = segment['end_time'] - segment['start_time']
        if segment['pid'] is not None:
            process_id = f"P{segment['pid']}"
            chart += f"{process_id * ((duration * 3) // len(process_id))}{' ' * ((duration * 3) % len(process_id))}"
        else:
            chart += "I" * (duration * 3)
        
        current_time = segment['end_time']
    
    chart += "\n"
    
    # Create process timeline (each process gets its own line)
    seen_pids = set()
    for segment in sorted(timeline, key=lambda x: (x['pid'] if x['pid'] is not None else float('inf'))):
        pid = segment['pid']
        if pid is None or pid in seen_pids:
            continue
        
        seen_pids.add(pid)
        process_line = f"P{pid} |"
        
        current_time = 0
        for t in range(end_time + 1):
            is_active = any(
                seg['pid'] == pid and seg['start_time'] <= t < seg['end_time'] 
                for seg in timeline
            )
            
            if is_active:
                process_line += "███"
            else:
                process_line += "   "
        
        chart += process_line + "\n"
    
    return chart

def display_process_table(processes: List) -> str:
    """
    Display process details in an HTML table format.
    
    Args:
        processes (List): List of scheduled processes
    
    Returns:
        str: HTML table representation of process details
    """
    headers = ["Process", "Arrival Time", "Burst Time", "Priority", 
              "Completion Time", "Turnaround Time", "Waiting Time", "Response Time"]
    
    table_data = []
    for p in processes:
        table_data.append([
            f"P{p.pid}",
            p.arrival_time,
            p.burst_time,
            p.priority,
            p.completion_time,
            p.turnaround_time,
            p.waiting_time,
            p.response_time
        ])
    
    # Generate HTML table instead of plain text
    html_table = '<table class="table table-striped table-bordered">\n'
    
    # Add table header
    html_table += '<thead class="table-dark">\n<tr>\n'
    for header in headers:
        html_table += f'<th>{header}</th>\n'
    html_table += '</tr>\n</thead>\n'
    
    # Add table body
    html_table += '<tbody>\n'
    for row in table_data:
        html_table += '<tr>\n'
        for i, cell in enumerate(row):
            # Add special styling for process ID
            if i == 0:  # Process ID column
                html_table += f'<td><span class="badge bg-primary">{cell}</span></td>\n'
            # Format numeric values
            elif i >= 4:  # Result columns (completion time onwards)
                html_table += f'<td>{cell}</td>\n'
            else:
                html_table += f'<td>{cell}</td>\n'
        html_table += '</tr>\n'
    html_table += '</tbody>\n'
    html_table += '</table>'
    
    return html_table

def display_summary_metrics(processes: List) -> str:
    """
    Calculate and display summary metrics as an HTML table.
    
    Args:
        processes (List): List of scheduled processes
    
    Returns:
        str: HTML table of summary metrics
    """
    avg_turnaround_time = sum(p.turnaround_time for p in processes) / len(processes)
    avg_waiting_time = sum(p.waiting_time for p in processes) / len(processes)
    avg_response_time = sum(p.response_time for p in processes) / len(processes)
    
    # Create HTML card with metrics
    html = '<div class="row">'
    
    # Turnaround Time Card
    html += '''
    <div class="col-md-4">
        <div class="card bg-dark mb-3">
            <div class="card-header text-center text-info">
                <h5 class="mb-0"><i class="bi bi-arrow-repeat"></i> Avg. Turnaround Time</h5>
            </div>
            <div class="card-body text-center">
                <h2 class="display-4">{:.2f}</h2>
                <p class="card-text">Time from submission to completion</p>
            </div>
        </div>
    </div>
    '''.format(avg_turnaround_time)
    
    # Waiting Time Card
    html += '''
    <div class="col-md-4">
        <div class="card bg-dark mb-3">
            <div class="card-header text-center text-warning">
                <h5 class="mb-0"><i class="bi bi-hourglass-split"></i> Avg. Waiting Time</h5>
            </div>
            <div class="card-body text-center">
                <h2 class="display-4">{:.2f}</h2>
                <p class="card-text">Time spent in ready queue</p>
            </div>
        </div>
    </div>
    '''.format(avg_waiting_time)
    
    # Response Time Card
    html += '''
    <div class="col-md-4">
        <div class="card bg-dark mb-3">
            <div class="card-header text-center text-success">
                <h5 class="mb-0"><i class="bi bi-lightning-charge"></i> Avg. Response Time</h5>
            </div>
            <div class="card-body text-center">
                <h2 class="display-4">{:.2f}</h2>
                <p class="card-text">Time until first CPU response</p>
            </div>
        </div>
    </div>
    '''.format(avg_response_time)
    
    html += '</div>'
    
    # Additional summary table
    html += '''
    <table class="table table-dark table-bordered mt-3">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Processes</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>CPU Utilization</td>
                <td>{:.2f}%</td>
            </tr>
            <tr>
                <td>Throughput</td>
                <td>{:.4f} processes/unit time</td>
            </tr>
        </tbody>
    </table>
    '''.format(
        len(processes),
        (sum(p.burst_time for p in processes) / max(p.completion_time for p in processes) * 100),
        len(processes) / max(p.completion_time for p in processes) if max(p.completion_time for p in processes) > 0 else 0
    )
    
    return html
