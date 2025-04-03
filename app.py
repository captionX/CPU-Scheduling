import os
import logging
from typing import List, Dict, Any, Optional

from flask import Flask, render_template, request, redirect, url_for, flash
from process import Process
from algorithms import (
    fcfs, 
    sjf_non_preemptive, 
    sjf_preemptive, 
    priority_scheduling, 
    round_robin
)
from visualization import (
    generate_gantt_chart, 
    display_process_table, 
    display_summary_metrics
)
from metrics import calculate_metrics, compare_algorithms

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

@app.route('/')
def index():
    """Render the home page with the simulation form."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page with algorithm descriptions."""
    return render_template('about.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    """Handle the simulation form submission and run the selected algorithm."""
    try:
        # Get form data
        algorithm = request.form.get('algorithm')
        num_processes = int(request.form.get('numProcesses', 0))
        
        if num_processes < 1:
            flash('Please enter at least one process.', 'danger')
            return redirect(url_for('index'))
        
        # Get time quantum for Round Robin
        time_quantum = None
        if algorithm == 'Round Robin' or algorithm == 'Compare All':
            time_quantum = int(request.form.get('timeQuantum', 2))
            if time_quantum < 1:
                flash('Time quantum must be at least 1.', 'danger')
                return redirect(url_for('index'))
        
        # Create processes from form data
        processes = []
        need_priority = 'Priority' in algorithm or algorithm == 'Compare All'
        
        for i in range(num_processes):
            arrival_time = int(request.form.get(f'arrivalTime{i}', 0))
            burst_time = int(request.form.get(f'burstTime{i}', 1))
            
            priority = 0
            if need_priority:
                priority = int(request.form.get(f'priority{i}', 0))
            
            processes.append(Process(i+1, arrival_time, burst_time, priority))
        
        # Run selected algorithm
        results = {}
        comparison = None
        
        if algorithm == 'Compare All':
            algorithms = [
                "FCFS",
                "SJF (Non-preemptive)",
                "SJF (Preemptive)",
                "Priority (Non-preemptive)",
                "Priority (Preemptive)",
                "Round Robin"
            ]
            
            all_metrics = {}
            for algo in algorithms:
                algo_results = run_algorithm(algo, processes, time_quantum if algo == "Round Robin" else None)
                all_metrics[algo] = algo_results['metrics']
            
            comparison = compare_algorithms(all_metrics)
            
            # Also show detailed results for FCFS as a default
            results = run_algorithm("FCFS", processes)
            algorithm = "All Algorithms (Showing FCFS Details)"
        else:
            results = run_algorithm(algorithm, processes, time_quantum)
        
        # Generate visualizations
        gantt_chart = generate_gantt_chart(results['timeline'], len(processes))
        process_table = display_process_table(results['processes'])
        metrics_summary = display_summary_metrics(results['processes'])
        
        return render_template(
            'index.html',
            results=True,
            algorithm_name=algorithm,
            gantt_chart=gantt_chart,
            process_table=process_table,
            metrics_summary=metrics_summary,
            comparison=comparison
        )
        
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

def run_algorithm(algorithm: str, processes: List[Process], time_quantum: Optional[int] = None) -> Dict[str, Any]:
    """Run the selected scheduling algorithm and return results."""
    timeline = []
    scheduled_processes = []
    
    # Create copies of processes to avoid modifying the original list
    process_copies = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    
    if algorithm == "FCFS":
        timeline, scheduled_processes = fcfs(process_copies)
    elif algorithm == "SJF (Non-preemptive)":
        timeline, scheduled_processes = sjf_non_preemptive(process_copies)
    elif algorithm == "SJF (Preemptive)":
        timeline, scheduled_processes = sjf_preemptive(process_copies)
    elif algorithm == "Priority (Non-preemptive)":
        timeline, scheduled_processes = priority_scheduling(process_copies, preemptive=False)
    elif algorithm == "Priority (Preemptive)":
        timeline, scheduled_processes = priority_scheduling(process_copies, preemptive=True)
    elif algorithm == "Round Robin":
        # Default time quantum if not provided
        rr_time_quantum = 2 if time_quantum is None else time_quantum
        timeline, scheduled_processes = round_robin(process_copies, rr_time_quantum)
    
    metrics = calculate_metrics(scheduled_processes)
    
    return {
        'timeline': timeline,
        'processes': scheduled_processes,
        'metrics': metrics
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)