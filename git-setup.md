# Git Setup for Recovery Protocol

## Clone the Recovery Repository

Once you've registered your SSH key, you can clone the recovery repository:

```bash
git clone git@recovery.example.com:recovery-protocol.git
cd recovery-protocol
```

## Configure Git (First Time)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Basic Git Workflow

### 1. Check Status
```bash
git status
```

### 2. Make Changes
Edit task files in `missions/mission_1_data_basics/tasks/`

### 3. Stage Changes
```bash
git add missions/mission_1_data_basics/tasks/sort_signals.py
```

### 4. Commit
```bash
git commit -m "Implement sort_signals - O(n log n)"
```

### 5. Push to Optimization Branch
After validating with `recovery validate`, push to the appropriate branch:

```bash
# Push time-optimized solution
git push origin HEAD:best/time

# Push memory-optimized solution
git push origin HEAD:best/memory
```

## Pushing Best Solutions

The Recovery Protocol uses git branches to organize optimized solutions:

- **main** - Your development branch (can be any state)
- **best/time** - Your fastest solution
- **best/memory** - Your most memory-efficient solution
- **best/balanced** - Your best overall solution

You can push to multiple branches for the same code:

```bash
git push origin HEAD:best/time
git push origin HEAD:best/memory
```

## Viewing Branches

```bash
# List all branches
git branch -a

# Switch to best/time branch
git checkout best/time

# See latest commit
git log -1
```

## Pulling Updates

If the Recovery Protocol gets new missions or fixes:

```bash
git pull origin main
```

---

For SSH key setup, see [ssh-setup.md](ssh-setup.md)
