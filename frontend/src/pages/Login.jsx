import React from 'react';
import { Link } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import AuthLayout from '../components/auth/AuthLayout';
import './AuthForm.css'; // Shared CSS for auth forms

const Login = () => {
  return (
    <AuthLayout>
      <div className="auth-card glass-panel">
        <h2 className="auth-title">Welcome back</h2>
        <p className="auth-subtitle">Sign in to your TR-Insight-Forge workspace.</p>

        <form className="auth-form" onSubmit={(e) => e.preventDefault()}>
          <div className="form-group">
            <label htmlFor="email">Work email</label>
            <input type="email" id="email" placeholder="you@company.com" required />
          </div>
          <div className="form-group">
            <div className="flex justify-between items-center w-full">
              <label htmlFor="password">Password</label>
              <a href="#" className="forgot-link">Forgot?</a>
            </div>
            <input type="password" id="password" placeholder="••••••••" required />
          </div>
          
          <button type="submit" className="btn btn-primary btn-block auth-submit">Sign in</button>
        </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

          <div className="flex justify-center w-full">
            <GoogleLogin
              onSuccess={credentialResponse => {
                fetch('http://localhost:8000/auth/google', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ token: credentialResponse.credential })
                })
                .then(res => res.json())
                .then(data => {
                  console.log('Login success:', data);
                  alert('Google login successful! Token saved.');
                  // Redirect or save token to context here
                })
                .catch(err => console.error('Google auth error', err));
              }}
              onError={() => {
                console.log('Login Failed');
              }}
              useOneTap
              theme="outline"
              size="large"
              shape="rectangular"
              text="continue_with"
              width="100%"
            />
          </div>

        <div className="auth-footer">
          Don't have an account? <Link to="/signup" className="auth-link">Create one</Link>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Login;
