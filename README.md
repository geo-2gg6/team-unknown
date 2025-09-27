# Privacy Scanner - Global Web App

A privacy monitoring system that works for **anyone worldwide** just by visiting the web app. No installation, no local agents, no browser extensions required!

## 🌍 Global Access

- **Works for everyone**: Just visit the Render URL from any device
- **No installation**: Pure web app, works in any modern browser
- **Real-time monitoring**: Tracks network requests as users browse
- **Smart classification**: Safe/Risk/Caution based on destination domains

## 🚀 Quick Start

1. **Deploy to Render**:
   - Push this code to GitHub
   - Connect to Render, deploy as Web Service
   - Get your public URL (e.g., `https://your-app.onrender.com`)

2. **Use globally**:
   - Share the URL with anyone worldwide
   - They visit the link and click "Start Monitoring"
   - Real-time network activity tracking begins

## 🔍 How It Works

### Browser-Based Monitoring
- **Navigation tracking**: Monitors page visits and link clicks
- **Form submissions**: Tracks form data being sent
- **Fetch requests**: Monitors AJAX/API calls
- **Real-time analysis**: Classifies domains as Safe/Risk/Caution

### Smart Classification
- **Safe**: Trusted domains (google.com, microsoft.com, github.com, etc.)
- **Risk**: Known tracking/ads domains (doubleclick.net, googlesyndication.com, etc.)
- **Caution**: Unknown or suspicious domains

### Privacy Features
- **Session-based**: Each user gets their own session
- **No permanent storage**: Data only exists during the session
- **Client-side processing**: Most analysis happens in the browser
- **HTTPS only**: All communication is encrypted

## 📊 Features

- **Real-time dashboard**: Live network activity display
- **Session statistics**: Request counts, domain analysis
- **Visual indicators**: Color-coded Safe/Risk/Caution
- **Responsive design**: Works on desktop and mobile
- **No dependencies**: Pure HTML/CSS/JavaScript

## 🛠️ Technical Details

### Backend (Flask)
- Receives browser events via REST API
- Classifies domains using pattern matching
- Stores session data temporarily
- CORS enabled for global access

### Frontend (Vanilla JS)
- Monitors browser navigation and requests
- Real-time UI updates
- Session management
- Domain classification

### Deployment
- **Render**: Easy deployment with automatic HTTPS
- **Environment**: Python 3.9+ with Flask
- **Dependencies**: Minimal (just Flask + CORS)

## 🔒 Privacy & Security

- **No data collection**: We don't store personal information
- **Session isolation**: Each user's data is separate
- **Local processing**: Most analysis happens in the browser
- **HTTPS only**: All communication is encrypted
- **No tracking**: We don't track users across sessions

## 🌐 Global Use Cases

- **Privacy awareness**: Help users understand what their browser is doing
- **Educational tool**: Teach about network privacy and tracking
- **Security audit**: Quick check of suspicious network activity
- **Research**: Analyze web tracking patterns across different sites

## 📱 Browser Support

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## 🚀 Deployment

1. Fork this repository
2. Connect to Render
3. Deploy as Web Service
4. Share the URL globally!

**That's it!** Anyone can now use your privacy scanner by just visiting the link.