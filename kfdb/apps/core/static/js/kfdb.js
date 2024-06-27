// Adjust css 'vh' based on viewport size (fix for mobile browsers)
window.addEventListener('load', setPosition);
window.addEventListener('resize', setPosition);
function setPosition() {
    let vh = window.innerHeight * 0.01; // Current viewport height
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}
