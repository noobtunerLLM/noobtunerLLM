// static/js/main.js

class FineTuningUI {
    constructor() {
        this.form = document.getElementById('fine-tuning-form');
        this.jobsContainer = document.getElementById('active-jobs');
        this.fileInput = document.getElementById('file-upload');
        this.dropZone = document.querySelector('.border-dashed');
        this.progressBars = new Map();
        this.activePolling = new Set();

        this.initialize();
    }

    initialize() {
        if (this.form) {
            this.setupFormHandling();
            this.setupFileUpload();
        }
        
        if (this.jobsContainer) {
            this.startJobPolling();
        }

        // Initialize tooltips and other UI elements
        this.setupTooltips();
        this.setupNotifications();
    }

    // Form Handling
    setupFormHandling() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmission(e);
        });

        // Real-time validation
        this.form.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => this.validateField(input));
        });
    }

    async handleFormSubmission(e) {
        try {
            this.showLoader();
            
            if (!this.validateForm()) {
                throw new Error('Please check all fields and try again');
            }

            const formData = new FormData(this.form);
            const params = {
                model_name: formData.get('model_name'),
                learning_rate: parseFloat(formData.get('learning_rate')),
                epochs: parseInt(formData.get('epochs')),
                batch_size: parseInt(formData.get('batch_size'))
            };

            // Handle file upload first if present
            if (this.fileInput.files.length > 0) {
                const fileUploadResult = await this.uploadFile();
                if (!fileUploadResult.success) {
                    throw new Error('File upload failed: ' + fileUploadResult.message);
                }
            }

            // Start fine-tuning
            const response = await fetch('/api/fine-tuning/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                throw new Error('Failed to start fine-tuning process');
            }

            const result = await response.json();
            this.showNotification('success', 'Fine-tuning job started successfully!');
            this.form.reset();
            this.updateJobsList(result.job_id);

        } catch (error) {
            this.showNotification('error', error.message);
        } finally {
            this.hideLoader();
        }
    }

    // File Upload Handling
    setupFileUpload() {
        if (!this.dropZone || !this.fileInput) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
            this.dropZone.addEventListener(event, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        this.dropZone.addEventListener('dragover', () => {
            this.dropZone.classList.add('border-purple-500', 'bg-purple-50');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('border-purple-500', 'bg-purple-50');
        });

        this.dropZone.addEventListener('drop', (e) => {
            this.dropZone.classList.remove('border-purple-500', 'bg-purple-50');
            const files = e.dataTransfer.files;
            if (files.length) {
                this.fileInput.files = files;
                this.updateFileLabel(files[0]);
            }
        });

        this.fileInput.addEventListener('change', () => {
            if (this.fileInput.files.length) {
                this.updateFileLabel(this.fileInput.files[0]);
            }
        });
    }

    async uploadFile() {
        const file = this.fileInput.files[0];
        if (!file) return { success: false, message: 'No file selected' };

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/fine-tuning/upload-data', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const result = await response.json();
            return { success: true, data: result };

        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    updateFileLabel(file) {
        const label = this.dropZone.querySelector('p');
        if (label) {
            label.textContent = `Selected: ${file.name}`;
            // Add file size and type info
            const size = (file.size / 1024 / 1024).toFixed(2);
            const fileInfo = document.createElement('span');
            fileInfo.className = 'text-xs text-gray-500 block';
            fileInfo.textContent = `${size}MB - ${file.type}`;
            label.appendChild(fileInfo);
        }
    }

    // Job Status Handling
    async startJobPolling() {
        await this.updateJobsList();
        setInterval(() => this.updateJobsList(), 5000); // Poll every 5 seconds
    }

    async updateJobsList(newJobId = null) {
        try {
            const response = await fetch('/api/fine-tuning/status/all');
            if (!response.ok) throw new Error('Failed to fetch jobs');

            const jobs = await response.json();
            this.renderJobs(jobs);

            if (newJobId) {
                this.startJobProgressPolling(newJobId);
            }

        } catch (error) {
            console.error('Error fetching jobs:', error);
        }
    }

    renderJobs(jobs) {
        if (!this.jobsContainer) return;

        this.jobsContainer.innerHTML = jobs.length ? jobs.map(job => `
            <div class="bg-gray-50 rounded-lg p-4 mb-4" id="job-${job.id}">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-semibold">${job.model_name}</h3>
                    <span class="status-badge ${this.getStatusClass(job.status)}">
                        ${job.status}
                    </span>
                </div>
                <div class="progress-bar bg-gray-200 rounded-full h-2 mb-2">
                    <div class="bg-purple-600 rounded-full h-2" style="width: ${job.progress}%"></div>
                </div>
                <div class="text-sm text-gray-600">
                    Progress: ${job.progress}% | Started: ${new Date(job.start_time).toLocaleString()}
                </div>
            </div>
        `).join('') : '<p class="text-gray-500">No active jobs</p>';
    }

    getStatusClass(status) {
        const statusClasses = {
            'running': 'bg-blue-100 text-blue-800',
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'pending': 'bg-yellow-100 text-yellow-800'
        };
        return statusClasses[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
    }

    // Validation
    validateForm() {
        let isValid = true;
        const requiredFields = this.form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        switch (field.name) {
            case 'model_name':
                isValid = value.length >= 3;
                errorMessage = 'Model name must be at least 3 characters';
                break;
            case 'learning_rate':
                isValid = value > 0 && value < 1;
                errorMessage = 'Learning rate must be between 0 and 1';
                break;
            case 'epochs':
                isValid = value > 0 && value <= 100;
                errorMessage = 'Epochs must be between 1 and 100';
                break;
            case 'batch_size':
                isValid = value > 0 && value <= 128;
                errorMessage = 'Batch size must be between 1 and 128';
                break;
        }

        this.toggleFieldError(field, isValid, errorMessage);
        return isValid;
    }

    toggleFieldError(field, isValid, message) {
        const errorDiv = field.nextElementSibling?.classList.contains('error-message') 
            ? field.nextElementSibling 
            : document.createElement('div');

        if (!isValid) {
            errorDiv.className = 'error-message text-red-500 text-sm mt-1';
            errorDiv.textContent = message;
            if (!field.nextElementSibling?.classList.contains('error-message')) {
                field.parentNode.insertBefore(errorDiv, field.nextElementSibling);
            }
            field.classList.add('border-red-500');
        } else {
            if (field.nextElementSibling?.classList.contains('error-message')) {
                field.nextElementSibling.remove();
            }
            field.classList.remove('border-red-500');
        }
    }

    // UI Helpers
    showLoader() {
        const loader = document.createElement('div');
        loader.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center';
        loader.id = 'loader';
        loader.innerHTML = `
            <div class="bg-white p-4 rounded-lg">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <p class="mt-2 text-sm text-gray-600">Processing...</p>
            </div>
        `;
        document.body.appendChild(loader);
    }

    hideLoader() {
        const loader = document.getElementById('loader');
        if (loader) loader.remove();
    }

    showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`;
        notification.textContent = message;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    setupTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip absolute bg-gray-800 text-white p-2 rounded text-sm';
                tooltip.textContent = e.target.dataset.tooltip;
                document.body.appendChild(tooltip);

                const rect = e.target.getBoundingClientRect();
                tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
                tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
            });

            element.addEventListener('mouseleave', () => {
                document.querySelector('.tooltip')?.remove();
            });
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.fineTuningUI = new FineTuningUI();
});