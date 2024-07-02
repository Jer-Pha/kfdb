function fadeOut(bool) {
    document.querySelectorAll('.results-item')?.forEach(o => {
        o.classList.add('fade-out');
    });
}
