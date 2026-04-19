// Vibecheck - Session-based Frontend

// State
let sessionCode = null;
let userRole = null; // "user_a" or "user_b"
let selectedFile = null;
let pollInterval = null;

// DOM Elements
const sections = {
    landing: document.getElementById('landing-section'),
    code: document.getElementById('code-section'),
    upload: document.getElementById('upload-section'),
    waiting: document.getElementById('waiting-section'),
    analyzing: document.getElementById('analyzing-section'),
    results: document.getElementById('results-section'),
    error: document.getElementById('error-section'),
};

// Helper: Show a specific section
function showSection(sectionId) {
    Object.values(sections).forEach(section => {
        if (section) section.classList.add('hidden');
    });
    if (sections[sectionId]) {
        sections[sectionId].classList.remove('hidden');
    }
}

// Helper: Show error
function showError(message) {
    document.getElementById('error-message').textContent = message;
    showSection('error');
}

// Helper: Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ============== Session Management ==============

async function createSession() {
    try {
        const response = await fetch('/api/session/create', { method: 'POST' });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail || 'Failed to create session');
        
        sessionCode = data.code;
        userRole = data.role;
        
        // Show code section
        document.getElementById('session-code').textContent = sessionCode;
        showSection('code');
        
        // Start polling for partner to join
        startPolling();
        
    } catch (error) {
        showError('Failed to create session: ' + error.message);
    }
}

async function joinSession() {
    const codeInput = document.getElementById('join-code-input');
    const code = codeInput.value.trim().toUpperCase();
    
    if (code.length < 4) {
        alert('Please enter a valid session code');
        return;
    }
    
    try {
        const response = await fetch(`/api/session/${code}/join`, { method: 'POST' });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail || 'Failed to join session');
        
        sessionCode = data.code;
        userRole = data.role;
        
        // Go directly to upload
        showUploadSection();
        
    } catch (error) {
        showError('Failed to join session: ' + error.message);
    }
}

function showUploadSection() {
    document.getElementById('upload-session-code').textContent = sessionCode;
    document.getElementById('your-role').textContent = userRole === 'user_a' ? 'Person A' : 'Person B';
    showSection('upload');
}

// ============== File Upload ==============

function setupDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInfo = document.getElementById('file-info');
    
    if (!dropzone) return;
    
    // Drag and drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Upload button
    uploadBtn.addEventListener('click', uploadFile);
}

function handleFileSelect(file) {
    const fileInfo = document.getElementById('file-info');
    const uploadBtn = document.getElementById('upload-btn');
    
    if (!file.name.toLowerCase().endsWith('.zip')) {
        fileInfo.innerHTML = '<span class="error">⚠️ Please select a ZIP file</span>';
        uploadBtn.disabled = true;
        selectedFile = null;
        return;
    }
    
    selectedFile = file;
    fileInfo.innerHTML = `
        <span class="success">✅ ${file.name} (${formatFileSize(file.size)})</span>
    `;
    uploadBtn.disabled = false;
}

async function uploadFile() {
    if (!selectedFile || !sessionCode || !userRole) {
        showError('Missing file or session information');
        return;
    }
    
    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Uploading...';
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(`/api/session/${sessionCode}/upload?role=${userRole}`, {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail || 'Upload failed');
        
        // Show waiting section
        updateWaitingStatus(true, data.both_uploaded);
        showSection('waiting');
        
        // Start polling for results
        startPolling();
        
    } catch (error) {
        uploadBtn.disabled = false;
        uploadBtn.textContent = '📤 Upload Data';
        showError('Upload failed: ' + error.message);
    }
}

// ============== Polling ==============

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(pollStatus, 3000);
    pollStatus(); // Initial poll
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

async function pollStatus() {
    if (!sessionCode || !userRole) return;
    
    try {
        const response = await fetch(`/api/session/${sessionCode}/status?role=${userRole}`);
        const data = await response.json();
        
        if (!response.ok) {
            stopPolling();
            showError(data.detail || 'Session expired or not found');
            return;
        }
        
        handleStatusUpdate(data);
        
    } catch (error) {
        console.error('Poll error:', error);
    }
}

function handleStatusUpdate(status) {
    console.log('Status update:', status);
    
    // Update waiting status
    if (status.status === 'waiting_for_partner') {
        // Still waiting for partner to join
        if (status.your_role === 'user_a') {
            // We created the session, show code section
            // Partner hasn't joined yet
        }
    } else if (status.status === 'waiting_for_uploads') {
        // Partner joined, check if we need to show upload or waiting
        if (!status.user_a_uploaded || !status.user_b_uploaded) {
            const youUploaded = (status.your_role === 'user_a' && status.user_a_uploaded) ||
                               (status.your_role === 'user_b' && status.user_b_uploaded);
            
            if (youUploaded) {
                // Show waiting section
                updateWaitingStatus(true, status.user_a_uploaded && status.user_b_uploaded);
                if (!sections.waiting.classList.contains('hidden')) return;
                showSection('waiting');
            } else if (status.user_b_joined && status.your_role === 'user_a' && !sections.upload.classList.contains('hidden')) {
                // Partner joined while we were showing code, go to upload
                showUploadSection();
            } else if (status.user_b_joined && sections.code && !sections.code.classList.contains('hidden')) {
                // Partner joined, creator should go to upload
                showUploadSection();
            }
        }
    } else if (status.status === 'analyzing') {
        stopPolling();
        showSection('analyzing');
        // Resume polling to wait for results
        setTimeout(() => startPolling(), 2000);
    } else if (status.status === 'complete') {
        stopPolling();
        displayResults(status.result);
    } else if (status.status === 'error') {
        stopPolling();
        showError(status.error || 'Analysis failed');
    }
}

function updateWaitingStatus(youUploaded, partnerUploaded) {
    const checkYou = document.getElementById('check-you');
    const checkPartner = document.getElementById('check-partner');
    
    if (checkYou) {
        checkYou.querySelector('.check-icon').textContent = youUploaded ? '✅' : '⏳';
    }
    if (checkPartner) {
        checkPartner.querySelector('.check-icon').textContent = partnerUploaded ? '✅' : '⏳';
    }
}

// ============== Results Display ==============

function displayResults(result) {
    showSection('results');
    
    // Score and tier
    const score = result.vibe_score || 0;
    document.getElementById('score-number').textContent = score;
    document.getElementById('tier-label').textContent = result.tier || 'Unknown';
    document.getElementById('tier-description').textContent = result.tier_description || '';
    
    // Score circle color
    const scoreCircle = document.getElementById('score-circle');
    scoreCircle.style.background = getScoreGradient(score);
    
    // Narrative
    document.getElementById('narrative').textContent = result.narrative || 'No analysis available.';
    
    // Exact matches
    const exactList = document.getElementById('exact-matches');
    exactList.innerHTML = '';
    if (result.exact_matches && result.exact_matches.length > 0) {
        result.exact_matches.forEach(match => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${match.entity}</strong>`;
            exactList.appendChild(li);
        });
    } else {
        exactList.innerHTML = '<li class="empty">No exact matches found</li>';
    }
    
    // Category matches
    const categoryList = document.getElementById('category-matches');
    categoryList.innerHTML = '';
    if (result.category_matches && result.category_matches.length > 0) {
        result.category_matches.forEach(match => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${match.category}</strong><br><small>${match.note || ''}</small>`;
            categoryList.appendChild(li);
        });
    } else {
        categoryList.innerHTML = '<li class="empty">No category matches found</li>';
    }
    
    // Broad overlaps
    const broadList = document.getElementById('broad-overlaps');
    broadList.innerHTML = '';
    if (result.broad_overlaps && result.broad_overlaps.length > 0) {
        result.broad_overlaps.forEach(overlap => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${overlap.category}</strong><br><small>${overlap.note || ''}</small>`;
            broadList.appendChild(li);
        });
    } else {
        broadList.innerHTML = '<li class="empty">No broad overlaps found</li>';
    }
    
    // Unique interests
    const uniqueA = document.getElementById('unique-a');
    const uniqueB = document.getElementById('unique-b');
    
    uniqueA.innerHTML = '';
    if (result.unique_to_a && result.unique_to_a.length > 0) {
        result.unique_to_a.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            uniqueA.appendChild(li);
        });
    } else {
        uniqueA.innerHTML = '<li class="empty">None identified</li>';
    }
    
    uniqueB.innerHTML = '';
    if (result.unique_to_b && result.unique_to_b.length > 0) {
        result.unique_to_b.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            uniqueB.appendChild(li);
        });
    } else {
        uniqueB.innerHTML = '<li class="empty">None identified</li>';
    }
    
    // Summaries
    document.getElementById('summary-a').textContent = result.user_a_summary || 'No summary available';
    document.getElementById('summary-b').textContent = result.user_b_summary || 'No summary available';
}

function getScoreGradient(score) {
    if (score >= 75) return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    if (score >= 50) return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    if (score >= 25) return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
    return 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)';
}

// ============== Event Listeners ==============

document.addEventListener('DOMContentLoaded', () => {
    // Create session button
    const createBtn = document.getElementById('create-session-btn');
    if (createBtn) createBtn.addEventListener('click', createSession);
    
    // Join session button
    const joinBtn = document.getElementById('join-session-btn');
    if (joinBtn) joinBtn.addEventListener('click', joinSession);
    
    // Join code input - allow Enter key
    const joinInput = document.getElementById('join-code-input');
    if (joinInput) {
        joinInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') joinSession();
        });
        // Auto-uppercase
        joinInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }
    
    // Copy code button
    const copyBtn = document.getElementById('copy-code-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(sessionCode);
            copyBtn.textContent = '✅';
            setTimeout(() => copyBtn.textContent = '📋', 2000);
        });
    }
    
    // Setup dropzone
    setupDropzone();
    
    // New session button
    const newSessionBtn = document.getElementById('new-session-btn');
    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', () => {
            sessionCode = null;
            userRole = null;
            selectedFile = null;
            stopPolling();
            showSection('landing');
        });
    }
    
    // Retry button
    const retryBtn = document.getElementById('retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            sessionCode = null;
            userRole = null;
            selectedFile = null;
            stopPolling();
            showSection('landing');
        });
    }
});
