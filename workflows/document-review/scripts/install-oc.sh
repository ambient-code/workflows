#!/usr/bin/env bash
# Install the OpenShift CLI (oc) from the OpenShift mirror.
# Intended for ubi9/python-311 container images.
set -euo pipefail

INSTALL_DIR="/usr/local/bin"

if command -v oc &>/dev/null; then
  echo "oc is already installed: $(oc version --client 2>/dev/null || echo 'oc installed')"
  echo "Binary path: $(command -v oc)"
  exit 0
fi

URL="https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz"
TARBALL="oc.tar.gz"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

echo "Downloading ${TARBALL}..."
curl -fsSL -o "${TMPDIR}/${TARBALL}" "${URL}"

echo "Extracting..."
tar xzf "${TMPDIR}/${TARBALL}" -C "${TMPDIR}"

echo "Installing oc to ${INSTALL_DIR}..."
install -m 0755 "${TMPDIR}/oc" "${INSTALL_DIR}/oc"

# Ensure the install directory is on PATH
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *) export PATH="${INSTALL_DIR}:${PATH}" ;;
esac

echo "Installed: $(oc version --client 2>/dev/null || echo 'oc installed')"
echo "Binary path: ${INSTALL_DIR}/oc"
