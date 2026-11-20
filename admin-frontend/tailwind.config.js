/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Roboto Flex"', "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        "md3-1": "0 1px 2px 0 rgb(0 0 0 / 0.06), 0 1px 3px 0 rgb(0 0 0 / 0.06)",
        "md3-2": "0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.06)",
        "md3-3": "0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.06)",
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--md-primary))",
          foreground: "hsl(var(--md-on-primary))",
        },
        "on-primary": "hsl(var(--md-on-primary))",
        "primary-container": "hsl(var(--md-primary-container))",
        "on-primary-container": "hsl(var(--md-on-primary-container))",
        secondary: {
          DEFAULT: "hsl(var(--md-secondary))",
          foreground: "hsl(var(--md-on-secondary))",
        },
        "secondary-container": "hsl(var(--md-secondary-container))",
        "on-secondary-container": "hsl(var(--md-on-secondary-container))",
        tertiary: "hsl(var(--md-tertiary))",
        "tertiary-container": "hsl(var(--md-tertiary-container))",
        "on-tertiary-container": "hsl(var(--md-on-tertiary-container))",
        error: "hsl(var(--md-error))",
        "on-error": "hsl(var(--md-on-error))",
        surface: "hsl(var(--md-surface))",
        "surface-variant": "hsl(var(--md-surface-variant))",
        "on-surface": "hsl(var(--md-on-surface))",
        "on-surface-variant": "hsl(var(--md-on-surface-variant))",
        outline: "hsl(var(--md-outline))",
        "outline-variant": "hsl(var(--md-outline-variant))",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
