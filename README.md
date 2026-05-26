# InspireWorks IVR Demo — Plivo Voice API

> A demo IVR system built for the Plivo Product Operations Engineer Intern assignment.  
> Demonstrates outbound calling, caller authentication via OTP, and a multi-level interactive voice menu — all powered by Plivo's Voice API and XML.

---

## What it does

When triggered, the system:

1. **Makes an outbound call** from a Plivo number to any target phone number
2. **Authenticates the caller** by prompting them to enter a 4-digit OTP (birthdate in DDMM format) via their keypad — re-prompting on incorrect input until the correct OTP is entered
3. **Presents a 2-level IVR menu:**
   - **Level 1** — Language selection: Press 1 for English, Press 2 for Spanish
   - **Level 2** — Action selection: Press 1 to hear an audio message, Press 2 to connect to a live associate

---

## IVR Call Flow

```
Outbound call initiated
  └── OTP Prompt (4 digits via keypad)
        ├── Wrong OTP → re-prompt (up to 5 retries)
        └── Correct OTP → authenticated ✅
              └── Level 1: Language Selection
                    ├── Press 1 → English
                    │     └── Level 2: Action Menu
                    │           ├── Press 1 → Play audio message 🎵
                    │           └── Press 2 → Forward to live associate 📞
                    └── Press 2 → Spanish
                          └── Level 2: Action Menu
                                ├── Press 1 → Play audio message 🎵
                                └── Press 2 → Forward to live associate 📞
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.x |
| Web Framework | Flask |
| Production Server | Waitress |
| Voice API | Plivo REST API + Plivo XML |
| Public Tunnel | Cloudflare Tunnel (cloudflared) |

---

## Project Structure

```
plivo-ivr/
├── app.py        # Core Flask app — all IVR routes and Plivo XML logic
├── run.py        # Production server runner using Waitress
└── README.md     # Setup, credentials, and usage guide
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Rish0310/plivo-ivr.git
cd plivo-ivr
```

### 2. Install dependencies
```bash
pip install flask requests waitress
```

### 3. Set up a public tunnel using Cloudflare
Download and install cloudflared, then run:
```bash
cloudflared tunnel --url http://localhost:5000
```
Copy the generated URL — it will look like:
```
https://xxxx-xxxx-xxxx.trycloudflare.com
```

### 4. Update BASE_URL in app.py
Open `app.py` and set:
```python
BASE_URL = "https://xxxx-xxxx-xxxx.trycloudflare.com"
```

### 5. Run the server
```bash
python run.py
```
You should see:
```
✅ IVR running on http://localhost:5000
```

### 6. Trigger a call
Open `http://localhost:5000` in your browser, enter a phone number in `+91XXXXXXXXXX` format, and click **Make Call**.

---


## How it works — under the hood

1. The **web UI** sends a POST request to `/make_call` with the target number
2. Flask calls **Plivo's REST API** to initiate an outbound call, passing the `answer_url` pointing to `/ivr/otp`
3. When the call is answered, Plivo fetches **Plivo XML** from `/ivr/otp` which prompts for OTP using `<GetDigits>`
4. DTMF digits are sent to `/ivr/verify_otp` — correct OTP redirects to `/ivr/level1`, wrong OTP re-prompts
5. Each IVR level uses `<GetDigits>` for input, `<Speak>` for voice prompts, `<Play>` for audio, and `<Dial>` for call forwarding
6. **Cloudflare Tunnel** makes the local Flask server publicly accessible so Plivo can reach the webhook URLs

---

## Demo Video

The demo video covers:
- Triggering an outbound call via the web UI
- Entering a wrong OTP → hearing the re-prompt
- Entering the correct OTP → accessing the IVR
- Navigating Level 1 (language) → Level 2 (action)
- Audio message playback
- Call forwarding to live associate

---

*Built by Rishika Gitta | Plivo Product Operations Engineer Intern Assignment*
