'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import { KatexRenderer } from '@/components/math/katex-renderer';
import 'katex/dist/katex.min.css';
import 'highlight.js/styles/github.css';

function MarkdownContent({ text }: { text: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeHighlight, rehypeKatex]}
      components={{
        p: ({ children }) => <>{children}</>,
      }}
    >
      {text}
    </ReactMarkdown>
  );
}

function FullMarkdown({ text }: { text: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeHighlight, rehypeKatex]}
    >
      {text}
    </ReactMarkdown>
  );
}

export function renderWithLatex(text: string): React.ReactNode {
  if (!text) return null;
  return <MarkdownContent text={text} />;
}

export function renderMarkdownWithLatex(text: string): React.ReactNode {
  if (!text) return null;
  return <FullMarkdown text={text} />;
}

export { KatexRenderer };
