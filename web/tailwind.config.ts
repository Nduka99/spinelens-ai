import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  safelist: ["sr-only"],
  theme: {
    extend: {
      colors: {
        spine: {
          amber: "#f59e0b",
          ink: "#0f172a",
          civic: "#10b981",
          sky: "#38bdf8",
          paper: "#f8fafc",
        },
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
