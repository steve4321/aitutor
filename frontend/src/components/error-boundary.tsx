'use client';

import { Component, type ReactNode } from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      const isDev = process.env.NODE_ENV === 'development';
      return (
        this.props.fallback || (
          <div className="flex min-h-[200px] flex-col items-center justify-center p-8 text-center" role="alert">
            <AlertTriangle className="mb-4 h-12 w-12 text-amber-500" />
            <p className="mb-2 text-lg font-medium text-slate-900 dark:text-white">
              抱歉，似乎出现了一些问题
            </p>
            <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
              请尝试刷新页面或返回首页
            </p>
            {isDev && this.state.error && (
              <div className="mb-6 w-full max-w-md rounded-lg bg-slate-100 p-4 text-left dark:bg-slate-800">
                <p className="text-xs font-mono text-red-600 dark:text-red-400">
                  {this.state.error.name}: {this.state.error.message}
                </p>
              </div>
            )}
            <div className="flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={this.handleReload}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
              >
                <RotateCcw className="h-4 w-4" />
                刷新页面
              </button>
              <button
                onClick={this.handleGoHome}
                className="flex items-center gap-2 rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
              >
                <Home className="h-4 w-4" />
                返回首页
              </button>
              <button
                onClick={this.handleRetry}
                className="text-sm text-blue-600 underline hover:text-blue-700 dark:text-blue-400"
              >
                重试
              </button>
            </div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
