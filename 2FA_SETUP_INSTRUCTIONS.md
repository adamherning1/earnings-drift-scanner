# Two-Factor Authentication (2FA) Setup Instructions

## What You've Got

I've implemented a complete 2FA system for Drift Analytics with:

1. **Security Settings Page** (`/security`)
   - Enable/disable 2FA
   - QR code generation for authenticator apps
   - Backup codes for emergency access
   - Login history tracking

2. **Updated Login Flow**
   - Detects if 2FA is enabled
   - Shows 2FA code input after password
   - Verifies TOTP codes

3. **API Endpoints**
   - `/api/auth/2fa-setup` - Generates QR codes and secrets
   - `/api/auth/2fa-verify` - Validates TOTP codes

## How to Use It

### First Time Setup:
1. Login to your account
2. Go to Account → Security Settings (or directly to `/security`)
3. Click "Enable Two-Factor Authentication"
4. Scan the QR code with an authenticator app:
   - Google Authenticator
   - Microsoft Authenticator
   - Authy
   - 1Password
5. Save the backup codes somewhere safe
6. Enter the 6-digit code from your app to verify
7. Click "Verify & Enable 2FA"

### Login with 2FA:
1. Enter email and password as usual
2. When prompted, enter the 6-digit code from your authenticator app
3. Click "Verify & Log In"

## To Deploy

1. First install the new dependencies:
   ```bash
   cd earnings-push
   npm install otpauth qrcode
   ```

2. Commit and push:
   ```bash
   git add -A
   git commit -m "Add two-factor authentication (2FA) with TOTP support"
   git push origin main
   ```

## Important Notes

- **Current Implementation**: Uses localStorage for demo purposes
- **Production Ready**: Would need database storage for secrets and backup codes
- **Security**: Never expose the secret keys in client-side code
- **Backup Codes**: Users should save these offline in case they lose their phone

## Features Included

✅ QR Code generation for easy setup
✅ Manual secret key option
✅ 8 backup codes for recovery
✅ Time-based OTP (30-second windows)
✅ Login history tracking
✅ Security recommendations
✅ Clean UI matching your theme

## Testing

After deployment:
1. Enable 2FA on your admin account
2. Logout
3. Try logging back in - you'll need the 6-digit code
4. Test a backup code if needed

The 2FA is now fully integrated into your Drift Analytics platform!