# Platinum Cloud Deploy

## Purpose
Deploy the AI Employee system to an Ubuntu cloud VPS for 24/7 operation with systemd services, nginx reverse proxy, and automated SSL.

## Prerequisites
- Gold Tier complete
- Ubuntu 22.04+ VPS (2GB RAM, 2 vCPU, 40GB disk minimum)
- Domain name with DNS pointed to VPS IP
- SSH root access

## Key Features
- Automated deployment script (`deploy.sh`)
- Systemd service units for Dashboard, API, and Watchers
- Nginx reverse proxy with gzip, security headers, WebSocket support
- Let's Encrypt SSL via certbot
- Automated daily backups with 7-day retention
- Health endpoint for monitoring
- Environment-based configuration (`.env` file)

## Implementation Steps
1. Create `deploy.sh` script that provisions Ubuntu VPS
2. Create systemd unit files for each service
3. Create nginx configuration with SSL placeholders
4. Create backup script with rotation
5. Test deployment on fresh VPS
6. Verify all services auto-restart on failure
7. Verify SSL auto-renewal with certbot timer

## Acceptance Criteria
- [ ] `deploy.sh` runs successfully on fresh Ubuntu 22.04
- [ ] All three systemd services running and enabled
- [ ] nginx serves dashboard on port 443
- [ ] API accessible via nginx reverse proxy
- [ ] SSL certificate installed and valid
- [ ] Services restart automatically after `kill -9`
- [ ] Backup script creates compressed archive
- [ ] Old backups rotated (max 7 kept)

## Estimated Time
6-8 hours
