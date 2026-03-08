# 📱 Deploy as a PWA — Step-by-Step Guide

This folder contains the mobile-ready PWA version of the Stock Analysis Dashboard.
The web version (browser) remains untouched in the parent folder as `dashboard.py`.

---

## 📁 Folder Structure

```
stock-pwa/
├── app.py                  ← Mobile-optimised Streamlit app
├── requirements.txt        ← Python dependencies
├── DEPLOY.md               ← This file
├── .streamlit/
│   └── config.toml         ← Theme + server settings
└── static/
    ├── manifest.json       ← PWA web-app manifest
    ├── icon.svg            ← App icon (shown on home screen)
    └── icon-maskable.svg   ← Adaptive icon for Android
```

---

## 🚀 Deploy to Streamlit Community Cloud (Free)

### Prerequisites
- A free GitHub account
- A free Streamlit Cloud account at https://share.streamlit.io

### Step 1 — Push to GitHub

```bash
# From inside the stock-pwa folder
git init
git add .
git commit -m "Initial PWA deployment"
git remote add origin https://github.com/YOUR_USERNAME/stock-dashboard-pwa.git
git push -u origin main
```

Or create a new repo on github.com, then drag-and-drop the folder contents.

### Step 2 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Connect your GitHub account
4. Select the repo `stock-dashboard-pwa`
5. Set **Main file path** to `app.py`
6. Click **"Deploy!"**

> ⏱ First deploy takes ~3 minutes. Subsequent updates are automatic when you push to GitHub.

You'll get a URL like:
```
https://your-username-stock-dashboard-pwa-app-xxxxxx.streamlit.app
```

---

## 📲 Install as a PWA (Add to Home Screen)

### Android (Chrome)
1. Open the app URL in **Chrome**
2. Tap the **⋮ menu** (top right)
3. Tap **"Add to Home screen"**
4. Tap **"Add"** — the app icon appears on your home screen
5. Open it — it launches full-screen like a native app ✅

### iOS (Safari)
1. Open the app URL in **Safari** (must be Safari, not Chrome)
2. Tap the **Share button** (box with arrow at bottom)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"** — the app icon appears on your home screen ✅

> **Note for iOS:** The app requires an internet connection since data comes
> from Yahoo Finance. Offline use is not supported.

---

## 🔄 Updating the App

Any change pushed to the GitHub `main` branch automatically redeploys.

To update from your desktop:
```bash
cd stock-pwa
git add .
git commit -m "Update: describe your change"
git push
```

Streamlit Cloud will detect the push and redeploy in ~30 seconds.

---

## ⚙️ Local Testing Before Deploy

```bash
cd "C:\Users\Suresh\OneDrive\Desktop\stock report\stock-pwa"
pip install -r requirements.txt
streamlit run app.py
```

To simulate a phone screen in your browser:
1. Open Chrome DevTools (F12)
2. Click the **Toggle Device Toolbar** icon (Ctrl+Shift+M)
3. Select **iPhone 14** or **Pixel 7** from the device dropdown

---

## 📊 What's Different from the Desktop Version

| Feature | Desktop (`dashboard.py`) | PWA (`app.py`) |
|---------|--------------------------|----------------|
| Sidebar | Open by default | Collapsed by default |
| Tab labels | Full names | Shortened for mobile |
| Columns | Multi-column layouts | Stack to single column on phone |
| Chart heights | Tall | Capped at 320px on phone |
| Touch targets | Standard | Min 44px (Apple HIG compliant) |
| PWA meta tags | None | ✅ iOS + Android |
| Web manifest | None | ✅ manifest.json |
| App icon | None | ✅ SVG (any size) |
| Install prompt | None | ✅ Android Chrome auto-prompt |

---

## 🌐 Alternative Free Hosting Options

If you prefer not to use Streamlit Cloud:

| Platform | Free Tier | Notes |
|----------|-----------|-------|
| **Railway** | 500hr/month | `railway up` CLI deploy |
| **Render** | 750hr/month | Connect GitHub repo |
| **Hugging Face Spaces** | Unlimited | Streamlit natively supported |
| **Google Cloud Run** | 2M req/month | Requires Docker |

---

## ❓ Troubleshooting

**"Add to Home Screen" option not showing on Android Chrome**
→ The app must be served over HTTPS (Streamlit Cloud provides this automatically).
→ You must visit the page at least twice for Chrome to offer the install prompt.

**App looks like a website, not an app, on iOS**
→ Make sure you opened it in **Safari** (not Chrome) before adding to home screen.
→ Safari is the only iOS browser that supports "Add to Home Screen" as a PWA.

**Data not loading**
→ The app calls Yahoo Finance's API. If you're behind a corporate proxy or firewall,
  some requests may be blocked. Try on a mobile data connection.

**Charts look tiny on phone**
→ Turn your phone to landscape orientation for wider charts.
→ Pinch-to-zoom also works on all Plotly charts.
