/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
    theme: {
        extend: {
            fontFamily: {
                sans: [
                    '"Roboto Flex"',
                    "system-ui",
                    "-apple-system",
                    "sans-serif",
                ],
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
                "md3-4": "0 20px 25px -5px rgb(0 0 0 / 0.10), 0 8px 10px -6px rgb(0 0 0 / 0.08)",
                "md3-5": "0 25px 50px -12px rgb(0 0 0 / 0.18)",
            },
            colors: {
                /* shadcn tokens — kept so /components/ui/* keeps working */
                background: "hsl(var(--background))",
                foreground: "hsl(var(--foreground))",
                card: {
                    DEFAULT: "hsl(var(--card))",
                    foreground: "hsl(var(--card-foreground))",
                },
                popover: {
                    DEFAULT: "hsl(var(--popover))",
                    foreground: "hsl(var(--popover-foreground))",
                },
                primary: {
                    DEFAULT: "hsl(var(--md-primary))",
                    foreground: "hsl(var(--md-on-primary))",
                },
                secondary: {
                    DEFAULT: "hsl(var(--md-secondary))",
                    foreground: "hsl(var(--md-on-secondary))",
                },
                muted: {
                    DEFAULT: "hsl(var(--muted))",
                    foreground: "hsl(var(--muted-foreground))",
                },
                accent: {
                    DEFAULT: "hsl(var(--accent))",
                    foreground: "hsl(var(--accent-foreground))",
                },
                destructive: {
                    DEFAULT: "hsl(var(--destructive))",
                    foreground: "hsl(var(--destructive-foreground))",
                },
                border: "hsl(var(--border))",
                input: "hsl(var(--input))",
                ring: "hsl(var(--ring))",
                /* Material 3 named tokens */
                "on-primary": "hsl(var(--md-on-primary))",
                "primary-container": "hsl(var(--md-primary-container))",
                "on-primary-container": "hsl(var(--md-on-primary-container))",
                "on-secondary": "hsl(var(--md-on-secondary))",
                "secondary-container": "hsl(var(--md-secondary-container))",
                "on-secondary-container": "hsl(var(--md-on-secondary-container))",
                tertiary: "hsl(var(--md-tertiary))",
                "on-tertiary": "hsl(var(--md-on-tertiary))",
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
            keyframes: {
                "accordion-down": { from: { height: "0" }, to: { height: "var(--radix-accordion-content-height)" } },
                "accordion-up":   { from: { height: "var(--radix-accordion-content-height)" }, to: { height: "0" } },
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up":   "accordion-up 0.2s ease-out",
            },
        },
    },
    plugins: [require("tailwindcss-animate")],
};
