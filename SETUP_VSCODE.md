# Setting Up Link Checker Agent in VS Code with Virtual Environment

## Step-by-Step Setup Guide

### Part 1: Open Project in VS Code

1. **Open VS Code**
2. Click **File → Open Folder**
3. Select your `link-checker-agent-github` folder
4. Click **Open**

---

### Part 2: Create Virtual Environment (IMPORTANT!)

**Step 1: Open Terminal in VS Code**
- Click **Terminal → New Terminal** (at the top menu)
- Or press `Ctrl + ` (backtick)

**Step 2: Create Virtual Environment**

On Mac:
```bash
python3 -m venv venv
```

**What this does:** Creates a `venv` folder with isolated Python

---

### Part 3: Activate Virtual Environment

On Mac:
```bash
source venv/bin/activate
```

**You should see:** `(venv)` appear in the terminal

---

### Part 4: Install Dependencies

With `(venv)` showing in terminal:
```bash
pip install -r requirements.txt
```

Wait for it to finish.

---

### Part 5: Select Python Interpreter in VS Code

1. **Press `Cmd + Shift + P`**
2. Type: `Python: Select Interpreter`
3. Look for **`./venv/bin/python`** and click it

---

## Now You're Ready! 🎉

### First Run

1. **Open terminal** (Ctrl + `)
2. **Make sure `(venv)` shows in terminal**
3. **Run:**
```bash
python link_checker_agent.py
```

4. **When prompted, enter:**
```
archetypestainedglass.com
```

5. **It will generate `link_report.json`**

---

## Common Issues

**"python: command not found"**
- Use `python3` instead

**"(venv) doesn't appear"**
- Try: `source venv/bin/activate`

**"ModuleNotFoundError: aiohttp"**
- Make sure `(venv)` shows and run `pip install -r requirements.txt`

---

**You're all set! Happy scanning!** 🎉
