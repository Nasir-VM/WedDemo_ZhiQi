
module.exports = {
  darkMode: "class",
  content: [
    "./templates/**/*.html",
    "./frontend-demo/**/*.{html,js}",
    "./static/js/**/*.js",
    "./apps/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          200: "#bcd3ff",
          300: "#8eb5ff",
          400: "#598cff",
          500: "#3563f5",
          600: "#2148e0",
          700: "#1b39b5",
          800: "#1c338f",
          900: "#1c2f72",
        },
      },
      fontFamily: {
        sans: [
          "Noto Sans TC",
          "PingFang TC",
          "Microsoft JhengHei",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
