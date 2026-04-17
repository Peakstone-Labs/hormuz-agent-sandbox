// In dev, Vite proxy handles /api → localhost:8000
// In production, set VITE_API_BASE to your backend URL (e.g. https://api.peakstone-labs.com)
export const API_BASE = import.meta.env.VITE_API_BASE || ''
