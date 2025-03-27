import React, { Component, ErrorInfo, ReactNode } from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string;
}

class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = {
      hasError: false,
      errorMessage: '',
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: error.message,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error occurred: ', error);
    console.error('Error info: ', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mt-10 text-center">
          <h2 className="text-xl font-bold text-red-500">Something went wrong!</h2>
          <p className="text-gray-600">Error Message: {this.state.errorMessage}</p>
          <p className="text-gray-400">Please try again later.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
