# Phishing URL Detector

A web app that checks if a URL looks like a phishing site or a safe one, and explains why. Built with Python, scikit-learn, and Flask, deployed live on Render.

**Live demo:** https://phishing-url-detector-oey4.onrender.com
*(It's on Render's free tier, so if nobody's used it in a while it goes to sleep. First load can take 30-60 seconds to wake up — just wait it out, it's not broken.)*

## Why I built this

I'm a 12th grader interested in computer science, and I wanted to explore cybersecurity along with it. Most beginner ML projects I saw were just a notebook that prints an accuracy score and stops there. I wanted to actually build something you could use — type in a real URL and get a real answer, not just a number in a Jupyter notebook.

Phishing felt like a good problem to pick because it's something people actually deal with — fake bank login pages, sketchy links in emails, stuff like that. And it let me combine two things I'm interested in instead of picking just one.

## What it actually does

1. You type in a URL
2. The app checks 22 different things about it — is there a valid SSL certificate, where do the page's links actually go, does the domain use tricks like an IP address instead of a real name, stuff like that
3. A machine learning model (trained on over 11,000 real websites) predicts whether it looks safe or phishing
4. You get a confidence percentage and a list of exactly which red flags got triggered — not just a yes/no

## Tech stack

- **Python** — the whole thing is written in it
- **scikit-learn** — for training the model (Random Forest)
- **pandas** — for handling the dataset
- **Flask** — runs the actual website
- **requests + BeautifulSoup** — fetch and read a webpage's HTML
- **ssl / socket** — check SSL certificates and DNS
- **Bootstrap 5** — for styling (didn't want to hand-write CSS for everything)
- **Render + gunicorn** — hosting

## The model

Trained on the UCI Phishing Websites dataset (11,055 real websites, already labeled safe or phishing). Tried Logistic Regression first (92.4% accuracy) and Random Forest (96.7%) — went with Random Forest since it also had way fewer false negatives, meaning it misses fewer actual phishing sites, which matters more than raw accuracy for something like this.

**Honest thing I ran into:** the dataset's original 30 features included some that depended on services that don't really exist anymore (like the old Google PageRank API). So a model trained on all 30 couldn't actually be used on a real URL someone types in today — it would need data that's just not available anymore. I had to figure out which of the 30 features I could actually compute live, dropped 8 that I couldn't, and retrained on the remaining 22. Accuracy dropped a little (96.7% → 95.3%) but now it actually works on real websites, which is the whole point.

**Top features the model relies on most:**
- Whether the SSL certificate is valid (32.6% of the model's decision-making)
- Where the page's links actually point to (24.6%)

Together those two features account for over half of what the model bases its decision on — which honestly lines up with how a person would manually check if a site looks sketchy.

## Known limitations (being honest about this)

- **Free hosting sleeps when unused.** Not a bug, just how free Render instances work.
- **A bigger one I found while testing:** when a page completely fails to load (like a dead domain), some of the checks default to "looks fine" just because there's no evidence of anything specifically bad — but "no evidence" isn't the same as "confirmed safe." So a dead or broken URL can sometimes end up with a weirdly low-confidence "safe" result instead of being flagged harder. I noticed this during testing and decided to document it honestly here instead of rushing a fix in, since I wanted to actually understand it properly first rather than patch it quickly.

## What I'd want to improve later

- Fix the limitation above properly — probably by treating "couldn't check" as its own separate signal instead of defaulting to safe
- Clean up the GitHub commit history a bit (some of my early deployment commits were just me debugging in real time)
- Maybe try adding a couple more features if I can find a reliable way to compute them live

## Running it locally

\`\`\`bash
git clone https://github.com/hemashribellary/phishing-url-detector
cd phishing-url-detector
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python build.py             # trains and saves the model
python app.py
\`\`\`

Then open `http://localhost:5000` in your browser.

## A note on the debugging process

Getting this deployed wasn't as simple as "push code, it works." At one point the site would just hang forever when checking certain URLs. I spent a while assuming it was a server timeout issue and fixed a bunch of backend stuff (which was still good to fix), but the actual bug turned out to be a one-line JavaScript issue — disabling the submit button too early was silently cancelling the form submission in Firefox, so the request never even reached my server. Found it by checking the server logs (nothing was showing up) and then the browser's network tab (confirmed the request was never sent). That was probably the most useful debugging lesson from this whole project — check both ends, not just the one you assume is broken.

---

Built by a 12th grader still learning — feedback welcome.