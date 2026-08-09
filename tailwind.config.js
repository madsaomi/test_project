/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      boxShadow: {
        teal: "0 4px 14px -3px rgba(13,148,136,0.35)",
        amber: "0 4px 14px -3px rgba(245,158,11,0.35)",
      },
    },
  },
  plugins: [],
};
