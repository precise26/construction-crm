// Base URL for API calls
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000'
    : `http://${window.location.hostname}:3000`;

// Global functions
function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    alertsContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

function closeModal() {
    const modalElement = document.getElementById('detailsModal');
    if (modalElement) {
        const bsModal = bootstrap.Modal.getInstance(modalElement);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

function showModal(modalContent) {
    const modalElement = document.getElementById('detailsModal');
    if (modalElement) {
        modalElement.querySelector('.modal-content').innerHTML = modalContent;
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
}

function getStatusBadgeClass(status) {
    switch(status.toLowerCase()) {
        case 'pending': return 'bg-warning';
        case 'in_progress': return 'bg-primary';
        case 'on_hold': return 'bg-secondary';
        case 'completed': return 'bg-success';
        case 'cancelled': return 'bg-danger';
        default: return 'bg-info';
    }
}

// Lead status badge colors
const leadStatusColors = {
    'new': 'bg-info',
    'pending': 'bg-warning',
    'active': 'bg-primary',
    'qualified': 'bg-success',
    'negotiating': 'bg-purple',
    'converted': 'bg-success',
    'closed': 'bg-secondary',
    'lost': 'bg-danger'
};

let currentLeadId = null;

function showUpdateStatusModal() {
    const statusModal = new bootstrap.Modal(document.getElementById('updateLeadStatusModal'));
    statusModal.show();
}

function updateLeadStatus() {
    if (!currentLeadId) return;

    const status = document.getElementById('leadStatusSelect').value;
    const notes = document.getElementById('leadStatusNotes').value;
    const nextFollowup = document.getElementById('leadNextFollowup').value;

    fetch(`${API_BASE_URL}/leads/${currentLeadId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: status,
            notes: notes,
            next_follow_up: nextFollowup || null
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update lead status');
        }
        return response.json();
    })
    .then(data => {
        // Close the status update modal
        const statusModal = bootstrap.Modal.getInstance(document.getElementById('updateLeadStatusModal'));
        statusModal.hide();

        // Refresh the lead details
        viewLead(currentLeadId);

        // Show success message
        showAlert('Lead status updated successfully', 'success');

        // Refresh the leads list
        loadLeads();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Failed to update lead status', 'danger');
    });
}

async function convertToCustomer(leadId) {
    try {
        const response = await fetch(`${API_BASE_URL}/leads/${leadId}/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Failed to convert lead to customer');
        }

        const customer = await response.json();
        console.log('Customer details:', customer);
        
        // Refresh the leads list to update the UI
        await loadLeads();
        
        // Show success message
        showAlert('Lead successfully converted to customer!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('Failed to convert lead to customer', 'danger');
    }
}

window.viewCustomer = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const customer = await response.json();
        console.log('Customer details:', customer);

        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">Customer Details: ${customer.name}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Name:</strong> ${customer.name}</p>
                        <p><strong>Email:</strong> ${customer.email}</p>
                        <p><strong>Phone:</strong> ${customer.phone}</p>
                        <p><strong>Address:</strong> ${customer.address || 'Not provided'}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Projects:</strong></p>
                        <ul>
                            ${customer.projects ? customer.projects.map(project => 
                                `<li>${project.name} - ${project.status}</li>`
                            ).join('') : 'No projects'}
                        </ul>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-danger" onclick="deleteCustomer(${customer.id})">Delete</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        `;

        showModal(modalContent);
    } catch (error) {
        console.error('Error viewing customer:', error);
        showAlert('Error loading customer details', 'danger');
    }
}

window.viewProject = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/projects/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const project = await response.json();
        console.log('Project details:', project); // Debug log

        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">Project Details: ${project.name}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Customer:</strong> ${project.customer ? project.customer.name : 'N/A'}</p>
                        <p><strong>Status:</strong> <span class="badge badge-${project.status.toLowerCase()}">${project.status}</span></p>
                        <p><strong>Start Date:</strong> ${project.start_date || 'Not set'}</p>
                        <p><strong>End Date:</strong> ${project.end_date || 'Not set'}</p>
                        <p><strong>Budget:</strong> $${project.budget ? project.budget.toFixed(2) : 'Not set'}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Description:</strong></p>
                        <p>${project.description || 'No description available'}</p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-danger" onclick="deleteProject(${project.id})">Delete</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        `;

        showModal(modalContent);
    } catch (error) {
        console.error('Error viewing project:', error);
        showAlert('Error loading project details', 'danger');
    }
}

window.viewVendor = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/vendors/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const vendor = await response.json();
        console.log('Vendor details:', vendor);

        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">Vendor Details: ${vendor.name}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Company Name:</strong> ${vendor.name}</p>
                        <p><strong>Contact Name:</strong> ${vendor.contact_name || 'Not provided'}</p>
                        <p><strong>Email:</strong> ${vendor.email}</p>
                        <p><strong>Phone:</strong> ${vendor.phone}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Address:</strong> ${vendor.address || 'Not provided'}</p>
                        <p><strong>Specialty:</strong> ${vendor.specialty || 'Not specified'}</p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-danger" onclick="deleteVendor(${vendor.id})">Delete</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        `;

        showModal(modalContent);
    } catch (error) {
        console.error('Error viewing vendor:', error);
        showAlert('Error loading vendor details', 'danger');
    }
}

window.viewLead = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/leads/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const lead = await response.json();
        currentLeadId = lead.id;

        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">Lead Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p><strong>Name:</strong> ${lead.name}</p>
                <p><strong>Email:</strong> ${lead.email}</p>
                <p><strong>Phone:</strong> ${lead.phone || '-'}</p>
                <p><strong>Source:</strong> ${lead.source || '-'}</p>
                <p><strong>Project Type:</strong> ${lead.project_type || '-'}</p>
                <p><strong>Description:</strong> ${lead.description || '-'}</p>
                <p><strong>Status:</strong> <span class="badge ${leadStatusColors[lead.status] || 'bg-secondary'}">${lead.status}</span></p>
                <p><strong>Created:</strong> ${new Date(lead.created_at).toLocaleString()}</p>
                ${lead.converted_at ? `<p><strong>Converted:</strong> ${new Date(lead.converted_at).toLocaleString()}</p>` : ''}
                <button class="btn btn-primary" onclick="showUpdateStatusModal()">Update Status</button>
                <button class="btn btn-success" onclick="convertToCustomer(${lead.id})">Convert to Customer</button>
            </div>
            <div class="modal-footer">
                <button class="btn btn-danger" onclick="deleteLead(${lead.id})">Delete</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        `;
        showModal(modalContent);
    } catch (error) {
        console.error('Error viewing lead:', error);
        showAlert('Error viewing lead details', 'danger');
    }
};

async function createLead() {
    const leadData = {
        name: document.getElementById('leadName').value,
        email: document.getElementById('leadEmail').value,
        phone: document.getElementById('leadPhone').value,
        address: document.getElementById('leadAddress').value,
        source: document.getElementById('leadSource').value,
        status: document.getElementById('leadStatus').value.toUpperCase(),
        project_type: document.getElementById('leadProjectType').value,
        description: document.getElementById('leadDescription').value,
        expected_value: parseFloat(document.getElementById('leadExpectedValue').value) || null,
        next_follow_up: document.getElementById('leadNextFollowup').value || null,
        notes: document.getElementById('leadNotes').value
    };

    console.log('Sending lead data:', leadData);

    try {
        const response = await fetch(`${API_BASE_URL}/leads/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(leadData)
        });

        const responseText = await response.text();
        console.log('Server response text:', responseText);

        if (!response.ok) {
            throw new Error(`Failed to create lead: ${responseText}`);
        }

        const result = JSON.parse(responseText);
        console.log('Server response parsed:', result);
        
        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addLeadModal'));
        modal.hide();

        // Clear the form
        document.getElementById('addLeadForm').reset();

        // Show success message
        showAlert('success', 'Lead created successfully!');

        // Refresh the leads list
        loadLeads();
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', error.message || 'Failed to create lead');
    }
}

// Function to format the status badge
function getStatusBadgeHtml(status) {
    // Convert status to lowercase for display
    const displayStatus = status.toLowerCase();
    
    const statusColors = {
        'new': 'bg-info',
        'pending': 'bg-warning',
        'active': 'bg-primary',
        'qualified': 'bg-success',
        'negotiating': 'bg-purple',
        'converted': 'bg-success',
        'closed': 'bg-secondary',
        'lost': 'bg-danger'
    };

    return `<span class="badge ${statusColors[displayStatus] || 'bg-secondary'}">${displayStatus}</span>`;
}

// Function to show alerts
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert the alert at the top of the alerts area
    const alertsArea = document.getElementById('alerts');
    if (alertsArea) {
        alertsArea.insertBefore(alertDiv, alertsArea.firstChild);
    } else {
        console.error('Alerts container not found');
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Update loadLeads function to use the new status badge formatter
async function loadLeads() {
    try {
        const response = await fetch(`${API_BASE_URL}/leads/`);
        const leads = await response.json();
        
        const activeLeadsTableBody = document.getElementById('leadsTableBody');
        const convertedLeadsTableBody = document.getElementById('convertedLeadsTableBody');
        
        activeLeadsTableBody.innerHTML = '';
        convertedLeadsTableBody.innerHTML = '';
        
        leads.forEach(lead => {
            if (lead.status === 'CONVERTED') {
                // Add to converted leads table
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${lead.name}</td>
                    <td>${lead.email}</td>
                    <td>${lead.phone || ''}</td>
                    <td>${lead.source || ''}</td>
                    <td>${new Date(lead.converted_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-info btn-sm" onclick="viewLeadDetails(${lead.id})">
                            View Details
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteLead(${lead.id})">
                            Delete
                        </button>
                    </td>
                `;
                convertedLeadsTableBody.appendChild(row);
            } else {
                // Add to active leads table
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${lead.name}</td>
                    <td>${lead.email}</td>
                    <td>${lead.phone || ''}</td>
                    <td>${lead.source || ''}</td>
                    <td><span class="badge bg-${getStatusBadgeColor(lead.status)}">${lead.status}</span></td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="convertToCustomer(${lead.id})">
                            Convert to Customer
                        </button>
                        <button class="btn btn-info btn-sm" onclick="viewLeadDetails(${lead.id})">
                            View Details
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteLead(${lead.id})">
                            Delete
                        </button>
                    </td>
                `;
                activeLeadsTableBody.appendChild(row);
            }
        });
    } catch (error) {
        console.error('Error loading leads:', error);
        showAlert('danger', 'Failed to load leads');
    }
}

function getStatusBadgeColor(status) {
    const colors = {
        'NEW': 'primary',
        'PENDING': 'warning',
        'ACTIVE': 'info',
        'QUALIFIED': 'success',
        'NEGOTIATING': 'purple',
        'CONVERTED': 'success',
        'CLOSED': 'secondary',
        'LOST': 'danger'
    };
    return colors[status] || 'secondary';
}

// Delete functions
async function deleteVendor(id) {
    if (!confirm('Are you sure you want to delete this vendor?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/vendors/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete vendor');
        
        showAlert('Vendor deleted successfully', 'success');
        closeModal();
        loadVendors();
    } catch (error) {
        console.error('Error deleting vendor:', error);
        showAlert('Error deleting vendor', 'danger');
    }
}

async function deleteCustomer(id) {
    if (!confirm('Are you sure you want to delete this customer?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete customer');
        
        showAlert('Customer deleted successfully', 'success');
        closeModal();
        loadCustomers();
    } catch (error) {
        console.error('Error deleting customer:', error);
        showAlert('Error deleting customer', 'danger');
    }
}

async function deleteProject(id) {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete project');
        
        showAlert('Project deleted successfully', 'success');
        closeModal();
        loadProjects();
    } catch (error) {
        console.error('Error deleting project:', error);
        showAlert('Error deleting project', 'danger');
    }
}

async function deleteLead(leadId) {
    if (!confirm('Are you sure you want to delete this lead?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/leads/${leadId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete lead');
        }

        // Refresh the leads list
        loadLeads();
        showAlert('success', 'Lead deleted successfully');
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Failed to delete lead');
    }
}

// Load functions
async function loadVendors() {
    const vendorsList = document.getElementById('vendorsList');
    if (!vendorsList) return;

    try {
        const response = await fetch(`${API_BASE_URL}/vendors/`);
        if (!response.ok) throw new Error('Failed to fetch vendors');
        const vendors = await response.json();

        vendorsList.innerHTML = vendors.map(vendor => `
            <tr>
                <td>${vendor.name}</td>
                <td>${vendor.contact_name || '-'}</td>
                <td>${vendor.email}</td>
                <td>${vendor.phone}</td>
                <td>${vendor.specialty || '-'}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewVendor(${vendor.id})">View</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading vendors:', error);
        showAlert('Error loading vendors', 'danger');
    }
}

async function loadCustomers() {
    fetch(`${API_BASE_URL}/customers/`)
        .then(response => response.json())
        .then(customers => {
            const tbody = document.getElementById('customersList');
            if (!tbody) {
                console.error('Could not find customers list element');
                return;
            }
            tbody.innerHTML = '';
            customers.forEach(customer => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${customer.name}</td>
                    <td>${customer.email}</td>
                    <td>${customer.phone || 'N/A'}</td>
                    <td>${customer.address || 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewCustomer(${customer.id})">
                            <i class="bi bi-eye"></i> View
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Failed to load customers');
        });
}

async function loadProjects() {
    const projectsList = document.getElementById('projectsList');
    if (!projectsList) return;

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`);
        if (!response.ok) throw new Error('Failed to fetch projects');
        const projects = await response.json();

        projectsList.innerHTML = projects.map(project => `
            <tr>
                <td>${project.name}</td>
                <td>${project.customer ? project.customer.name : 'N/A'}</td>
                <td><span class="badge ${getStatusBadgeClass(project.status)}">${project.status}</span></td>
                <td>${project.start_date || '-'}</td>
                <td>${project.end_date || '-'}</td>
                <td>$${project.budget ? project.budget.toFixed(2) : '-'}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewProject(${project.id})">View</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading projects:', error);
        showAlert('Error loading projects', 'danger');
    }
}

// Dashboard functions
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard stats');
        }
        const stats = await response.json();

        // Update lead statistics
        document.getElementById('totalLeadsCount').textContent = stats.leads.total;
        document.getElementById('convertedLeadsCount').textContent = stats.leads.converted;

        // Update customer statistics
        document.getElementById('totalCustomersCount').textContent = stats.customers.total;
        document.getElementById('activeCustomersCount').textContent = stats.customers.active;

        // Update project statistics
        document.getElementById('totalProjectsCount').textContent = stats.projects.total;
        document.getElementById('activeProjectsCount').textContent = stats.projects.active;
    } catch (error) {
        showAlert('Error loading dashboard statistics', 'error');
        console.error('Error:', error);
    }
}

// Helper function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initial load of visible tab
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        switch (activeTab.id) {
            case 'customers':
                loadCustomers();
                break;
            case 'projects':
                loadProjects();
                break;
            case 'vendors':
                loadVendors();
                break;
            case 'dashboard':
                loadDashboardStats();
                break;
        }
    }

    // Load data when switching tabs
    const tabElements = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target').replace('#', '');
            switch (targetId) {
                case 'customers':
                    loadCustomers();
                    break;
                case 'projects':
                    loadProjects();
                    break;
                case 'vendors':
                    loadVendors();
                    break;
                case 'dashboard':
                    loadDashboardStats();
                    break;
            }
        });
    });

    // Section navigation handling
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide sections
            sections.forEach(section => {
                if (section.id === targetId) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });

            // Load data for specific sections
            switch(targetId) {
                case 'vendors':
                    loadVendors();
                    break;
                case 'leads':
                    loadLeads();
                    break;
                case 'interactions':
                    loadInteractions();
                    populateCustomersForInteraction();
                    break;
                case 'notifications':
                    loadNotifications();
                    populateCustomersForNotification();
                    break;
                case 'customers':
                    loadCustomers();
                    break;
                case 'projects':
                    loadProjects();
                    break;
                case 'dashboard':
                    loadDashboardStats();
                    break;
            }
        });
    });

    // Vendor Form Submission
    const vendorForm = document.getElementById('vendorForm');
    if (vendorForm) {
        vendorForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            const formData = {
                name: document.getElementById('vendorName').value,
                contact_name: document.getElementById('vendorContactName').value || null,
                email: document.getElementById('vendorEmail').value,
                phone: document.getElementById('vendorPhone').value,
                address: document.getElementById('vendorAddress').value || null,
                specialty: document.getElementById('vendorSpecialty').value || null
            };

            try {
                const response = await fetch(`${API_BASE_URL}/vendors/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                showAlert('Vendor added successfully!', 'success');
                vendorForm.reset();
                loadVendors();
            } catch (error) {
                console.error('Error adding vendor:', error);
                showAlert('Error adding vendor', 'danger');
            }
        });
    }

    // Lead Form Submission
    const leadForm = document.getElementById('leadForm');
    if (leadForm) {
        leadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('leadName').value,
                email: document.getElementById('leadEmail').value,
                phone: document.getElementById('leadPhone').value || null,
                source: document.getElementById('leadSource').value || null,
                status: document.getElementById('leadStatus').value.toUpperCase(),
                project_type: document.getElementById('leadProjectType').value || null,
                description: document.getElementById('leadDescription').value || null
            };

            try {
                const response = await fetch(`${API_BASE_URL}/leads/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAlert('Lead added successfully!', 'success');
                    leadForm.reset();
                    loadLeads();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Error adding lead', 'danger');
                }
            } catch (error) {
                showAlert('Error adding lead', 'danger');
            }
        });
    }

    // Interaction Form Submission
    const interactionForm = document.getElementById('interactionForm');
    if (interactionForm) {
        interactionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                customer_id: parseInt(document.getElementById('interactionCustomer').value),
                project_id: document.getElementById('interactionProject').value ? parseInt(document.getElementById('interactionProject').value) : null,
                interaction_type: document.getElementById('interactionType').value,
                description: document.getElementById('interactionDescription').value,
                notes: document.getElementById('interactionNotes').value || null,
                date: document.getElementById('interactionDate').value,
                duration: document.getElementById('interactionDuration').value ? parseFloat(document.getElementById('interactionDuration').value) : null
            };

            try {
                const response = await fetch(`${API_BASE_URL}/interactions/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAlert('Interaction logged successfully!', 'success');
                    interactionForm.reset();
                    loadInteractions();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Error logging interaction', 'danger');
                }
            } catch (error) {
                showAlert('Error logging interaction', 'danger');
            }
        });
    }

    // Notification Form Submission
    const notificationForm = document.getElementById('notificationForm');
    if (notificationForm) {
        notificationForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                customer_id: document.getElementById('notificationCustomer').value ? parseInt(document.getElementById('notificationCustomer').value) : null,
                project_id: document.getElementById('notificationProject').value ? parseInt(document.getElementById('notificationProject').value) : null,
                type: document.getElementById('notificationType').value,
                title: document.getElementById('notificationTitle').value,
                description: document.getElementById('notificationDescription').value || null,
                due_date: document.getElementById('notificationDueDate').value || null
            };

            try {
                const response = await fetch(`${API_BASE_URL}/notifications/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAlert('Notification created successfully!', 'success');
                    notificationForm.reset();
                    loadNotifications();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Error creating notification', 'danger');
                }
            } catch (error) {
                showAlert('Error creating notification', 'danger');
            }
        });
    }

    // Load Leads
    async function loadLeads() {
        const leadsList = document.getElementById('leadsList');
        if (!leadsList) return;

        try {
            const response = await fetch(`${API_BASE_URL}/leads/`);
            const leads = await response.json();

            leadsList.innerHTML = leads.map(lead => `
                <tr>
                    <td>${lead.name}</td>
                    <td>${lead.email}</td>
                    <td>${lead.phone || '-'}</td>
                    <td>${getStatusBadgeHtml(lead.status)}</td>
                    <td>${lead.project_type || '-'}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="viewLead(${lead.id})">View</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteLead(${lead.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            showAlert('Error loading leads', 'danger');
        }
    }

    // Populate Customers for Interaction
    async function populateCustomersForInteraction() {
        const customerSelect = document.getElementById('interactionCustomer');
        const projectSelect = document.getElementById('interactionProject');
        if (!customerSelect) return;

        try {
            const customersResponse = await fetch(`${API_BASE_URL}/customers/`);
            const customers = await customersResponse.json();

            // Clear existing options
            customerSelect.innerHTML = '<option value="">Select Customer</option>';
            customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.name;
                customerSelect.appendChild(option);
            });

            // Populate projects when a customer is selected
            customerSelect.addEventListener('change', async () => {
                const customerId = customerSelect.value;
                if (!customerId) {
                    projectSelect.innerHTML = '<option value="">Select Project</option>';
                    return;
                }

                try {
                    const projectsResponse = await fetch(`${API_BASE_URL}/customers/${customerId}/projects`);
                    const projects = await projectsResponse.json();

                    projectSelect.innerHTML = '<option value="">Select Project</option>';
                    projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.id;
                        option.textContent = project.name;
                        projectSelect.appendChild(option);
                    });
                } catch (error) {
                    showAlert('Error loading projects', 'danger');
                }
            });
        } catch (error) {
            showAlert('Error loading customers', 'danger');
        }
    }

    // Populate Customers for Notification
    async function populateCustomersForNotification() {
        const customerSelect = document.getElementById('notificationCustomer');
        const projectSelect = document.getElementById('notificationProject');
        if (!customerSelect) return;

        try {
            const customersResponse = await fetch(`${API_BASE_URL}/customers/`);
            const customers = await customersResponse.json();

            // Clear existing options
            customerSelect.innerHTML = '<option value="">Select Customer</option>';
            customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.name;
                customerSelect.appendChild(option);
            });

            // Populate projects when a customer is selected
            customerSelect.addEventListener('change', async () => {
                const customerId = customerSelect.value;
                if (!customerId) {
                    projectSelect.innerHTML = '<option value="">Select Project</option>';
                    return;
                }

                try {
                    const projectsResponse = await fetch(`${API_BASE_URL}/customers/${customerId}/projects`);
                    const projects = await projectsResponse.json();

                    projectSelect.innerHTML = '<option value="">Select Project</option>';
                    projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.id;
                        option.textContent = project.name;
                        projectSelect.appendChild(option);
                    });
                } catch (error) {
                    showAlert('Error loading projects', 'danger');
                }
            });
        } catch (error) {
            showAlert('Error loading customers', 'danger');
        }
    }

    // Load Interactions
    async function loadInteractions() {
        const interactionsList = document.getElementById('interactionsList');
        if (!interactionsList) return;

        try {
            const response = await fetch(`${API_BASE_URL}/interactions/`);
            const interactions = await response.json();

            interactionsList.innerHTML = interactions.map(interaction => `
                <tr>
                    <td>${interaction.customer.name}</td>
                    <td>${interaction.project ? interaction.project.name : '-'}</td>
                    <td>${interaction.interaction_type}</td>
                    <td>${new Date(interaction.date).toLocaleDateString()}</td>
                    <td>${interaction.duration ? interaction.duration + ' min' : '-'}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="window.viewInteraction(${interaction.id})">View</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            showAlert('Error loading interactions', 'danger');
        }
    }

    // Load Notifications
    async function loadNotifications() {
        const notificationsList = document.getElementById('notificationsList');
        if (!notificationsList) return;

        try {
            const response = await fetch(`${API_BASE_URL}/notifications/`);
            const notifications = await response.json();

            notificationsList.innerHTML = notifications.map(notification => `
                <tr>
                    <td>${notification.title}</td>
                    <td>${notification.type}</td>
                    <td>${notification.customer ? notification.customer.name : '-'}</td>
                    <td>${notification.project ? notification.project.name : '-'}</td>
                    <td>${notification.due_date ? new Date(notification.due_date).toLocaleDateString() : '-'}</td>
                    <td>${notification.is_read ? 'Read' : 'Unread'}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="window.viewNotification(${notification.id})">View</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            showAlert('Error loading notifications', 'danger');
        }
    }

    // Form submission handling
    const customerForm = document.getElementById('customerForm');
    if (customerForm) {
        customerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                address: document.getElementById('address').value
            };

            try {
                const response = await fetch(`${API_BASE_URL}/customers/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAlert('Customer added successfully!', 'success');
                    customerForm.reset();
                    loadCustomers();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Error adding customer', 'danger');
                }
            } catch (error) {
                showAlert('Error adding customer', 'danger');
            }
        });
    }

    // Add project form submission handling
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('projectName').value,
                customer_id: parseInt(document.getElementById('projectCustomer').value),
                description: document.getElementById('projectDescription').value || null,
                start_date: document.getElementById('startDate').value || null,
                end_date: document.getElementById('endDate').value || null,
                budget: document.getElementById('budget').value ? parseFloat(document.getElementById('budget').value) : null,
                status: document.getElementById('status').value
            };

            try {
                const response = await fetch(`${API_BASE_URL}/projects/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAlert('Project created successfully!', 'success');
                    projectForm.reset();
                    loadProjects();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Error creating project', 'danger');
                }
            } catch (error) {
                showAlert('Error creating project', 'danger');
            }
        });
    }

    // Load customers on page load
    loadCustomers();

    // Initial load of projects
    loadProjects();

    // Add this inside the DOMContentLoaded event listener
    const projectsLink = document.querySelector('a[href="#projects"]');
    if (projectsLink) {
        projectsLink.addEventListener('click', loadCustomersForDropdown);
    }

    async function loadCustomersForDropdown() {
        const customerSelect = document.getElementById('projectCustomer');
        if (!customerSelect) return;

        try {
            const response = await fetch(`${API_BASE_URL}/customers/`);
            const customers = await response.json();

            // Clear existing options except the first one
            customerSelect.innerHTML = '<option value="">Select Customer</option>';

            // Add customer options
            customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.name;
                customerSelect.appendChild(option);
            });
        } catch (error) {
            showAlert('Error loading customers for selection', 'danger');
        }
    }
});

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show target section
        document.getElementById(targetId).style.display = 'block';
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        this.classList.add('active');

        // Load appropriate data based on section
        if (targetId === 'customers') {
            loadCustomers();
        } else if (targetId === 'projects') {
            loadProjects();
        } else if (targetId === 'leads') {
            loadLeads();
        } else if (targetId === 'vendors') {
            loadVendors();
        } else if (targetId === 'dashboard') {
            loadDashboardStats();
        }
    });
});

{{ }} 
