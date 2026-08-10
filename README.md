# Phishing URL Detector

A web app that checks if a URL looks like a phishing site or a safe one, and explains why. Built with Python, scikit-learn, and Flask, deployed live on Render.

![Phishing detector result page showing risk factors](image.png)

Live demo: https://phishing-url-detector-oey4.onrender.com (Free tier, sleeps when unused, first load takes 30-60 sec)

**Why I built this:** Wanted something you could actually use, not just a notebook that prints an accuracy score.

**What it does**
* Checks 22 things about a URL: SSL certificate, where links point, IP-address tricks, and more
* Random Forest model, trained on 11,000+ real websites
* Returns a confidence % and the exact red flags triggered, not just yes/no

**Tech:** Python, Flask, scikit-learn, pandas, BeautifulSoup, Bootstrap 5, Render/gunicorn

**The model:** 95.3% accuracy, catches 93/100 real phishing sites. Started with 30 dataset features but 8 depended on APIs that no longer exist (like Google PageRank), so I dropped those and retrained on the 22 I could actually compute live. Accuracy dropped slightly, from 96.7% to 95.3%, but now it works on real URLs. Biggest factors: SSL validity (32.6%) and link destinations (24.6%).

**Known limitation:** dead/broken URLs sometimes default to "looks safe" since there's no evidence found, when really it just couldn't check. Found this in testing, documenting it honestly rather than rushing a fix.

**Debugging note:** Site would randomly hang. Assumed server timeout, fixed backend stuff, but the real bug was that JS was disabling the submit button too early, silently killing form submission in Firefox. Found it by checking server logs (empty) then the browser network tab (request never sent). Lesson: check both ends.

Built by a 12th grader still learning. Feedback welcome.
