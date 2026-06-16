/**
 * Math-specific content blocks: formula (KaTeX), GeoGebra, animation.
 */

export interface FormulaBlock {
  type: 'formula';
  /** LaTeX expression */
  latex: string;
  /** Formula title / name */
  title?: string;
  /** Color annotations e.g. { "a_b": "#4A90D9" } */
  color_coding?: Record<string, string>;
  /** Explanatory note */
  note?: string;
  /** Display mode */
  display?: 'inline' | 'block' | 'card';
}

export interface GeoGebraBlock {
  type: 'geogebra';
  /** GeoGebra material / applet ID */
  material_id?: string;
  /** Custom GeoGebra XML config */
  applet_config?: string;
  /** User instructions */
  instructions: string;
  /** Width */
  width?: number;
  /** Height */
  height?: number;
  /** E-ink fallback (static step screenshots) */
  eink_fallback?: {
    steps: Array<{
      image_url: string;
      caption: string;
      insight?: string;
    }>;
    fallback_note?: string;
  };
}

export interface AnimationBlock {
  type: 'animation';
  /** Animation engine */
  animation_type: 'manim' | 'lottie' | 'css' | 'canvas';
  /** Animation resource URL (MP4 / JSON / none) */
  url?: string;
  /** Title */
  title: string;
  /** Duration in seconds */
  duration_sec?: number;
  /** Thumbnail */
  thumbnail_url?: string;
  /** Inline config for CSS/Canvas animations */
  inline_config?: Record<string, unknown>;
  /** E-ink fallback (keyframe screenshots) */
  eink_fallback?: {
    keyframes: Array<{
      image_url: string;
      caption: string;
    }>;
  };
}
