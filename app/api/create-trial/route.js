import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { email, name, paymentMethodId } = await request.json();

    // Call your Python backend
    const response = await fetch(`${process.env.BACKEND_URL}/api/create-trial`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        name,
        payment_method_id: paymentMethodId,
      }),
    });

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Server error' },
      { status: 500 }
    );
  }
}