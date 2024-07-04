// Prevent HTML forms from being submitted by the Enter/Return key.
// Without this, forms will submit the GET request to a new page instead
// of using htmx.
var input = document.getElementById('host-search');
function stopSubmit(e) {
    if (e.key === 'Enter') {
        e.currentTarget.blur();
        return false;
    }
    return true;
}
input?.addEventListener('keydown', stopSubmit);
