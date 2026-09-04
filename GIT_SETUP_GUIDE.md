# Git Repository Setup Guide

## ✅ What's Been Done

Your local repository is configured and ready:
- ✅ Git remote set to: `git@github.com:vishwajitr/aone_vrunda.git`
- ✅ Setup files committed (QUICKSTART.md, SETUP_COMPLETE.md, etc.)
- ✅ `.env` file is protected by `.gitignore` - **will NOT be committed**
- ✅ Database files (`.db`) are protected - **will NOT be committed**
- ✅ All secret keys are safe and will never be committed

## 🔐 Security Verification

Run these commands to verify secrets are protected:

```bash
# Should return ".env" (meaning it's ignored)
git check-ignore .env

# Should show no .env or .db files
git status

# Check what's staged before any commit
git diff --cached --name-only
```

## 🚀 Next Steps

### Step 1: Ensure GitHub Repository Exists

The repository `aone_vrunda` must exist on GitHub first:

**Option A: Create via GitHub Web UI**
1. Go to: https://github.com/new
2. Repository name: `aone_vrunda`
3. Set to Private (recommended for trading apps)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

**Option B: Create via GitHub CLI**
```bash
gh repo create vishwajitr/aone_vrunda --private --source=. --remote=origin
```

### Step 2: Set Up SSH Authentication

If you haven't set up SSH keys for GitHub:

1. **Check for existing SSH keys:**
   ```bash
   ls -la ~/.ssh
   # Look for id_rsa.pub or id_ed25519.pub
   ```

2. **Generate new SSH key (if needed):**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Enter a passphrase (recommended)
   ```

3. **Add SSH key to ssh-agent:**
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **Copy SSH public key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Copy the output
   ```

5. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your public key
   - Click "Add SSH key"

6. **Test SSH connection:**
   ```bash
   ssh -T git@github.com
   # Should see: "Hi vishwajitr! You've successfully authenticated..."
   ```

### Step 3: Push to GitHub

Once repository exists and SSH is configured:

```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo

# Push your changes
git push -u origin main
```

### Step 4: Verify on GitHub

After pushing, verify:
1. Go to: https://github.com/vishwajitr/aone_vrunda
2. Check that your files are there
3. **Verify .env is NOT visible** (should not be listed)
4. **Verify no .db files** are visible

## 🔄 Daily Workflow

### Making Changes

```bash
# 1. Check status
git status

# 2. Add files (git automatically skips ignored files)
git add .

# 3. Verify what will be committed
git diff --cached --name-only

# 4. Commit
git commit -m "Your commit message"

# 5. Push
git push
```

### Before Every Commit - Security Check

**ALWAYS verify no secrets are being committed:**

```bash
# Check for secrets in staged files
git diff --cached | grep -i "api_key\|secret\|password\|token\|pepper\|salt"

# If it finds anything, review carefully
# Only placeholders/examples in docs are OK
# Real secrets = DO NOT COMMIT
```

## 🚨 Emergency: Accidentally Committed a Secret

If you accidentally commit a secret:

1. **IMMEDIATELY rotate the secret:**
   ```bash
   # Generate new keys
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Update .env with new key
   # Update in broker portal if it's a broker API key
   ```

2. **Remove from Git history:**
   ```bash
   # For recent commit (not pushed yet)
   git reset --soft HEAD~1
   
   # For already pushed commits, you need:
   # - git filter-branch or BFG Repo-Cleaner
   # - Force push to remote
   # This is complex - see GitHub docs
   ```

3. **Verify removal:**
   ```bash
   git log --all --full-history -- .env
   # Should show no history
   ```

## 📋 Protected Files (Never Committed)

These files are automatically excluded by `.gitignore`:

### 🔐 Secrets & Configuration
- `.env` (all variants: .env.*, *.env, env.backup)
- `keys/` (OAuth signing keys)
- `db/strategy_encryption.key`

### 💾 Databases
- `*.db` (SQLite databases)
- `*.duckdb` (DuckDB databases)
- `*.sqlite`

### 📁 Personal Data
- `workspace/**` (your strategies and research)
- `log/` (application logs)
- `tmp/` (temporary files)

### 🏗️ Build Artifacts
- `.venv/` (Python virtual environment)
- `node_modules/` (Node packages)
- `dist/`, `build/` (build output)

## ✅ Current Commit

Your initial commit includes:
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `SETUP_COMPLETE.md` - Detailed setup docs
- ✅ `START_HERE.txt` - Quick reference
- ✅ `configure_broker.sh` - Broker setup script
- ✅ `.gitignore.security` - Security documentation

**Verified:** No secrets, no databases, no sensitive files.

## 🆘 Need Help?

**Git Issues:**
- GitHub SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- Git Basics: https://git-scm.com/book/en/v2

**OpenAlgo Issues:**
- Discord: https://www.openalgo.in/discord
- GitHub: https://github.com/marketcalls/openalgo/issues

---

**Repository:** git@github.com:vishwajitr/aone_vrunda.git  
**Setup Date:** September 4, 2026  
**Status:** Ready to push (SSH authentication may be required)
