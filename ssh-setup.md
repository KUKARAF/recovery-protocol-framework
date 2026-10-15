# SSH Setup for Recovery Protocol

## Generate SSH Key (If You Don't Have One)

### macOS / Linux
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

When prompted:
- **File**: Press Enter (default location: `~/.ssh/id_ed25519`)
- **Passphrase**: Create a secure passphrase (or press Enter for none)

### Windows (PowerShell)
```powershell
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Same prompts as above.

## Copy Your Public Key

### macOS / Linux
```bash
cat ~/.ssh/id_ed25519.pub
```

### Windows (PowerShell)
```powershell
Get-Content ~/.ssh/id_ed25519.pub
```

Copy the entire output (starts with `ssh-ed25519`).

## Register Your SSH Key

1. Go to the Recovery Protocol web intro page
2. Paste your **public key** into the textarea
3. Click "Initialize Recovery"

**Important**: Only paste your **public key** (the `.pub` file), never your private key!

## Test Your SSH Connection

```bash
ssh -T git@recovery.example.com
```

You should see a message like:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see an error, check:
- Your public key was registered correctly
- You're using the right SSH hostname
- Your private key has correct permissions: `chmod 600 ~/.ssh/id_ed25519`

## SSH Config (Optional, Recommended)

Create `~/.ssh/config` (or add to it):

```
Host recovery.example.com
    HostName recovery.example.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
```

Then you can just use:
```bash
git clone git@recovery.example.com:recovery-protocol.git
```

## Troubleshooting

### "Permission denied (publickey)"
- Make sure you registered your **public** key (ends in `.pub`)
- Check that `~/.ssh/id_ed25519` exists and has correct permissions
- Try: `ssh-add ~/.ssh/id_ed25519`

### "Could not resolve hostname"
- Check the SSH hostname is correct
- Verify internet connection

### "Connection refused"
- Server may be down
- Try again in a few moments

---

For git workflow, see [git-setup.md](git-setup.md)
