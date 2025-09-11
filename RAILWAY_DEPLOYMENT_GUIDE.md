# 🚂 Railway Deployment Guide για Discord Bot

## Προαπαιτούμενα
1. GitHub account
2. Railway account ([railway.app](https://railway.app))
3. Discord Bot Token (ήδη το έχεις στα Replit Secrets)

## Βήμα 1: Δημιουργία GitHub Repository

1. Πήγαινε στο GitHub και δημιούργησε νέο repository
2. Clone το repository τοπικά ή χρησιμοποίησε το GitHub web interface
3. Copy όλα τα αρχεία από το Replit project:
   - `main.py`
   - `bot.py`
   - `keep_alive.py`
   - `auto_ping.py`
   - `requirements.txt` (νέο αρχείο που δημιουργήθηκε)
   - `railway.toml` (νέο αρχείο που δημιουργήθηκε)
   - `Procfile` (νέο αρχείο που δημιουργήθηκε)

## Βήμα 2: Railway Setup

1. **Συνδέσου στο Railway:**
   - Πήγαινε στο [railway.app](https://railway.app)
   - Sign up/Login με το GitHub account σου

2. **Δημιούργησε νέο Project:**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Επέλεξε το repository που έφτιαξες

3. **Environment Variables:**
   - Στο Railway dashboard, πήγαινε στο "Variables" tab
   - Πρόσθεσε μόνο το DISCORD_TOKEN:
     ```
     DISCORD_TOKEN=<το_discord_token_σου>
     ```
   - **Σημείωση:** Το PORT δε χρειάζεται να το ορίσεις - το Railway το παρέχει αυτόματα

## Βήμα 3: Railway Configuration

Το Railway θα διαβάσει αυτόματα το `railway.toml` file και θα:
- Build το project χρησιμοποιώντας Nixpacks
- Start το bot με την εντολή `python main.py`
- Monitor την υγεία του bot μέσω του `/` endpoint
- Auto-restart σε περίπτωση crash

## Βήμα 4: Domain και URLs

Μόλις deploy το bot:
1. Το Railway θα σου δώσει ένα public URL (π.χ. `mybot-production.up.railway.app`)
2. Αυτό το URL θα είναι διαθέσιμο 24/7
3. Το Keep-alive endpoint θα είναι: `https://your-app.up.railway.app/ping`

## Βήμα 5: Verification

1. **Check Deployment Logs:**
   - Στο Railway dashboard, πήγαινε στο "Logs" tab
   - Βεβαιώσου ότι βλέπεις: "✅ Bot online ως [Bot Name]"

2. **Test Keep-Alive:**
   - Επισκέψου το public URL του bot
   - Θα δεις την status page με πληροφορίες
   - Test το `/ping` endpoint

3. **Verify Discord Connection:**
   - Έλεγξε ότι ο bot είναι online στον Discord server σου

## Βήμα 6: Cleanup (Προαιρετικό)

Μόλις confirm ότι όλα δουλεύουν στο Railway:
- Μπορείς να σταματήσεις το Replit bot
- Το Railway bot θα τρέχει 24/7 χωρίς περιορισμούς

## Πλεονεκτήματα Railway vs Replit

✅ **24/7 Uptime** - Δεν σταματάει ποτέ
✅ **No Sleep Mode** - Πάντα ενεργός  
✅ **Better Performance** - Πιο γρήγοροι servers
✅ **Reliable** - Λιγότερα 502 errors
✅ **Auto-scaling** - Automatic resource management
✅ **Professional Hosting** - Production-ready environment

## Troubleshooting

### Bot δε συνδέεται:
- Έλεγξε το DISCORD_TOKEN environment variable
- Check τα deployment logs για errors

### 502/503 Errors:
- Βεβαιώσου ότι το PORT environment variable είναι set
- Check ότι το Flask server bind στο σωστό port

### Build Failures:
- Έλεγξε ότι το `requirements.txt` έχει όλες τις dependencies
- Δες τα build logs για specific errors

## Κόστος

- Railway έχει δωρεάν tier με $5 πίστωση το μήνα
- Ένας Discord bot συνήθως καταναλώνει ~$1-2/μήνα
- Πολύ πιο οικονομικό από paid Replit plans για 24/7 hosting

## Support

Αν έχεις προβλήματα:
1. Check τα Railway logs
2. Test το bot τοπικά πρώτα
3. Verify environment variables
4. Check Discord permissions