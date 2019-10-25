#!/bin/bash
echo "Creating folder..."
mkdir -p /var/streaming/
echo "Changing folder owner..."
chown -R www-data:www-data /var/streaming/
echo "Mounting tmpfs filesystem..."
mount -t tmpfs -o size=300m tmpfs /var/streaming
