#!/bin/bash

# Generate self-signed SSL certificates for development

set -e

# Create SSL directory
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=CA/L=San Francisco/O=Immanuel MCP Server/OU=Development/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# Set appropriate permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

# Clean up CSR
rm ssl/cert.csr

echo "SSL certificates generated successfully!"
echo "Certificate: ssl/cert.pem"
echo "Private key: ssl/key.pem"
echo ""
echo "Note: These are self-signed certificates for development use only."
echo "For production, use certificates from a trusted CA."