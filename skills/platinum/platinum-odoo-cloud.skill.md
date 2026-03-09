# Platinum Odoo Cloud

## Purpose
Deploy Odoo Community edition on the cloud VPS using Docker with PostgreSQL, nginx reverse proxy, and automated backups.

## Prerequisites
- Gold Tier complete (local Odoo integration working)
- Cloud VPS deployed
- Docker and Docker Compose installed on VPS
- Domain for Odoo (e.g., odoo.example.com)

## Key Features
- Docker Compose stack: Odoo 17 + PostgreSQL 15
- Nginx reverse proxy with SSL termination
- Port 8069 bound to localhost only (no direct access)
- Automated daily database and filestore backups
- 7-day backup retention
- Performance tuning for 2GB RAM
- Longpolling support via separate upstream

## Implementation Steps
1. Create `docker-compose.cloud.yml` for Odoo stack
2. Create `nginx-odoo.conf` reverse proxy configuration
3. Configure SSL via certbot for Odoo domain
4. Set up automated backup script (pg_dump + filestore tar)
5. Configure backup rotation
6. Performance tune Odoo for cloud environment
7. Test MCP integration from cloud agent
8. Verify draft-only operations from cloud

## Acceptance Criteria
- [ ] Odoo accessible at `https://odoo.example.com`
- [ ] PostgreSQL data persisted in named volume
- [ ] Direct access to port 8069 blocked (localhost only)
- [ ] Daily backups running via cron
- [ ] Backups rotated (7 days retained)
- [ ] Odoo container auto-restarts on failure
- [ ] Longpolling works through nginx
- [ ] MCP server can connect to cloud Odoo

## Estimated Time
4-5 hours
