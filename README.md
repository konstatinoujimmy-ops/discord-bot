# 🤖 Discord Bot 24/7 για Replit

Ένας πλήρως λειτουργικός Discord bot που τρέχει 24/7 στο Replit χρησιμοποιώντας δωρεάν μεθόδους keep-alive.

## ✨ Χαρακτηριστικά

- **24/7 Λειτουργία**: Keep-alive μηχανισμός με Flask web server
- **Αυτόματη Επανεκκίνηση**: Error handling και auto-restart capabilities
- **Web Dashboard**: Status page με οδηγίες setup
- **Ελληνικό UI**: Όλες οι εντολές και μηνύματα στα ελληνικά
- **Logging**: Detailed logging για debugging
- **Environment Variables**: Ασφαλής διαχείριση tokens

## 🚀 Εγκατάσταση στο Replit

### Βήμα 1: Setup Bot
1. Κάντε fork αυτό το repository στο Replit
2. Πηγαίνετε στο [Discord Developer Portal](https://discord.com/developers/applications)
3. Δημιουργήστε νέα εφαρμογή και bot
4. Αντιγράψτε το Bot Token

### Βήμα 2: Ρύθμιση Secrets
1. Στο Replit, πηγαίνετε στην καρτέλα "Secrets" (🔒)
2. Προσθέστε νέο secret:
   - **Key**: `DISCORD_TOKEN`
   - **Value**: Το token του bot σας

### Βήμα 3: Εκκίνηση Bot
1. Πατήστε το κουμπί "Run"
2. Περιμένετε να ξεκινήσει ο bot και ο web server
3. Επισκεφτείτε το URL του Repl για να δείτε το status page

### Βήμα 4: Setup 24/7 Keep-Alive

#### Μέθοδος 1: UptimeRobot (Προτεινόμενο)
1. Πηγαίνετε στο [UptimeRobot](https://uptimerobot.com) και κάντε δωρεάν εγγραφή
2. Δημιουργήστε νέο Monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: `https://your-repl-name.your-username.repl.co/ping`
   - **Monitoring Interval**: 5 λεπτά
   - **Monitor Name**: Discord Bot Keep-Alive

#### Μέθοδος 2: Cron-Job.org
1. Πηγαίνετε στο [cron-job.org](https://cron-job.org)
2. Δημιουργήστε νέο Cron Job:
   - **URL**: `https://your-repl-name.your-username.repl.co/ping`
   - **Interval**: Κάθε 5 λεπτά

#### Μέθοδος 3: Custom Script (Προχωρημένα)
Δημιουργήστε ένα Python script σε άλλο service που κάνει ping το bot κάθε 4 λεπτά.

## 🎮 Διαθέσιμες Εντολές

| Εντολή | Περιγραφή |
|--------|-----------|
| `!ping` | Έλεγχος καθυστέρησης bot |
| `!info` | Πληροφορίες για το bot |
| `!status` | Κατάσταση λειτουργίας bot |
| `!hello` | Απλός χαιρετισμός |
| `!help` | Εμφάνιση όλων των εντολών |
| `!restart` | Επανεκκίνηση bot (μόνο owner) |

## 📁 Δομή Project

