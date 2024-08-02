function hslToHex(l, s, h) {
    l = l.substring(0, l.length - 1) / 100;
    let a = (s * 100) * Math.min(l, 1 - l) / 100;
    let f = n => {
        let k = (n + h / 30) % 12;
        let color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');   // convert to Hex and prefix "0" if needed
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}
