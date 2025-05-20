document.addEventListener('DOMContentLoaded', function() {
    // Initialize date-time pickers
    const deadlineInput = document.getElementById('deadline');
    if (deadlineInput) {
        // Set min date to today
        const today = new Date();
        const formattedDate = today.toISOString().slice(0, 16);
        deadlineInput.min = formattedDate;
        deadlineInput.value = formattedDate;
        
        // Setup deadline conflict detection
        setupDeadlineConflictDetection();
    }

    // Task filters
    const filterButtons = document.querySelectorAll('.task-filter-btn');
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get filter type
                const filterType = this.getAttribute('data-filter');
                
                // Apply filter
                filterTasks(filterType);
            });
        });
    }

    // Task completion toggle
    setupTaskCompletionToggles();

    // Task deletion confirmation
    setupTaskDeletionConfirmation();

    // Tooltip initialization (Bootstrap 5)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Filter tasks based on selected filter
function filterTasks(filterType) {
    // Show loading spinner
    const taskContainer = document.getElementById('task-container');
    if (taskContainer) {
        taskContainer.innerHTML = '<div class="d-flex justify-content-center my-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Fetch filtered tasks from server
        fetch(`/tasks/filter?type=${filterType}`)
            .then(response => response.json())
            .then(data => {
                if (data.tasks.length === 0) {
                    taskContainer.innerHTML = `
                        <div class="alert alert-info text-center">
                            No tasks found for this filter.
                        </div>
                    `;
                    return;
                }
                
                // Clear container
                taskContainer.innerHTML = '';
                
                // Render tasks
                data.tasks.forEach(task => {
                    // Determine urgency class
                    const deadline = new Date(task.deadline);
                    const now = new Date();
                    const diff = deadline - now;
                    
                    let urgencyClass = 'normal';
                    let timeRemaining = '';
                    
                    if (diff < 0) {
                        urgencyClass = 'overdue';
                        timeRemaining = 'Overdue';
                    } else {
                        const hours = diff / (1000 * 60 * 60);
                        
                        if (hours < 24) {
                            urgencyClass = 'urgent';
                            timeRemaining = hours < 1 
                                ? `${Math.round(hours * 60)} mins` 
                                : `${Math.floor(hours)} hours, ${Math.round((hours % 1) * 60)} mins`;
                        } else if (hours < 72) {
                            urgencyClass = 'soon';
                            timeRemaining = `${Math.floor(hours / 24)} days, ${Math.floor(hours % 24)} hours`;
                        } else {
                            timeRemaining = `${Math.floor(hours / 24)} days`;
                        }
                    }
                    
                    // Create task card
                    const taskCard = document.createElement('div');
                    taskCard.className = `card task-card ${urgencyClass} ${task.completed ? 'completed' : ''}`;
                    taskCard.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${task.title}</h5>
                            <p class="card-text">${task.description || 'No description'}</p>
                            <div class="task-meta d-flex justify-content-between align-items-center">
                                <div>
                                    <p class="task-deadline mb-0">
                                        <i class="bi bi-calendar-event"></i> 
                                        Due: ${new Date(task.deadline).toLocaleString()}
                                    </p>
                                    <p class="task-time-remaining mb-0 ${urgencyClass}">
                                        <i class="bi bi-alarm"></i> 
                                        ${timeRemaining}
                                    </p>
                                </div>
                                <div class="task-actions">
                                    <form action="/tasks/${task.id}/complete" method="post" class="d-inline">
                                        <button type="submit" class="btn ${task.completed ? 'btn-outline-success' : 'btn-success'} btn-sm">
                                            <i class="bi ${task.completed ? 'bi-x-circle' : 'bi-check-circle'}"></i>
                                            ${task.completed ? 'Mark Incomplete' : 'Complete'}
                                        </button>
                                    </form>
                                    <form action="/tasks/${task.id}/delete" method="post" class="d-inline delete-task-form">
                                        <button type="button" class="btn btn-danger btn-sm delete-task-btn">
                                            <i class="bi bi-trash"></i> Delete
                                        </button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    taskContainer.appendChild(taskCard);
                });
                
                // Re-attach event listeners
                setupTaskCompletionToggles();
                setupTaskDeletionConfirmation();
            })
            .catch(error => {
                console.error('Error fetching tasks:', error);
                taskContainer.innerHTML = `
                    <div class="alert alert-danger text-center">
                        An error occurred while fetching tasks.
                    </div>
                `;
            });
    }
}

// Setup task completion toggles
function setupTaskCompletionToggles() {
    const completeButtons = document.querySelectorAll('.task-actions button[type="submit"]');
    completeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form.classList.contains('processing')) {
                e.preventDefault();
                return;
            }
            
            form.classList.add('processing');
            this.disabled = true;
            
            // Add a small spinner
            const originalContent = this.innerHTML;
            this.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;
            
            // Submit form after a slight delay for better UX
            setTimeout(() => {
                form.submit();
            }, 300);
        });
    });
}

// Setup task deletion confirmation
function setupTaskDeletionConfirmation() {
    const deleteButtons = document.querySelectorAll('.delete-task-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this task?')) {
                const form = this.closest('form');
                form.submit();
            }
        });
    });
}

// Calculate and display time remaining
function updateTimeRemaining() {
    const timeElements = document.querySelectorAll('.task-time-remaining');
    
    timeElements.forEach(element => {
        const deadlineStr = element.closest('.task-meta').querySelector('.task-deadline').textContent;
        const deadlineMatch = deadlineStr.match(/Due: (.+)/);
        
        if (deadlineMatch) {
            const deadline = new Date(deadlineMatch[1]);
            const now = new Date();
            const diff = deadline - now;
            
            if (diff < 0) {
                element.textContent = 'Overdue';
                element.className = 'task-time-remaining mb-0 overdue';
            } else {
                const hours = diff / (1000 * 60 * 60);
                let timeRemaining = '';
                let urgencyClass = 'normal';
                
                if (hours < 24) {
                    urgencyClass = 'urgent';
                    timeRemaining = hours < 1 
                        ? `${Math.round(hours * 60)} mins` 
                        : `${Math.floor(hours)} hours, ${Math.round((hours % 1) * 60)} mins`;
                } else if (hours < 72) {
                    urgencyClass = 'soon';
                    timeRemaining = `${Math.floor(hours / 24)} days, ${Math.floor(hours % 24)} hours`;
                } else {
                    timeRemaining = `${Math.floor(hours / 24)} days`;
                }
                
                element.innerHTML = `<i class="bi bi-alarm"></i> ${timeRemaining}`;
                element.className = `task-time-remaining mb-0 ${urgencyClass}`;
            }
        }
    });
}

// Update time remaining every minute
setInterval(updateTimeRemaining, 60000);

// Setup deadline conflict detection
function setupDeadlineConflictDetection() {
    const taskForm = document.getElementById('taskForm');
    const deadlineInput = document.getElementById('deadline');
    const prioritySelect = document.getElementById('priority');
    const existingDeadlinesInput = document.getElementById('existingDeadlines');
    const modalPrioritySelect = document.getElementById('modalPriority');
    const updatePriorityBtn = document.getElementById('updatePriorityBtn');
    
    // Exit if any element is missing
    if (!taskForm || !deadlineInput || !prioritySelect || !existingDeadlinesInput || !modalPrioritySelect || !updatePriorityBtn) {
        return;
    }
    
    // Initialize the deadline conflict modal
    const deadlineConflictModal = new bootstrap.Modal(document.getElementById('deadlineConflictModal'));
    
    // Handle form submission
    taskForm.addEventListener('submit', function(e) {
        // Parse existing deadlines from input
        const existingDeadlines = JSON.parse(existingDeadlinesInput.value || '[]');
        
        // Format the new deadline to match the format from the server
        const newDeadlineDate = new Date(deadlineInput.value);
        // Remove seconds and milliseconds for comparison
        const newDeadlineFormatted = newDeadlineDate.toISOString().split('.')[0];
        
        console.log("Existing deadlines:", existingDeadlines);
        console.log("New deadline formatted:", newDeadlineFormatted);
        
        // Look for conflicts by comparing the date parts only
        let hasConflict = false;
        for (const existingDeadline of existingDeadlines) {
            // Compare without seconds and milliseconds
            if (existingDeadline.startsWith(newDeadlineFormatted)) {
                hasConflict = true;
                break;
            }
        }
        
        console.log("Has conflict:", hasConflict);
        
        if (hasConflict && prioritySelect.value === "0") {
            // Prevent form submission
            e.preventDefault();
            
            // Show the conflict modal
            deadlineConflictModal.show();
            
            // Update priority button handler
            updatePriorityBtn.onclick = function() {
                // Set the higher priority from modal
                prioritySelect.value = modalPrioritySelect.value;
                
                // Hide modal
                deadlineConflictModal.hide();
                
                // Submit the form
                setTimeout(() => {
                    taskForm.submit();
                }, 300);
            };
        }
    });
}
