import { NextResponse } from 'next/server';
import * as OTPAuth from 'otpauth';
import QRCode from 'qrcode';

export async function POST(request) {
  try {
    const { email } = await request.json();

    // Generate secret for this user
    const secret = new OTPAuth.Secret({ size: 20 });
    
    // Create TOTP instance
    const totp = new OTPAuth.TOTP({
      issuer: 'Drift Analytics',
      label: email,
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret: secret
    });

    // Generate QR code
    const qrCode = await QRCode.toDataURL(totp.toString());

    // In production, save secret to database for this user
    // For demo, we'll store in session/localStorage
    
    return NextResponse.json({
      secret: secret.base32,
      qrCode: qrCode,
      backupCodes: generateBackupCodes()
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

function generateBackupCodes() {
  const codes = [];
  for (let i = 0; i < 8; i++) {
    codes.push(Math.random().toString(36).substring(2, 10).toUpperCase());
  }
  return codes;
}