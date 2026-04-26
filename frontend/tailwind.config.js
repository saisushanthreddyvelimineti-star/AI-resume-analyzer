/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Orbitron", "sans-serif"],
        body: ["Rajdhani", "sans-serif"],
      },
      colors: {
        void: "#02040d",
        plasma: "#44f7ff",
        ion: "#8b5cf6",
        ember: "#ff6b35",
        solar: "#ffe66d",
      },
      boxShadow: {
        neon: "0 0 24px rgba(68, 247, 255, 0.45)",
        ion: "0 0 34px rgba(139, 92, 246, 0.38)",
        ember: "0 0 32px rgba(255, 107, 53, 0.3)",
      },
      backgroundImage: {
        "radial-grid":
          "radial-gradient(circle at center, rgba(68,247,255,0.16), transparent 34%), linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      keyframes: {
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        pulseRing: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.75" },
          "50%": { transform: "scale(1.12)", opacity: "0.25" },
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
      },
      animation: {
        shimmer: "shimmer 1.7s linear infinite",
        pulseRing: "pulseRing 2.2s ease-in-out infinite",
        blink: "blink 1.3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
