/**
 * Text-based content blocks: paragraph, code, table, expandable, divider, illustration.
 */

import type { ContentBlock } from '../content-block';

export interface TextBlock {
  type: 'text';
  /** Markdown text (supports $...$ inline LaTeX) */
  content: string;
  /** Style variant */
  variant?: 'body' | 'caption' | 'quote' | 'callout' | 'note' | 'tip' | 'warning';
}

export interface ExpandableBlock {
  type: 'expandable';
  /** Collapsed title */
  title: string;
  /** Expanded content (recursive ContentBlock) */
  content: ContentBlock[];
  /** Default expanded state */
  default_expanded?: boolean;
}

export interface DividerBlock {
  type: 'divider';
  /** Style */
  variant?: 'line' | 'spacing' | 'dots' | 'label';
  /** Text for label variant */
  label?: string;
}

export interface IllustrationBlock {
  type: 'illustration';
  /** Title */
  title: string;
  /** Description */
  description?: string;
  /** Image */
  image: {
    url: string;
    alt: string;
  };
  /** Highlighted annotations on the image */
  annotations?: Array<{
    label: string;
    description: string;
    /** Relative position 0-1 */
    position: { x: number; y: number };
  }>;
}

export interface CodeBlock {
  type: 'code';
  /** Code content */
  code: string;
  /** Programming language */
  language?: string;
  /** Title */
  title?: string;
  /** Whether runnable (e.g. Python compute check) */
  runnable?: boolean;
}

export interface TableBlock {
  type: 'table';
  /** Column headers */
  headers: string[];
  /** Data rows */
  rows: Array<string[]>;
  /** Title */
  title?: string;
}
