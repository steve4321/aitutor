'use client';

import React from 'react';
import { KatexRenderer } from '@/components/math/katex-renderer';

/**
 * Render text with inline LaTeX ($...$), display LaTeX ($$...$$),
 * inline bold (**...**), inline italic (*...*), and inline code (`...`).
 */
export function renderWithLatex(text: string): React.ReactNode {
  if (!text) return null;

  const parts: React.ReactNode[] = [];

  // Order matters: $$ before $, ** before *
  const regex = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$|\*\*([^*]+?)\*\*|\*([^*]+?)\*|`([^`]+?)`/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    if (match[1] !== undefined) {
      // Display math $$...$$
      parts.push(<KatexRenderer key={`dm-${key++}`} latex={match[1]} displayMode />);
    } else if (match[2] !== undefined) {
      // Inline math $...$
      parts.push(<KatexRenderer key={`im-${key++}`} latex={match[2]} displayMode={false} />);
    } else if (match[3] !== undefined) {
      // Bold **...**
      parts.push(<strong key={`b-${key++}`}>{match[3]}</strong>);
    } else if (match[4] !== undefined) {
      // Italic *...*
      parts.push(<em key={`i-${key++}`}>{match[4]}</em>);
    } else if (match[5] !== undefined) {
      // Inline code `...`
      parts.push(
        <code key={`c-${key++}`} className="rounded bg-muted px-1 py-0.5 text-sm font-mono">
          {match[5]}
        </code>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length === 1 ? parts[0] : <>{parts}</>;
}

/**
 * Render multi-line Markdown text with LaTeX support.
 * Supports: # / ## / ### headers, > blockquotes, - / * lists,
 * | tables (skips separator rows), **bold lines**, and all inline formatting.
 */
export function renderMarkdownWithLatex(text: string): React.ReactNode {
  if (!text) return null;
  const lines = text.split('\n');
  return (
    <>
      {lines.map((line, li) => {
        const trimmed = line.trim();
        if (!trimmed) return <br key={li} />;
        if (trimmed.startsWith('# '))
          return <h1 key={li} className="text-2xl font-bold mt-4 mb-2">{renderWithLatex(trimmed.slice(2))}</h1>;
        if (trimmed.startsWith('## '))
          return <h2 key={li} className="text-xl font-bold mt-4 mb-2">{renderWithLatex(trimmed.slice(3))}</h2>;
        if (trimmed.startsWith('### '))
          return <h3 key={li} className="text-lg font-semibold mt-3 mb-1">{renderWithLatex(trimmed.slice(4))}</h3>;
        if (trimmed.startsWith('> '))
          return <blockquote key={li} className="border-l-4 border-blue-400 pl-3 my-2 text-muted-foreground italic">{renderWithLatex(trimmed.slice(2))}</blockquote>;
        if (trimmed.startsWith('- ') || trimmed.startsWith('• '))
          return <li key={li} className="ml-4">{renderWithLatex(trimmed.slice(2))}</li>;
        if (trimmed.startsWith('| ') && trimmed.endsWith('|')) {
          const cells = trimmed.split('|').filter(Boolean).map((c) => c.trim());
          if (cells.every((c) => /^[-:]+$/.test(c))) return null;
          return (
            <div key={li} className="flex gap-2 py-1 border-b border-border/30 text-sm">
              {cells.map((c, ci) => (
                <span key={ci} className="flex-1">{renderWithLatex(c)}</span>
              ))}
            </div>
          );
        }
        if (trimmed.startsWith('**') && trimmed.endsWith('**'))
          return <p key={li} className="font-bold mt-2">{renderWithLatex(trimmed.slice(2, -2))}</p>;
        return <p key={li} className="mb-1">{renderWithLatex(trimmed)}</p>;
      })}
    </>
  );
}
