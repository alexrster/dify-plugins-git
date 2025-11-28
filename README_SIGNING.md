# Plugin Installation - Signature Verification

## Error: "plugin verification has been enabled, and the plugin you want to install has a bad signature"

This error occurs when Dify's plugin signature verification is enabled but the plugin is not signed or has an invalid signature.

## Solution Options

### Option 1: Disable Verification (Development/Testing Only)

**⚠️ Only use this for development/testing environments!**

1. Edit Dify's `.env` file:
   ```bash
   FORCE_VERIFYING_SIGNATURE=false
   ```

2. Restart Dify:
   ```bash
   cd docker
   docker compose down
   docker compose up -d
   ```

### Option 2: Sign the Plugin (Recommended for Production)

#### Quick Start

1. **Generate signing keys:**
   ```bash
   make generate-keys
   ```

2. **Build and sign the plugin:**
   ```bash
   make sign
   ```

3. **Install the signed plugin:**
   - Use `dist/git-integration-plugin.signed.difypkg` instead of the unsigned version

4. **Configure Dify to accept your signature:**
   - Copy `git-integration-keypair.public.pem` to Dify's public keys directory
   - Update Dify's configuration (see `PLUGIN_SIGNING.md` for details)

For detailed instructions, see [PLUGIN_SIGNING.md](PLUGIN_SIGNING.md).

## Makefile Commands

- `make generate-keys` - Generate signing key pair
- `make sign` - Build and sign the plugin
- `make verify-signature` - Verify the plugin signature

## Security Reminder

- **Never commit private keys** (`.private.pem` files)
- Keep private keys secure
- Use different keys for development and production

