/** @type {import("tailwindcss").Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}"
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: [
      "light",
      "dark",
      {
        kfblue: {
          "primary": "#00A3E0",
        },
      },
    ],
  },
  plugins: [
    require("daisyui"),
  ],
}
