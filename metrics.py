from typing import List
from process import Process

def calculate_metrics(processes: List[Process]) -> dict:
    """
    Calculate various scheduling metrics for a set of processes.
    
    Args:
        processes (List[Process]): List of completed processes
        
    Returns:
        dict: Dictionary containing calculated metrics
    """
    if not processes:
        return {
            'avg_turnaround_time': 0,
            'avg_waiting_time': 0,
            'avg_response_time': 0,
            'cpu_utilization': 0,
            'throughput': 0
        }
    
    total_turnaround_time = sum(p.turnaround_time for p in processes)
    total_waiting_time = sum(p.waiting_time for p in processes)
    total_response_time = sum(p.response_time for p in processes)
    
    # Calculate CPU utilization
    if processes:
        total_burst_time = sum(p.burst_time for p in processes)
        max_completion_time = max(p.completion_time for p in processes)
        min_arrival_time = min(p.arrival_time for p in processes)
        total_time = max_completion_time - min_arrival_time
        cpu_utilization = (total_burst_time / total_time) * 100 if total_time > 0 else 0
    else:
        cpu_utilization = 0
    
    # Calculate throughput
    if processes:
        max_completion_time = max(p.completion_time for p in processes)
        min_arrival_time = min(p.arrival_time for p in processes)
        total_time = max_completion_time - min_arrival_time
        throughput = len(processes) / total_time if total_time > 0 else 0
    else:
        throughput = 0
    
    n = len(processes)
    return {
        'avg_turnaround_time': total_turnaround_time / n,
        'avg_waiting_time': total_waiting_time / n,
        'avg_response_time': total_response_time / n,
        'cpu_utilization': cpu_utilization,
        'throughput': throughput
    }

def compare_algorithms(results: dict) -> str:
    """
    Compare the performance of different scheduling algorithms with HTML formatting.
    
    Args:
        results (dict): Dictionary containing results for different algorithms
        
    Returns:
        str: Comparison result as HTML formatted content
    """
    if not results:
        return '<div class="alert alert-warning">No results to compare.</div>'
    
    # Find the best algorithm for each metric
    metrics_to_compare = ['avg_turnaround_time', 'avg_waiting_time', 'avg_response_time', 'cpu_utilization', 'throughput']
    best_algorithms = {}
    
    for metric in metrics_to_compare:
        if metric in ['avg_turnaround_time', 'avg_waiting_time', 'avg_response_time']:
            # Lower is better
            best_value = float('inf')
            best_algo = None
            for algo, metrics in results.items():
                if metrics[metric] < best_value:
                    best_value = metrics[metric]
                    best_algo = algo
        else:
            # Higher is better
            best_value = float('-inf')
            best_algo = None
            for algo, metrics in results.items():
                if metrics[metric] > best_value:
                    best_value = metrics[metric]
                    best_algo = algo
        
        best_algorithms[metric] = (best_algo, best_value)
    
    # Create HTML formatted comparison table
    html = '''
    <div class="table-responsive">
        <table class="table table-bordered table-hover">
            <thead class="table-dark">
                <tr>
                    <th>Algorithm</th>
                    <th>Avg Turnaround Time</th>
                    <th>Avg Waiting Time</th>
                    <th>Avg Response Time</th>
                    <th>CPU Utilization (%)</th>
                    <th>Throughput</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    # Add a row for each algorithm
    for algo, metrics in results.items():
        html += '<tr>'
        html += f'<td>{algo}</td>'
        
        # Highlight the best value for each metric
        for metric, display in [
            ('avg_turnaround_time', 'Avg Turnaround Time'),
            ('avg_waiting_time', 'Avg Waiting Time'),
            ('avg_response_time', 'Avg Response Time'),
            ('cpu_utilization', 'CPU Utilization (%)'),
            ('throughput', 'Throughput')
        ]:
            is_best = best_algorithms[metric][0] == algo
            value = metrics[metric]
            
            if is_best:
                html += f'<td class="table-success fw-bold">{value:.2f}</td>'
            else:
                html += f'<td>{value:.2f}</td>'
                
        html += '</tr>'
    
    html += '''
            </tbody>
        </table>
    </div>
    '''
    
    # Create a summary of best algorithms
    html += '''
    <div class="card bg-dark mt-4">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Best Algorithm for Each Metric</h5>
        </div>
        <div class="card-body">
            <div class="row">
    '''
    
    # Create a card for each metric's best algorithm
    metric_icons = {
        'avg_turnaround_time': 'bi-arrow-repeat',
        'avg_waiting_time': 'bi-hourglass-split',
        'avg_response_time': 'bi-lightning-charge',
        'cpu_utilization': 'bi-cpu',
        'throughput': 'bi-speedometer'
    }
    
    metric_names = {
        'avg_turnaround_time': 'Turnaround Time',
        'avg_waiting_time': 'Waiting Time',
        'avg_response_time': 'Response Time',
        'cpu_utilization': 'CPU Utilization',
        'throughput': 'Throughput'
    }
    
    for metric in metrics_to_compare:
        best_algo, best_value = best_algorithms[metric]
        html += f'''
            <div class="col-md-4 mb-3">
                <div class="card h-100 border-secondary">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi {metric_icons[metric]}"></i> {metric_names[metric]}</h6>
                    </div>
                    <div class="card-body text-center">
                        <h5 class="card-title text-primary">{best_algo}</h5>
                        <p class="card-text text-muted">Value: {best_value:.2f}</p>
                    </div>
                </div>
            </div>
        '''
    
    html += '''
            </div>
        </div>
    </div>
    '''
    
    return html
