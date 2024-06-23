/** @type {import("tailwindcss").Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}"
  ],
  safelist: [
    'border-primary',
    'border-secondary',
    'border-accent',
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: [
      "light",
      "dark",
      "lofi",
      "black",
      {
        kindafunny: {
          "primary": "#27f8ff",
          "primary-content": "#011516",
          "secondary": "#ff19c1",
          "secondary-content": "#16000e",
          "accent": "#fcff00",
          "accent-content": "#161600",
          "neutral": "#00117f",
          "neutral-content": "#c5d0e8",
          "base-100": "#000944",
          "base-200": "#00073a",
          "base-300": "#000530",
          "base-content": "#c3cad9",
          "info": "#00117f",
          "info-content": "#c5d0e8",
          "success": "#a4fa04",
          "success-content": "#0a1500",
          "warning": "#fcff00",
          "warning-content": "#161600",
          "error": "#E90030",
          "error-content": "#ffd8d5",
        },
      },
    ],
  },
  plugins: [
    require("daisyui"),
  ],
}
