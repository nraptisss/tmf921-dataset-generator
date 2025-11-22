# Git Setup for: tmf921-dataset-generator

Repository: https://github.com/nraptisss/tmf921-dataset-generator

## ✅ Setup Steps (Run Once)

```bash
# 1. Initialize local repository
git init

# 2. Connect to GitHub
git remote add origin https://github.com/nraptisss/tmf921-dataset-generator.git

# 3. Fetch remote content
git fetch origin

# 4. Check what's on GitHub
git branch -r

# 5. Pull existing content (if any)
git pull origin main

# OR if main branch doesn't exist yet, create it:
git checkout -b main

# 6. Stage all new files
git add .

# 7. Commit
git commit -m "Reorganized structure: Added src/, docs/, experiments/ with RAG system"

# 8. Push to GitHub
git push -u origin main
```

---

## 📊 Daily Workflow

After initial setup, use these commands:

```bash
# See what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Your descriptive message"

# Push to GitHub
git push

# Pull latest from GitHub
git pull
```

---

## 🎯 VSCode Source Control

Now that Git is connected, use VSCode UI:

1. **View changes**: Click Source Control icon (Ctrl+Shift+G)
2. **Stage files**: Click + next to files
3. **Commit**: Type message and click ✓
4. **Push**: Click ⋯ → Push

---

## ⚠️ First Sync Strategy

Since you manually pushed files, you have two options:

### Option A: Keep Remote, Merge Local
```bash
git pull origin main --allow-unrelated-histories
git add .
git commit -m "Merged local changes with remote"
git push
```

### Option B: Overwrite Remote (if you want local version)
```bash
git add .
git commit -m "Complete reorganized structure"
git push -f origin main
```

**Recommend Option A** if unsure!

---

## 🔍 Check Status Anytime

```bash
git status              # See changes
git log --oneline      # See commit history
git remote -v          # See remote URL
```

---

**Repository**: https://github.com/nraptisss/tmf921-dataset-generator
