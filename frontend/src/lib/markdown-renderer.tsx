'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
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

export function MarkdownContentComponent({ text }: { text: string }) {
  return <MarkdownContent text={text} />;
}

export function FullMarkdownComponent({ text }: { text: string }) {
  return <FullMarkdown text={text} />;
}