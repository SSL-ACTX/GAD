/**
 * GAD Corner - Unified Table Logic
 * Handles Search, Year Filter, and Pagination for:
 * Circulars, Memoranda, Office Orders, and Resolutions
 */
document.addEventListener('DOMContentLoaded', function() {
    // 1. SELECTOR MAPPING
    const searchInput = document.getElementById('policySearch') || 
                        document.getElementById('memoSearch') || 
                        document.getElementById('orderSearch') || 
                        document.getElementById('resolutionSearch');

    const yearFilter = document.getElementById('yearFilter') || 
                       document.getElementById('memoYearFilter') || 
                       document.getElementById('orderYearFilter') || 
                       document.getElementById('resolutionYearFilter');

    const paginationControls = document.getElementById('paginationControls') || 
                               document.getElementById('memoPagination') || 
                               document.getElementById('orderPagination') || 
                               document.getElementById('resolutionPagination');

    const tableRows = Array.from(document.querySelectorAll('.policy-row, .memo-row, .order-row, .resolution-row'));

    // 2. SUMMARY MAPPING (For text updates)
    const summaryTotal = document.getElementById('totalItems') || 
                         document.getElementById('memoCount') || 
                         document.getElementById('orderTotal') || 
                         document.getElementById('resoTotalCount');

    const showingCount = document.getElementById('orderShowingCount') || 
                         document.getElementById('resolutionShowingCount');

    const startText = document.getElementById('showingStart'); // Circulars specific
    const endText = document.getElementById('showingEnd');     // Circulars specific

    if (!searchInput || tableRows.length === 0) return;

    let currentPage = 1;
    const rowsPerPage = 5;
    let filteredRows = [...tableRows];

    function updateTable() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedYear = yearFilter.value;

        // --- FILTERING ---
        filteredRows = tableRows.filter(row => {
            const content = (row.getAttribute('data-title') || row.getAttribute('data-content') || "").toLowerCase();
            const year = row.getAttribute('data-year') || "";
            
            const matchesSearch = content.includes(searchTerm);
            const matchesYear = (selectedYear === 'all' || year === selectedYear);

            return matchesSearch && matchesYear;
        });

        // --- PAGINATION ---
        const total = filteredRows.length;
        const totalPages = Math.ceil(total / rowsPerPage);
        
        if (currentPage > totalPages) currentPage = 1;
        if (totalPages === 0) currentPage = 0;

        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        // --- VISIBILITY ---
        tableRows.forEach(row => row.style.display = 'none');
        filteredRows.slice(start, end).forEach(row => row.style.display = '');

        // --- COUNTER UPDATES ---
        if (summaryTotal) summaryTotal.textContent = total;
        if (showingCount) showingCount.textContent = total;
        
        // For Circulars "Showing X to Y" format
        if (startText) startText.textContent = total === 0 ? 0 : start + 1;
        if (endText) endText.textContent = Math.min(end, total);

        renderPagination(totalPages);
    }

    function renderPagination(totalPages) {
        if (!paginationControls) return;
        paginationControls.innerHTML = '';
        if (totalPages <= 1) return;

        const btnClass = "w-8 h-8 flex items-center justify-center rounded text-xs font-bold transition-all border";

        const createBtn = (html, target, isDisabled, isActive = false) => {
            const btn = document.createElement('button');
            btn.className = `${btnClass} ${isActive ? 'bg-primary-green text-white border-primary-green' : 'bg-white border-gray-200 text-gray-600 hover:border-primary-green'} ${isDisabled ? 'opacity-30 cursor-not-allowed' : ''}`;
            btn.innerHTML = html;
            btn.disabled = isDisabled;
            if (!isDisabled) {
                btn.onclick = () => { currentPage = target; updateTable(); scrolltoTable(); };
            }
            return btn;
        };

        // Prev
        paginationControls.appendChild(createBtn('<i class="fas fa-chevron-left"></i>', currentPage - 1, currentPage === 1));

        // Pages
        for (let i = 1; i <= totalPages; i++) {
            paginationControls.appendChild(createBtn(i, i, false, i === currentPage));
        }

        // Next
        paginationControls.appendChild(createBtn('<i class="fas fa-chevron-right"></i>', currentPage + 1, currentPage === totalPages));
    }

    function scrolltoTable() {
        const table = document.querySelector('table');
        if (table) window.scrollTo({ top: table.offsetTop - 150, behavior: 'smooth' });
    }

    searchInput.addEventListener('input', () => { currentPage = 1; updateTable(); });
    yearFilter.addEventListener('change', () => { currentPage = 1; updateTable(); });

    updateTable(); // Init
});