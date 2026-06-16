/**
 * Web Speech API (SpeechRecognition) type declarations.
 *
 * The Web Speech API is not part of the standard TypeScript DOM lib,
 * so we declare the types here as ambient global declarations.
 *
 * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
 */

/** A single alternative transcription for a recognized phrase */
interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

/** A single recognition result, containing one or more alternatives */
interface SpeechRecognitionResult {
  readonly length: number;
  readonly isFinal: boolean;
  readonly [index: number]: SpeechRecognitionAlternative;
}

/** A collection of SpeechRecognitionResult objects */
interface SpeechRecognitionResultList {
  readonly length: number;
  readonly [index: number]: SpeechRecognitionResult;
}

/** Event fired when speech recognition produces results */
interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

/** Event fired when a speech recognition error occurs */
interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

/** The main SpeechRecognition interface */
interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  onaudiostart: (() => void) | null;
  onaudioend: (() => void) | null;
  onspeechstart: (() => void) | null;
  onspeechend: (() => void) | null;
  onnomatch: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

/** Constructor signature for creating SpeechRecognition instances */
interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
  readonly prototype: SpeechRecognition;
}

/**
 * Augment Window to include the standard and vendor-prefixed
 * SpeechRecognition constructors (Chrome exposes webkitSpeechRecognition).
 */
interface Window {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
}
