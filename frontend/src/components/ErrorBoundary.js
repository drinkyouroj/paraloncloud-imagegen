import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Suppress browser extension errors
    if (error.message && error.message.includes('Cannot redefine property: ethereum')) {
      return null; // Don't update state, suppress the error
    }
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Suppress browser extension errors
    if (error.message && error.message.includes('Cannot redefine property: ethereum')) {
      console.warn('Suppressed browser extension error in ErrorBoundary');
      return;
    }
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      // Only show error UI for non-extension errors
      if (!this.state.error.message.includes('ethereum')) {
        return (
          <div className="error" style={{ padding: '20px', margin: '20px' }}>
            <h2>Something went wrong</h2>
            <p>{this.state.error.message}</p>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Try again
            </button>
          </div>
        );
      }
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
