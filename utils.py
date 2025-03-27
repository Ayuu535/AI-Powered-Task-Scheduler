from datetime import datetime

def sort_tasks_by_edf(tasks):
    """
    Earliest Deadline First (EDF) algorithm implementation.
    
    Sorts tasks based on their deadline. Tasks with earlier deadlines come first.
    Completed tasks are always placed after incomplete tasks.
    """
    # First, separate completed and incomplete tasks
    incomplete_tasks = [task for task in tasks if not task.completed]
    completed_tasks = [task for task in tasks if task.completed]
    
    # Sort incomplete tasks by deadline (earlier deadlines first)
    sorted_incomplete = sorted(incomplete_tasks, key=lambda task: task.deadline)
    
    # Sort completed tasks by deadline (earlier deadlines first)
    sorted_completed = sorted(completed_tasks, key=lambda task: task.deadline)
    
    # Return the concatenated list (incomplete tasks first, then completed)
    return sorted_incomplete + sorted_completed

def get_time_remaining(deadline):
    """
    Calculate and format the time remaining until a deadline.
    
    Returns a string representation of the time remaining, or 'Overdue' if the deadline has passed.
    """
    now = datetime.now()
    
    if deadline < now:
        return "Overdue"
    
    delta = deadline - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} days, {hours} hours"
    elif hours > 0:
        return f"{hours} hours, {minutes} mins"
    else:
        return f"{minutes} mins"

def get_urgency_class(deadline):
    """
    Determine the urgency level based on deadline.
    
    Returns a CSS class name to be used for styling task cards:
    - 'urgent' for tasks due within 24 hours
    - 'soon' for tasks due within 3 days
    - 'normal' for tasks due later
    - 'overdue' for tasks past their deadline
    """
    now = datetime.now()
    
    if deadline < now:
        return "overdue"  # Past deadline
    
    delta = deadline - now
    hours = delta.days * 24 + delta.seconds / 3600
    
    if hours < 24:
        return "urgent"  # Due within 24 hours
    elif hours < 72:
        return "soon"    # Due within 3 days
    else:
        return "normal"  # Due later
