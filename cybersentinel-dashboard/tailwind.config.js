/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          navy: '#0a1628',
          darkNavy: '#0d2137',
          blue: '#00d9ff',
          cyan: '#00ffff',
          teal: '#14b8a6',
          purple: '#8b5cf6',
          dark: '#0a1628',
          darker: '#050814',
        },
        neon: {
          blue: '#00d9ff',
          cyan: '#00ffff',
          teal: '#14b8a6',
          purple: '#c084fc',
          pink: '#f0abfc',
        }
      },
      boxShadow: {
        'neon-blue': '0 0 20px rgba(0, 243, 255, 0.5)',
        'neon-purple': '0 0 20px rgba(168, 85, 247, 0.5)',
        'glow': '0 0 30px rgba(0, 243, 255, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
