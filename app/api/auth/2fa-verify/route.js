import { NextResponse } from 'next/server';
import * as OTPAuth from 'otpauth';

export async function POST(request) {
  try {
    const { email, token, secret } = await request.json();

    // Create TOTP instance with user's secret
    const totp = new OTPAuth.TOTP({
      issuer: 'Drift Analytics',
      label: email,
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret: OTPAuth.Secret.fromBase32(secret)
    });

    // Verify the token
    const delta = totp.validate({ token, window: 1 });

    if (delta !== null) {
      return NextResponse.json({ 
        success: true,
        message: '2FA verification successful'
      });
    } else {
      return NextResponse.json({ 
        success: false,
        message: 'Invalid verification code'
      }, { status: 401 });
    }
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}