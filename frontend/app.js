// RAG Course Generator - Frontend Application Logic

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initCourseGenerator();
  initDocumentIndexer();
  initVectorSearch();
  checkApiHealth();
});

/* --- TAB NAVIGATION --- */
function initTabs() {
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const pageTitle = document.getElementById('page-title');
  const pageSubtitle = document.getElementById('page-subtitle');

  const tabTitles = {
    generator: {
      title: 'Course Studio',
      subtitle: 'Transform raw documents into structured educational modules using RAG'
    },
    indexer: {
      title: 'Document Indexer',
      subtitle: 'Upload and index document chunk files into ChromaDB'
    },
    search: {
      title: 'Vector Search',
      subtitle: 'Perform direct semantic vector similarity search over indexed chunks'
    },
    health: {
      title: 'System Health',
      subtitle: 'View pipeline architecture, vector store status, and model metadata'
    }
  };

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabKey = btn.dataset.tab;

      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));

      btn.classList.add('active');
      document.getElementById(`tab-${tabKey}`).classList.add('active');

      if (tabTitles[tabKey]) {
        pageTitle.textContent = tabTitles[tabKey].title;
        pageSubtitle.textContent = tabTitles[tabKey].subtitle;
      }
    });
  });
}

/* --- TAB 1: COURSE GENERATOR STUDIO --- */
function initCourseGenerator() {
  const form = document.getElementById('course-form');
  const generateBtn = document.getElementById('generate-btn');
  const emptyState = document.getElementById('empty-state');
  const loaderState = document.getElementById('loader-state');
  const courseOutput = document.getElementById('course-output');
  const copyBtn = document.getElementById('copy-btn');
  const downloadBtn = document.getElementById('download-btn');

  let currentMarkdown = '';

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userGoal = document.getElementById('user-goal').value.trim();
    const level = document.getElementById('level').value;
    const duration = document.getElementById('duration').value.trim() || '10 minutes';
    const coverageLevel = document.getElementById('coverage-level').value;
    const docFilter = document.getElementById('doc-filter').value.trim();

    if (!userGoal) return;

    // UI Loading State
    emptyState.classList.add('hidden');
    courseOutput.classList.add('hidden');
    loaderState.classList.remove('hidden');
    generateBtn.disabled = true;
    copyBtn.disabled = true;
    downloadBtn.disabled = true;

    try {
      const payload = {
        documents: docFilter ? [docFilter] : ["all"],
        user_goal: userGoal,
        level: level,
        duration: duration,
        coverage_level: coverageLevel
      };

      const response = await fetch('/api/generate-course', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Course generation failed.');
      }

      const data = await response.json();
      currentMarkdown = data.content;

      // Render Markdown output
      courseOutput.innerHTML = marked.parse(currentMarkdown);

      loaderState.classList.add('hidden');
      courseOutput.classList.remove('hidden');

      copyBtn.disabled = false;
      downloadBtn.disabled = false;
    } catch (err) {
      loaderState.classList.add('hidden');
      emptyState.classList.remove('hidden');
      alert(`Error generating course: ${err.message}`);
    } finally {
      generateBtn.disabled = false;
    }
  });

  // Copy button
  copyBtn.addEventListener('click', () => {
    if (!currentMarkdown) return;
    navigator.clipboard.writeText(currentMarkdown);
    const origIcon = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color:#10b981"></i>';
    setTimeout(() => { copyBtn.innerHTML = origIcon; }, 2000);
  });

  // Download button
  downloadBtn.addEventListener('click', () => {
    if (!currentMarkdown) return;
    const blob = new Blob([currentMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'course_module.md';
    a.click();
    URL.revokeObjectURL(url);
  });
}

/* --- TAB 2: DOCUMENT INDEXER --- */
function initDocumentIndexer() {
  const form = document.getElementById('index-form');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileNameBadge = document.getElementById('file-name');
  const toast = document.getElementById('index-response');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--accent-primary)';
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = 'var(--border-color)';
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--border-color)';
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      updateFileName();
    }
  });

  fileInput.addEventListener('change', updateFileName);

  function updateFileName() {
    if (fileInput.files.length) {
      fileNameBadge.textContent = fileInput.files[0].name;
      fileNameBadge.classList.remove('hidden');
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const docId = document.getElementById('index-doc-id').value.trim();
    if (!docId || !fileInput.files.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('doc_id', docId);

    try {
      toast.className = 'response-toast hidden';
      const res = await fetch('/api/index', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Indexing failed.');

      toast.textContent = `Document "${data.doc_id}" successfully indexed into ChromaDB!`;
      toast.classList.add('success');
      toast.classList.remove('hidden');
      form.reset();
      fileNameBadge.classList.add('hidden');
    } catch (err) {
      toast.textContent = `Error indexing document: ${err.message}`;
      toast.classList.add('error');
      toast.classList.remove('hidden');
    }
  });
}

/* --- TAB 3: VECTOR SEARCH --- */
function initVectorSearch() {
  const form = document.getElementById('search-form');
  const promptInput = document.getElementById('search-prompt');
  const topKInput = document.getElementById('search-top-k');
  const resultsGrid = document.getElementById('search-results');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const prompt = promptInput.value.trim();
    const topK = parseInt(topKInput.value) || 3;

    if (!prompt) return;

    resultsGrid.innerHTML = '<div class="glowing-spinner"></div>';

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, top_k: topK })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Vector query failed.');

      if (!data.results || data.results.length === 0) {
        resultsGrid.innerHTML = '<p style="color:var(--text-secondary)">No matching vector chunks found.</p>';
        return;
      }

      resultsGrid.innerHTML = data.results.map((r, i) => `
        <div class="chunk-card">
          <div class="chunk-header">
            <span>Result #${i + 1} &bull; Chunk ${r.chunk_index !== undefined ? r.chunk_index : i}</span>
            <span>Distance Score: ${r.score !== undefined ? (1 - r.score).toFixed(4) : 'N/A'}</span>
          </div>
          <div class="chunk-body">
            <p>${escapeHtml(r.text)}</p>
          </div>
        </div>
      `).join('');

    } catch (err) {
      resultsGrid.innerHTML = `<p style="color:var(--accent-rose)">Error performing search: ${err.message}</p>`;
    }
  });
}

/* --- HEALTH & STATUS --- */
async function checkApiHealth() {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const healthApi = document.getElementById('health-api');

  try {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: 'ping', top_k: 1 })
    });

    if (res.ok || res.status === 404) {
      statusDot.className = 'status-indicator online';
      statusText.textContent = 'Online & Ready';
      if (healthApi) healthApi.textContent = 'Online';
    } else {
      throw new Error('Offline');
    }
  } catch {
    statusDot.className = 'status-indicator';
    statusText.textContent = 'Disconnected';
    if (healthApi) {
      healthApi.textContent = 'Disconnected';
      healthApi.className = 'health-value';
    }
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
}
