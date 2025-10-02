#!/usr/bin/env bash

# Generates a self-signed certificate with proper Subject Alternative Names
# and optionally installs it into Ubuntu's trusted root store so that OAuth
# providers accepting HTTPS-only redirect URIs can be developed locally.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/.env.ssl"
if [[ -f "${CONFIG_FILE}" ]]; then
	# shellcheck disable=SC1090
	set -a
	source "${CONFIG_FILE}"
	set +a
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="${SSL_DOMAIN:-${HOST:-}}"
if [[ -z "${DOMAIN}" ]]; then
	echo -e "${RED}✗ SSL_DOMAIN is not set. Add it to ${CONFIG_FILE##*/} or export HOST before running.${NC}" >&2
	exit 1
fi

CERT_NAME="${SSL_CERT_NAME:-${DOMAIN}}"
CERT_DIR="${SSL_CERT_DIR:-${SCRIPT_DIR}/ssl}"
COUNTRY="${SSL_COUNTRY:-US}"
STATE="${SSL_STATE:-Development}"
LOCALITY="${SSL_LOCALITY:-Localhost}"
ORG_NAME="${SSL_ORGANIZATION:-Local Dev CA}"
ORG_UNIT="${SSL_ORG_UNIT:-Development}"
DAYS_VALID="${SSL_DAYS_VALID:-825}" # < 825 to satisfy Chrome/Firefox requirements for self-signed certs

echo -e "${BLUE}▶ Generating local HTTPS assets for ${DOMAIN}${NC}"

command -v openssl >/dev/null 2>&1 || {
	echo -e "${RED}✗ OpenSSL is required but not installed.${NC}" >&2
	exit 1
}

if [[ -d "${CERT_DIR}" && ! -w "${CERT_DIR}" ]]; then
	echo -e "${RED}✗ Directory ${CERT_DIR}/ exists but is not writable. Fix with:${NC}"
	echo -e "    sudo chown -R \"$USER\":\"$USER\" ${CERT_DIR}"
	exit 1
fi

mkdir -p "${CERT_DIR}"

OPENSSL_CONFIG="${CERT_DIR}/openssl.cnf"
cat >"${OPENSSL_CONFIG}" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = ${COUNTRY}
ST = ${STATE}
L = ${LOCALITY}
O = ${ORG_NAME}
OU = ${ORG_UNIT}
CN = ${DOMAIN}
EOF

cat >>"${OPENSSL_CONFIG}" <<EOF

[req_ext]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = *.${DOMAIN}
DNS.3 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

echo -e "${BLUE}• Creating private key${NC}"
openssl genrsa -out "${CERT_DIR}/server.key" 2048 >/dev/null

echo -e "${BLUE}• Creating certificate signing request${NC}"
openssl req -new -key "${CERT_DIR}/server.key" -out "${CERT_DIR}/server.csr" -config "${OPENSSL_CONFIG}" >/dev/null

echo -e "${BLUE}• Self-signing certificate (valid ${DAYS_VALID} days)${NC}"
openssl x509 -req \
	-in "${CERT_DIR}/server.csr" \
	-signkey "${CERT_DIR}/server.key" \
	-out "${CERT_DIR}/server.crt" \
	-days "${DAYS_VALID}" \
	-extensions req_ext \
	-extfile "${OPENSSL_CONFIG}" >/dev/null

cat "${CERT_DIR}/server.crt" >"${CERT_DIR}/server.pem"
cat "${CERT_DIR}/server.key" >>"${CERT_DIR}/server.pem"

chmod 600 "${CERT_DIR}/server.key"
chmod 644 "${CERT_DIR}/server.crt" "${CERT_DIR}/server.pem" "${CERT_DIR}/openssl.cnf"
rm -f "${CERT_DIR}/server.csr"

echo -e "${GREEN}✓ Certificates written to ${CERT_DIR}/ (server.crt, server.key, server.pem)${NC}"

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
	echo -e "${BLUE}• Installing certificate into Ubuntu trust store${NC}"
	cp "${CERT_DIR}/server.crt" "/usr/local/share/ca-certificates/${DOMAIN}.crt"
	update-ca-certificates >/dev/null
	echo -e "${GREEN}✓ Certificate trusted system-wide${NC}"

	if ! grep -q "${DOMAIN}" /etc/hosts; then
		echo "127.0.0.1    ${DOMAIN}" >>/etc/hosts
		echo -e "${GREEN}✓ Added ${DOMAIN} to /etc/hosts${NC}"
	else
		echo -e "${YELLOW}• /etc/hosts already contains ${DOMAIN}${NC}"
	fi
else
	echo -e "${YELLOW}⚠ Run with sudo to install into the system trust store and update /etc/hosts automatically.${NC}"
	echo -e "${YELLOW}   sudo $0${NC}"
fi

cat <<INSTRUCTIONS

Next steps:
	1. Ensure /etc/hosts contains: 127.0.0.1    ${DOMAIN}
	2. Restart the docker stack so nginx reloads the certificates:
			 docker compose -f deployment/docker-compose.yml down
			 docker compose -f deployment/docker-compose.yml up --build
	3. Access https://${DOMAIN} and confirm the browser trusts it (no warning).
	4. Update ${CONFIG_FILE##*/} to change domains or certificate metadata.

If your browser still distrusts the cert, remove any cached cert for ${DOMAIN}
and re-import ${CERT_DIR}/server.crt as an authority.

INSTRUCTIONS
