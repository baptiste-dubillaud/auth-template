#!/bin/bash

# Script to generate self-signed SSL certificates for local development

set -e

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Domain name from environment
DOMAIN="${HOST:-template-app.dev}"

echo "Generating SSL certificate for domain: $DOMAIN"

# Generate private key
openssl genrsa -out ssl/server.key 2048

# Generate certificate signing request
openssl req -new -key ssl/server.key -out ssl/server.csr -subj "/C=US/ST=Development/L=Local/O=Auth Template/OU=Development/CN=$DOMAIN"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/server.csr -signkey ssl/server.key -out ssl/server.crt

# Create certificate bundle (some applications need this)
cat ssl/server.crt > ssl/server.pem
cat ssl/server.key >> ssl/server.pem

# Set appropriate permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt ssl/server.pem ssl/server.csr

echo "SSL certificates generated successfully!"
echo "Certificate: ssl/server.crt"
echo "Private Key: ssl/server.key"
echo "Certificate Bundle: ssl/server.pem"
echo ""
echo "To trust this certificate in your browser, you'll need to:"
echo "1. Open the certificate file (ssl/server.crt) in your browser"
echo "2. Add it to your trusted certificates"
echo "3. Or accept the security warning when accessing https://$DOMAIN"
echo ""
echo "Note: Remember to add '$DOMAIN' to your /etc/hosts file:"
echo "127.0.0.1    $DOMAIN"
