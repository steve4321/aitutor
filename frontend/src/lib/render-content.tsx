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

export function stripLatexForSpeech(text: string): string {
  if (!text) return '';

  let result = text;

  const latexReplacements: Array<[RegExp, string]> = [
    [/\\frac\{([^{}]*)\}\{([^{}]*)\}/g, '$1分之$2'],
    [/\\sqrt\{([^{}]*)\}/g, '根号$1'],
    [/\\times/g, '乘以'],
    [/\\div/g, '除以'],
    [/\\cdot/g, '乘'],
    [/\\pm/g, '正负'],
    [/\\leq/g, '小于等于'],
    [/\\le/g, '小于等于'],
    [/\\geq/g, '大于等于'],
    [/\\ge/g, '大于等于'],
    [/\\neq/g, '不等于'],
    [/\\ne/g, '不等于'],
    [/\\approx/g, '约等于'],
    [/\\equiv/g, '恒等于'],
    [/\\pi/g, '圆周率'],
    [/\\theta/g, '西塔'],
    [/\\alpha/g, '阿尔法'],
    [/\\beta/g, '贝塔'],
    [/\\gamma/g, '伽马'],
    [/\\delta/g, '德尔塔'],
    [/\\Delta/g, '德尔塔'],
    [/\\infty/g, '无穷'],
    [/\\sum/g, '求和'],
    [/\\rightarrow/g, '推导出'],
    [/\\Rightarrow/g, '推导出'],
    [/\\to/g, '到'],
    [/\\circ/g, '度'],
    [/\\degree/g, '度'],
    [/\\angle/g, '角'],
    [/\\triangle/g, '三角形'],
    [/\\perp/g, '垂直于'],
    [/\\parallel/g, '平行于'],
    [/\\sin/g, '正弦'],
    [/\\cos/g, '余弦'],
    [/\\tan/g, '正切'],
    [/\\log/g, '对数'],
    [/\\ln/g, '自然对数'],
    [/\\left\(/g, '('],
    [/\\right\)/g, ')'],
    [/\\left\[/g, '['],
    [/\\right\]/g, ']'],
    [/\\{/g, '{'],
    [/\\}/g, '}'],
    [/\\,/g, ''],
    [/\\!/g, ''],
    [/\\;/g, ''],
    [/\\:/g, ''],
  ];

  for (const [pattern, replacement] of latexReplacements) {
    result = result.replace(pattern, replacement);
  }

  result = result
    .replace(/\$\$([\s\S]*?)\$\$/g, '$1')
    .replace(/\$([^$]*?)\$/g, '$1')
    .replace(/\\\(([\s\S]*?)\\\)/g, '$1')
    .replace(/\\\[([\s\S]*?)\\\]/g, '$1')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/\^([0-9]+)/g, '的$1次方')
    .replace(/\^\{([^}]*)\}/g, '的$1次方')
    .replace(/_([0-9a-zA-Z])/g, '下标$1')
    .replace(/_\{([^}]*)\}/g, '下标$1')
    .replace(/\\text\{([^}]*)\}/g, '$1')
    .replace(/\\mathrm\{([^}]*)\}/g, '$1')
    .replace(/\\mathbf\{([^}]*)\}/g, '$1')
    .replace(/\\[a-zA-Z]+/g, '')
    .replace(/[{}]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  return result;
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
