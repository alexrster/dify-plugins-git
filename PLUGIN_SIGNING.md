# Plugin Signing Guide

Dify requires plugins to be signed for installation when signature verification is enabled. This guide explains how to sign your plugin.

## Quick Solution: Disable Verification (Development Only)

For development and testing, you can disable signature verification in Dify:

1. **Edit Dify's `.env` file:**
   ```bash
   FORCE_VERIFYING_SIGNATURE=false
   ```

2. **Restart Dify services:**
   ```bash
   cd docker
   docker compose down
   docker compose up -d
   ```

⚠️ **Warning:** Only disable verification in development/testing environments. Never disable it in production.

## Proper Solution: Sign the Plugin

### Step 1: Generate Key Pair

```bash
dify signature generate -f git-integration-keypair
```

This creates:
- `git-integration-keypair.private.pem` (keep secret!)
- `git-integration-keypair.public.pem` (share with Dify)

### Step 2: Sign the Plugin

After building the plugin:

```bash
dify signature sign dist/git-integration-plugin.difypkg -p git-integration-keypair.private.pem
```

This creates: `dist/git-integration-plugin.signed.difypkg`

### Step 3: Verify the Signature

```bash
dify signature verify dist/git-integration-plugin.signed.difypkg -p git-integration-keypair.public.pem
```

### Step 4: Configure Dify

1. **Place public key in Dify:**
   ```bash
   mkdir -p docker/volumes/plugin_daemon/public_keys
   cp git-integration-keypair.public.pem docker/volumes/plugin_daemon/public_keys/
   ```

2. **Update `docker-compose.override.yaml`:**
   ```yaml
   services:
     plugin_daemon:
       environment:
         FORCE_VERIFYING_SIGNATURE: true
         THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: true
         THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS: /app/storage/public_keys/git-integration-keypair.public.pem
   ```

3. **Restart Dify:**
   ```bash
   cd docker
   docker compose down
   docker compose up -d
   ```

### Step 5: Install Signed Plugin

Use the `.signed.difypkg` file for installation in Dify.

## Automated Signing in Makefile

The Makefile includes a `sign` target that automates signing:

```bash
make sign
```

This will:
1. Build the plugin
2. Sign it using the private key (if available)
3. Create a signed package

## Security Notes

- **Never commit private keys** to version control
- Add `*.private.pem` to `.gitignore`
- Keep private keys secure and backed up
- Use different keys for development and production
- Rotate keys periodically

## Troubleshooting

### "Key pair not found"
- Generate keys first: `dify signature generate -f git-integration-keypair`

### "Signature verification failed"
- Ensure you're using the correct public key in Dify
- Verify the plugin was signed with the matching private key
- Check that the plugin file wasn't modified after signing

### "Plugin still rejected"
- Ensure `THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: true` in Dify config
- Verify the public key path is correct
- Restart Dify services after configuration changes

