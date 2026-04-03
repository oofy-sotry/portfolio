// 검색 자동완성
(function() {
    const input = document.getElementById('searchInput');
    const dropdown = document.getElementById('suggestionsDropdown');
    if (!input || !dropdown) return;

    const suggestionsUrl = input.dataset.suggestionsUrl;
    const searchUrl = input.dataset.searchUrl;
    let debounceTimer;

    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const q = this.value.trim();

        if (q.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(function() {
            fetch(`${suggestionsUrl}?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(suggestions => {
                    if (suggestions.length === 0) {
                        dropdown.style.display = 'none';
                        return;
                    }
                    dropdown.innerHTML = suggestions.map(s =>
                        `<a href="${searchUrl}?q=${encodeURIComponent(s)}" class="list-group-item list-group-item-action">${s}</a>`
                    ).join('');
                    dropdown.style.display = 'block';
                });
        }, 300);
    });

    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
})();
