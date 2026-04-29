'use client';

import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';

// Initialize Stripe (replace with your publishable key)
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_xxxxx');

function CheckoutForm({ onSuccess }) {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) return;

    setProcessing(true);
    setError(null);

    // Create payment method
    const { error: pmError, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
      billing_details: {
        email,
        name,
      },
    });

    if (pmError) {
      setError(pmError.message);
      setProcessing(false);
      return;
    }

    // Send to your backend
    try {
      const response = await fetch('/api/create-trial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          name,
          paymentMethodId: paymentMethod.id,
        }),
      });

      const data = await response.json();

      if (data.success) {
        onSuccess(data);
      } else {
        setError(data.error || 'Signup failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const cardStyle = {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label>Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="John Doe"
          required
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label>Card Information</label>
        <div className="card-element-container">
          <CardElement options={{ style: cardStyle }} />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="trial-info">
        <p>✓ 7-day free trial</p>
        <p>✓ Then $97/month</p>
        <p>✓ Cancel anytime</p>
      </div>

      <button
        type="submit"
        disabled={!stripe || processing}
        className="submit-button"
      >
        {processing ? 'Processing...' : 'Start Free Trial'}
      </button>

      <p className="terms-text">
        By signing up, you agree to our{' '}
        <a href="/terms" target="_blank">Terms of Service</a> and{' '}
        <a href="/privacy" target="_blank">Privacy Policy</a>.
        You will be charged $97/month after your 7-day trial ends.
      </p>
    </form>
  );
}

export default function StripeCheckout({ onSuccess }) {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm onSuccess={onSuccess} />
    </Elements>
  );
}