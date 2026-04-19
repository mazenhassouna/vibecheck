// Vibecheck Frontend JavaScript

// State
const state = {
    userAFiles: [],
    userBFiles: [],
};

// DOM Elements
const elements = {
    uploadSection: document.getElementById('upload-section'),
    loadingSection: document.getElementById('loading-section'),
    resultsSection: document.getElementById('results-section'),
    errorSection: document.getElementById('error-section'),
    
    filesA: document.getElementById('files-a'),
    filesB: document.getElementById('files-b'),
    fileListA: document.getElementById('file-list-a'),
    fileListB: document.getElementById('file-list-b'),
    statusA: document.getElementById('status-a'),
    statusB: document.getElementById('status-b'),
    dropzoneA: document.getElementById('dropzone-a'),
    dropzoneB: document.getElementById('dropzone-b'),
    
    skipScraping: document.getElementById('skip-scraping'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resetBtn: document.getElementById('reset-btn'),
    retryBtn: document.getElementById('retry-btn'),
    
    loadingStatus: document.getElementById('loading-status'),
    
    scoreCircle: document.getElementById('score-circle'),
    scoreNumber: document.getElementById('score-number'),
    tierLabel: document.getElementById('tier-label'),
    tierDescription: document.getElementById('tier-description'),
    narrative: document.getElementById('narrative'),
    
    exactMatches: document.getElementById('exact-matches'),
    categoryMatches: document.getElementById('category-matches'),
    broadOverlaps: document.getElementById('broad-overlaps'),
    uniqueA: document.getElementById('unique-a'),
    uniqueB: document.getElementById('unique-b'),
    summaryA: document.getElementById('summary-a'),
    summaryB: document.getElementById('summary-b'),
    
    errorMessage: document.getElementById('error-message'),
};

// Initialize
document.addEventListener('DOMContentLoaded', init);

function init() {
    // File input handlers
    elements.filesA.addEventListener('change', (e) => handleFileSelect(e, 'A'));
    elements.filesB.addEventListener('change', (e) => handleFileSelect(e, 'B'));
    
    // Drag and drop handlers
    setupDragDrop(elements.dropzoneA, 'A');
    setupDragDrop(elements.dropzoneB, 'B');
    
    // Button handlers
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    elements.resetBtn.addEventListener('click', handleReset);
    elements.retryBtn.addEventListener('click', handleReset);
}

function setupDragDrop(dropzone, user) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });
    
    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        handleFiles(files, user);
    }, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleFileSelect(event, user) {
    const files = event.target.files;
    handleFiles(files, user);
}

function handleFiles(files, user) {
    const fileArray = Array.from(files).filter(f => f.name.endsWith('.json'));
    
    if (user === 'A') {
        state.userAFiles = [...state.userAFiles, ...fileArray];
        renderFileList(state.userAFiles, elements.fileListA, 'A');
        updateStatus(elements.statusA, `${state.userAFiles.length} file(s) selected`, 'success');
    } else {
        state.userBFiles = [...state.userBFiles, ...fileArray];
        renderFileList(state.userBFiles, elements.fileListB, 'B');
        updateStatus(elements.statusB, `${state.userBFiles.length} file(s) selected`, 'success');
    }
    
    updateAnalyzeButton();
}

function renderFileList(files, container, user) {
    container.innerHTML = files.map((file, index) => `
        <div class="file-item">
            <span>📄 ${file.name}</span>
            <button class="remove-btn" onclick="removeFile('${user}', ${index})">✕</button>
        </div>
    `).join('');
}

function removeFile(user, index) {
    if (user === 'A') {
        state.userAFiles.splice(index, 1);
        renderFileList(state.userAFiles, elements.fileListA, 'A');
        updateStatus(elements.statusA, state.userAFiles.length ? `${state.userAFiles.length} file(s) selected` : '', '');
    } else {
        state.userBFiles.splice(index, 1);
        renderFileList(state.userBFiles, elements.fileListB, 'B');
        updateStatus(elements.statusB, state.userBFiles.length ? `${state.userBFiles.length} file(s) selected` : '', '');
    }
    updateAnalyzeButton();
}

// Make removeFile globally available
window.removeFile = removeFile;

function updateStatus(element, message, type) {
    element.textContent = message;
    element.className = 'status' + (type ? ` ${type}` : '');
}

function updateAnalyzeButton() {
    const hasFilesA = state.userAFiles.length > 0;
    const hasFilesB = state.userBFiles.length > 0;
    elements.analyzeBtn.disabled = !(hasFilesA && hasFilesB);
}

async function handleAnalyze() {
    showSection('loading');
    updateLoadingStatus('Preparing your data...');
    
    try {
        // Create FormData
        const formData = new FormData();
        
        state.userAFiles.forEach(file => {
            formData.append('user_a_files', file);
        });
        
        state.userBFiles.forEach(file => {
            formData.append('user_b_files', file);
        });
        
        if (elements.skipScraping.checked) {
            formData.append('skip_scraping', 'true');
        }
        
        updateLoadingStatus('Analyzing Instagram data...');
        
        // Send to API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
            showSection('results');
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    }
}

function updateLoadingStatus(message) {
    elements.loadingStatus.textContent = message;
}

function displayResults(data) {
    // Score
    const score = data.vibe_score || 0;
    elements.scoreNumber.textContent = score;
    elements.tierLabel.textContent = data.tier || 'Unknown';
    elements.tierDescription.textContent = data.tier_description || '';
    
    // Animate score
    elements.scoreCircle.classList.add('animated');
    setTimeout(() => elements.scoreCircle.classList.remove('animated'), 600);
    
    // Narrative
    elements.narrative.textContent = data.narrative || 'No narrative generated.';
    
    // Exact matches
    renderMatchList(elements.exactMatches, data.exact_matches || [], 'exact');
    
    // Category matches
    renderMatchList(elements.categoryMatches, data.category_matches || [], 'category');
    
    // Broad overlaps
    renderMatchList(elements.broadOverlaps, data.broad_overlaps || [], 'broad');
    
    // Unique interests
    renderTagList(elements.uniqueA, data.unique_to_a || []);
    renderTagList(elements.uniqueB, data.unique_to_b || []);
    
    // Summaries
    elements.summaryA.textContent = data.user_a_summary || 'No summary available';
    elements.summaryB.textContent = data.user_b_summary || 'No summary available';
}

function renderMatchList(container, matches, type) {
    if (!matches || matches.length === 0) {
        container.innerHTML = '<li class="empty">No matches found</li>';
        return;
    }
    
    container.innerHTML = matches.map(match => {
        if (type === 'exact') {
            return `
                <li>
                    <strong>${match.entity}</strong>
                    ${match.contribution ? `<span class="note">+${match.contribution} points</span>` : ''}
                </li>
            `;
        } else if (type === 'category') {
            return `
                <li>
                    <strong>${match.category}</strong>
                    ${match.note ? `<span class="note">${match.note}</span>` : ''}
                </li>
            `;
        } else {
            return `
                <li>
                    <strong>${match.category}</strong>
                    ${match.note ? `<span class="note">${match.note}</span>` : ''}
                </li>
            `;
        }
    }).join('');
}

function renderTagList(container, items) {
    if (!items || items.length === 0) {
        container.innerHTML = '<li class="empty">Nothing unique</li>';
        return;
    }
    
    container.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

function showSection(section) {
    elements.uploadSection.classList.add('hidden');
    elements.loadingSection.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.errorSection.classList.add('hidden');
    
    switch (section) {
        case 'upload':
            elements.uploadSection.classList.remove('hidden');
            break;
        case 'loading':
            elements.loadingSection.classList.remove('hidden');
            break;
        case 'results':
            elements.resultsSection.classList.remove('hidden');
            break;
        case 'error':
            elements.errorSection.classList.remove('hidden');
            break;
    }
}

function showError(message) {
    elements.errorMessage.textContent = message;
    showSection('error');
}

function handleReset() {
    // Clear state
    state.userAFiles = [];
    state.userBFiles = [];
    
    // Clear UI
    elements.fileListA.innerHTML = '';
    elements.fileListB.innerHTML = '';
    elements.statusA.textContent = '';
    elements.statusB.textContent = '';
    elements.filesA.value = '';
    elements.filesB.value = '';
    
    updateAnalyzeButton();
    showSection('upload');
}
