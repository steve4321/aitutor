/**
 * Media content blocks: image, audio, video.
 */

export interface AudioBlock {
  type: 'audio';
  /** Audio URL (TTS-generated .mp3) */
  url: string;
  /** Duration in seconds */
  duration_sec: number;
  /** Corresponding text for synced highlighting */
  transcript?: string;
  /** Playback speed multiplier */
  speed?: 0.8 | 1.0 | 1.2;
  /** Player label */
  label?: string;
  /** Auto-play for narration */
  autoplay?: boolean;
}

export interface ImageBlock {
  type: 'image';
  /** Image URL */
  url: string;
  /** Alt text (accessibility) */
  alt: string;
  /** Caption */
  caption?: string;
  /** Max width in px (auto if unset) */
  max_width?: number;
}

export interface VideoBlock {
  type: 'video';
  /** Video URL (MP4 / HLS) */
  url: string;
  /** Thumbnail image */
  thumbnail_url?: string;
  /** Duration in seconds */
  duration_sec: number;
  /** Title */
  title?: string;
  /** Auto-play */
  autoplay?: boolean;
  /** E-ink fallback (keyframe screenshots + text summary) */
  eink_fallback?: {
    keyframes: Array<{
      image_url: string;
      caption: string;
    }>;
    text_summary: string;
  };
}
