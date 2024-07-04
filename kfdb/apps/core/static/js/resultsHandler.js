// Hiide video detail buttons once htmx request completes
document.body.addEventListener('htmx:afterRequest', function (e) {
    if (
        e.detail.requestConfig.headers['HX-RemoveNode'] && e.detail.successful
    ) {
        e.target.setAttribute('hidden', 'true');
        let parent = e.target.parentNode;
        if (!e.target.parentNode.querySelector(':scope > :not([hidden])')) {
            parent.remove();
        }
    } else if (
        e.detail.requestConfig.headers['HX-UpdateList'] && e.detail.successful
    ) {
        document.getElementById('page-input')
            .addEventListener('keydown', stopSubmit);
    }
});

// Add fade out animation before htmx swaps new results (w/ fade in)
function fadeOut() {
    document.querySelectorAll('.results-item')?.forEach(o => {
        o.classList.add('fade-out');
    });
}

// Prevent HTML forms from being submitted by the Enter/Return key.
// Without this, forms will submit the GET request to a new page instead
// of using htmx.
var inputs = document.querySelectorAll('.form-input');
function stopSubmit(e) {
    if (e.key === 'Enter') {
        e.currentTarget.blur();
        return false;
    }
    return true;
}
inputs?.forEach(i => i.addEventListener('keydown', stopSubmit));
