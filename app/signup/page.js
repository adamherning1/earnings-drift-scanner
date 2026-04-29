'use client';

import { useEffect } from 'react';

export default function SignupPage() {
  useEffect(() => {
    // Redirect to membership page which has Stripe checkout
    window.location.href = '/membership';
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      backgroundColor: '#f8f9fa'
    }}>
      <p>Redirecting to checkout...</p>
    </div>
  );
}