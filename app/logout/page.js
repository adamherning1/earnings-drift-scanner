'use client';

import { useEffect } from 'react';

export default function LogoutPage() {
  useEffect(() => {
    // Clear login status
    localStorage.removeItem('isLoggedIn');
    // Redirect to homepage
    window.location.href = '/';
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      backgroundColor: '#f8f9fa'
    }}>
      <p>Logging out...</p>
    </div>
  );
}