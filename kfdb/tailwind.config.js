/** @type {import("tailwindcss").Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}"
  ],
  safelist: [
    'border-primary',
    'border-secondary',
    'border-accent',
    'badge-primary',
    'badge-secondary',
    'badge-accent',
    'tooltip-primary',
    'tooltip-secondary',
    'tooltip-accent',
    'aspect-[16/9]',
    'aspect-[9/16]',
    'w-full',
    'w-[270px]',
    'sm:max-w-8',
  ],
  theme: {
    screens: {
      'xs': '432px',
      // => @media (min-width: 432px) { ... }
      'sm': '640px',
      // => @media (min-width: 640px) { ... }
      'md': '768px',
      // => @media (min-width: 768px) { ... }
      'lg': '1024px',
      // => @media (min-width: 1024px) { ... }
      'xl': '1280px',
      // => @media (min-width: 1280px) { ... }
      '2xl': '1536px',
      // => @media (min-width: 1536px) { ... }
    },
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
