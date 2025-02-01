// Main JavaScript file for Codlaxy

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });

    // Mobile menu toggle
    const menuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('open');
        });
    }

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileSelect);
    });

    // Like button functionality
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        button.addEventListener('click', handleLike);
    });

    // Comment form submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentSubmit);
    }

    // Role application
    const applyButtons = document.querySelectorAll('.apply-button');
    applyButtons.forEach(button => {
        button.addEventListener('click', handleRoleApplication);
    });
});

// Tooltip functions
function showTooltip(event) {
    const tooltip = event.target;
    const tooltipText = tooltip.getAttribute('data-tooltip');
    if (!tooltipText) return;

    const tooltipElement = document.createElement('div');
    tooltipElement.className = 'tooltip-popup';
    tooltipElement.textContent = tooltipText;
    document.body.appendChild(tooltipElement);

    const rect = tooltip.getBoundingClientRect();
    tooltipElement.style.position = 'absolute';
    tooltipElement.style.top = rect.top - tooltipElement.offsetHeight - 5 + 'px';
    tooltipElement.style.left = rect.left + (rect.width - tooltipElement.offsetWidth) / 2 + 'px';
}

function hideTooltip() {
    const tooltipElement = document.querySelector('.tooltip-popup');
    if (tooltipElement) {
        tooltipElement.remove();
    }
}

// File input preview
function handleFileSelect(event) {
    const input = event.target;
    const preview = document.querySelector(`[data-preview-for="${input.id}"]`);
    if (!preview) return;

    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Like functionality
function handleLike(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const projectId = button.dataset.projectId;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    showLoadingSpinner(button);

    fetch(`/project/${projectId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner(button);
        updateLikeButton(button, data.liked);
        updateLikeCount(projectId, data.likes_count);
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoadingSpinner(button);
    });
}

// Comment submission
function handleCommentSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const projectId = form.dataset.projectId;
    const content = form.querySelector('textarea').value;
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    if (!content.trim()) return;

    const submitButton = form.querySelector('button[type="submit"]');
    showLoadingSpinner(submitButton);

    fetch(`/project/${projectId}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner(submitButton);
        if (data.status === 'success') {
            addCommentToList(data);
            form.reset();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoadingSpinner(submitButton);
    });
}

// Role application
function handleRoleApplication(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const projectId = button.dataset.projectId;
    const role = button.dataset.role;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    showLoadingSpinner(button);

    fetch(`/project/${projectId}/apply/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ role }),
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner(button);
        if (data.status === 'success') {
            updateApplyButton(button);
        } else if (data.status === 'already_applied') {
            showMessage('You have already applied for this role', 'warning');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoadingSpinner(button);
    });
}

// Utility functions
function showLoadingSpinner(element) {
    element.disabled = true;
    element.dataset.originalContent = element.innerHTML;
    element.innerHTML = '<div class="loading-spinner"></div>';
}

function hideLoadingSpinner(element) {
    element.disabled = false;
    element.innerHTML = element.dataset.originalContent;
}

function updateLikeButton(button, liked) {
    const icon = button.querySelector('i');
    if (liked) {
        icon.classList.add('text-red-500');
    } else {
        icon.classList.remove('text-red-500');
    }
}

function updateLikeCount(projectId, count) {
    const countElement = document.querySelector(`[data-like-count="${projectId}"]`);
    if (countElement) {
        countElement.textContent = count;
    }
}

function addCommentToList(comment) {
    const commentsList = document.querySelector('.comments-list');
    if (!commentsList) return;

    const commentElement = document.createElement('div');
    commentElement.className = 'comment-item';
    commentElement.innerHTML = `
        <div class="flex space-x-3 p-4 border-b">
            <img class="h-10 w-10 rounded-full" src="${comment.user_avatar || 'https://via.placeholder.com/40'}" alt="${comment.user}">
            <div class="flex-1">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-medium">${comment.user}</h3>
                    <p class="text-sm text-gray-500">${comment.created_at}</p>
                </div>
                <p class="mt-1 text-sm text-gray-700">${comment.content}</p>
            </div>
        </div>
    `;

    commentsList.insertBefore(commentElement, commentsList.firstChild);
}

function updateApplyButton(button) {
    button.textContent = 'Applied';
    button.classList.remove('bg-blue-100', 'text-blue-700', 'hover:bg-blue-200');
    button.classList.add('bg-gray-100', 'text-gray-500');
    button.disabled = true;
}

function showMessage(message, type = 'info') {
    const messageElement = document.createElement('div');
    messageElement.className = `fixed top-4 right-4 p-4 rounded-md ${type === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'}`;
    messageElement.textContent = message;
    document.body.appendChild(messageElement);

    setTimeout(() => {
        messageElement.remove();
    }, 3000);
} 