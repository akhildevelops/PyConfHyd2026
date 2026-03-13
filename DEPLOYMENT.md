# Deployment Setup

This project uses GitHub Actions for CI/CD deployment to a remote server.

## GitHub Secrets Configuration

You need to configure the following secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `SSH_PRIVATE_KEY` | Your SSH private key for the remote server | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `REMOTE_HOST` | The hostname or IP of your remote server | `akhildevelops.co.in` |
| `REMOTE_USER` | SSH username for the remote server | `root` |
| `SSH_PORT` | SSH port (optional, defaults to 22) | `22` |

## How It Works

1. **Trigger**: The deployment runs automatically on every push to the `main` branch
2. **Build**: The workflow checks out your code and sets up SSH access
3. **Deploy**: Files are synced to `/apps/pyconfhyd2026/` on the remote server
4. **Service**: A systemd service is created/updated and started
5. **Verify**: The workflow checks that the service is running

## Manual Deployment

If you need to deploy manually:

```bash
# SSH into your server
ssh root@akhildevelops.co.in

# Check service status
systemctl status pyconfhyd2026

# View logs
journalctl -u pyconfhyd2026 -f

# Restart service
systemctl restart pyconfhyd2026

# Stop service
systemctl stop pyconfhyd2026
```

## Service Details

- **Service Name**: `pyconfhyd2026`
- **Installation Path**: `/apps/pyconfhyd2026/`
- **Executable**: `/usr/bin/python3 /apps/pyconfhyd2026/soccer.py`
- **Port**: 8080 (make sure this port is open in your firewall)
- **Auto-restart**: Enabled (service restarts automatically if it crashes)
- **Auto-start on boot**: Enabled

## Troubleshooting

1. **Service not starting**: Check logs with `journalctl -u pyconfhyd2026`
2. **Port already in use**: Ensure no other service is using port 8080
3. **SSH connection failed**: Verify your SSH private key and host settings in GitHub secrets
4. **Permission denied**: Ensure the remote user has write access to `/apps/`
