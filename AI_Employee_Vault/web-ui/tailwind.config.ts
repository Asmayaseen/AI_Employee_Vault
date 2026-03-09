import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#e0f7fa",
          100: "#b2ebf2",
          200: "#80deea",
          300: "#4dd0e1",
          400: "#00E5FF",
          500: "#00BCD4",
          600: "#0097A7",
          700: "#00838F",
          800: "#006064",
          900: "#004D40",
        },
        neon: {
          cyan: "#00E5FF",
          "cyan-deep": "#0097A7",
          orange: "#FF6B00",
          "orange-deep": "#E65100",
          green: "#39FF14",
          "green-deep": "#00C853",
        },
        surface: {
          DEFAULT: "#111111",
          elevated: "#1A1A1A",
          dark: "#0A0A0A",
        },
      },
      boxShadow: {
        "glow-cyan": "0 0 15px rgba(0, 229, 255, 0.3), 0 0 40px rgba(0, 229, 255, 0.1)",
        "glow-cyan-sm": "0 0 8px rgba(0, 229, 255, 0.25)",
        "glow-orange": "0 0 15px rgba(255, 107, 0, 0.3), 0 0 40px rgba(255, 107, 0, 0.1)",
        "glow-green": "0 0 15px rgba(57, 255, 20, 0.3), 0 0 40px rgba(57, 255, 20, 0.1)",
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 5px rgba(0, 229, 255, 0.2)" },
          "50%": { boxShadow: "0 0 20px rgba(0, 229, 255, 0.4)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
