# Xilo AI Tutor - Public Deployment Guide

## Quick Start (Cloudflare Tunnel)

Deploy Xilo AI Tutor publicly in 3 steps:

### Step 1: Install Cloudflare Tunnel (One-time)
```powershell
winget install Cloudflare.cloudflared
```

### Step 2: Install flask-cors (One-time)
```powershell
conda activate llm
pip install flask-cors
```

### Step 3: Start Public Server
```powershell
# Double-click or run:
.\start_public.bat
```

This will:
1. Start the backend (separate window)
2. Wait 30 seconds for backend to initialize
3. Create a public Cloudflare Tunnel
4. Display a URL like: `https://random-word-1234.trycloudflare.com`

### Share Your Site
- Copy the `https://` URL from the terminal
- Share with anyone, anywhere
- Works on phones, tablets, desktops

### Stop the Server
- Press `Ctrl+C` in the tunnel window (stops public access)
- Close the backend window (stops backend)

---

## Manual Deployment (Alternative)

If you prefer manual control:

### Terminal 1: Start Backend
```powershell
conda activate llm
python app.py --model mistral
# Wait for: "✅ Xilo AI Tutor ready!"
```

### Terminal 2: Create Tunnel
```powershell
cloudflared tunnel --url http://localhost:5000
# Copy the https:// URL and share
```

---

## Model Selection

Choose which AI model to use:

```powershell
# Fast responses (recommended for demos):
.\start_public.bat   # Uses Mistral 7B by default

# Or manually start with specific model:
python app.py --model mistral   # Fast (8-12 tok/s)
python app.py --model llama31   # Balanced (6-10 tok/s)
python app.py --model gptoss    # Reasoning (4-7 tok/s)
```

---

## Security Notes

- ✅ Tunnel is temporary (dies when you close terminal)
- ✅ No permanent server running
- ✅ Your PC is protected (tunnel handles security)
- ✅ Free forever (no costs)
- ✅ Random URL each time (not traceable)

---

## Troubleshooting

### "cloudflared not found"
```powershell
winget install Cloudflare.cloudflared
# Restart PowerShell after installation
```

### "Backend not responding"
Wait longer than 30 seconds before creating tunnel.
Backend needs time to load AI models (especially GPT-OSS 20B).

### "CORS error in browser"
Make sure flask-cors is installed:
```powershell
pip install flask-cors
```

### Tunnel URL not working
- Check that backend is running (visit http://localhost:5000)
- Verify tunnel is active (should show "Connection established" message)
- Try a different browser or incognito mode

---

## Advanced: Persistent URL (Optional)

If you want the same URL every time:

1. Sign up for free Cloudflare account
2. Run: `cloudflared tunnel login`
3. Create named tunnel: `cloudflared tunnel create xilo`
4. Configure: `cloudflared tunnel route dns xilo xiloai.yourdomain.com`

But for testing/demos, the quick tunnel (random URL) is perfectly fine!

---

## Performance Tips

- Use **Mistral 7B** for fastest responses
- Close unnecessary programs to free VRAM
- Limit to 3-5 concurrent users (add queue system later)
- Monitor GPU usage with `intel_gpu_top` or Task Manager

---

## Support

Issues? Check:
- Backend logs in console window
- Browser console (F12) for errors
- `xilo.log` file in project directory
