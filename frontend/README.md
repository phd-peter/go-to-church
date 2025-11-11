# Frontend: Static HTML/JS Church Commute App

## Overview
Simple static site that fetches commute recommendations from the backend API and displays top routes.

## Local Viewing
1. Open `index.html` in a browser (e.g., Chrome: drag file or `file://` URL).
2. Click "추천 보기" button – fetches from hardcoded backend URL (update in JS for your Render app).

Note: For API calls, serve via local server if CORS issues (e.g., `python -m http.server 3000` in frontend dir).

## API Integration
- JS fetches: `https://go-to-church-backend.onrender.com/gotochurch`
- Update line 10 in `index.html` with your Render URL.
- Displays top 5 ranked routes (route + arrival time).

## Deploy to Vercel
1. Git push frontend/ to GitHub repo.
2. Vercel Dashboard: New Project → Import repo → Root Dir: `/frontend/`
3. Framework: Static → Deploy (no build needed).

Auto-deploys on push. URL: https://go-to-church.vercel.app

## Enhancements
- Add real-time refresh (setInterval).
- Style with CSS/Tailwind for better UI.
