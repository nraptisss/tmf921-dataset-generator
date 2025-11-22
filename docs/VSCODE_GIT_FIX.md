# VSCode Git Integration Fix

## Quick Fix Steps

### 1. Restart VSCode
**Most common solution**: Close and reopen VSCode completely.

Git was just installed, so VSCode's PATH hasn't updated yet.

### 2. If Restart Doesn't Work

**Configure Git Path in VSCode**:

1. Open VSCode Settings (`Ctrl+,`)
2. Search for: `git.path`
3. Click "Edit in settings.json"
4. Add this line (adjust path if Git installed elsewhere):

```json
{
    "git.path": "C:\\Program Files\\Git\\bin\\git.exe"
}
```

### 3. Check Git Installation Path

Run in PowerShell:
```powershell
where.exe git
```

This shows Git's location. Use that path in VSCode settings.

### 4. Verify Git Works in Terminal

In VSCode terminal (`` Ctrl+` ``):
```bash
git --version
```

Should show: `git version 2.x.x`

### 5. Enable Git in VSCode

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Git: Enable`
3. Press Enter

---

## Quick Test

After fixing, test Git in VSCode:

1. Open Source Control panel (Ctrl+Shift+G)
2. Should see your repository
3. Should see changed files

---

## Alternative: Use VSCode Terminal

Even if VSCode UI doesn't show Git, you can use terminal:

```bash
# In VSCode terminal (Ctrl+`)
git status
git add .
git commit -m "Your message"
git push
```

---

## If Still Not Working

**Install Path might be different**:
- Default: `C:\Program Files\Git\bin\git.exe`
- Alternative: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Git\bin\git.exe`

**Check if Git is in PATH**:
1. Win+R → Type `sysdm.cpl`
2. Advanced → Environment Variables
3. System Variables → Path
4. Should contain Git path

---

**Most likely**: Just restart VSCode! 🔄
