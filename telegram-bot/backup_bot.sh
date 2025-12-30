#!/bin/bash
# backup_bot.sh

echo "=== Telegram Bot Backup ==="
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy essential files
cp bot.py "$BACKUP_DIR/"
cp config.py "$BACKUP_DIR/"
cp requirements.txt "$BACKUP_DIR/"
cp railway.json "$BACKUP_DIR/"
cp render.yaml "$BACKUP_DIR/"
cp Procfile "$BACKUP_DIR/"
cp Dockerfile "$BACKUP_DIR/"

# Create info file
echo "Backup created: $DATE" > "$BACKUP_DIR/info.txt"
echo "Services Guide: Included in README.md" >> "$BACKUP_DIR/info.txt"

# Create ZIP
zip -r "telegram_bot_backup_$DATE.zip" "$BACKUP_DIR"

# Cleanup
rm -rf "$BACKUP_DIR"

echo "✓ Backup created: telegram_bot_backup_$DATE.zip"
echo "=== Backup Complete ==="
