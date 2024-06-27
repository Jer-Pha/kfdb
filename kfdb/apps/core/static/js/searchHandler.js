let searchBox = document.getElementById('search-input');

searchBox?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        searchBox.blur();
        return false;
    }
    return true;
});
