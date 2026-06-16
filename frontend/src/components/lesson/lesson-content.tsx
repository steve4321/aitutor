'use client';

import type { LessonSection } from '@/types/course';
import {
  IntroductionCard,
  ConceptCard,
  ExampleCard,
  SummaryCard,
  ExpandableCard,
  TableCard,
  IllustrationCard,
  AudioBlockCard,
  ImageBlockCard,
  DividerCard,
  CodeBlockCard,
} from './sections/text-section';
import {
  FormulaCard,
  AnimationCard,
  GeoGebraCard,
} from './sections/math-section';
import {
  PracticeCard,
  VoiceInputCard,
} from './sections/interactive-section';

interface LessonContentProps {
  sections: LessonSection[];
  onAnswer?: (problemIndex: number, isCorrect: boolean, answer?: string, problemId?: string) => void;
  sessionId?: string | null;
  subject?: string;
}

export function LessonContent({ sections, onAnswer, sessionId, subject }: LessonContentProps) {
  return (
    <div className="space-y-4">
      {sections.map((section, idx) => {
        switch (section.type) {
          case 'introduction':
            return <IntroductionCard key={idx} content={section.content || ''} title={section.title} />;
          case 'concept':
          case 'text':
            return <ConceptCard key={idx} title={section.title || ''} content={section.content || ''} variant={section.variant} />;
          case 'example':
            return <ExampleCard key={idx} problem={section.problem || ''} solution={section.solution || ''} />;
          case 'practice':
            return <PracticeCard key={idx} problems={section.problems || []} onAnswer={onAnswer} />;
          case 'summary':
            return <SummaryCard key={idx} content={section.content || ''} />;
          case 'animation':
            return (
              <AnimationCard
                key={idx}
                title={section.title || ''}
                url={section.animationUrl}
                animationType={section.animationType}
                thumbnailUrl={section.thumbnailUrl}
                durationSec={section.durationSec}
                description={section.content}
              />
            );
          case 'formula':
            return <FormulaCard key={idx} title={section.title} latex={section.content || ''} note={section.note} />;
          case 'expandable':
            return <ExpandableCard key={idx} title={section.title || '展开查看'} content={section.content || ''} />;
          case 'interactive_table':
            return <TableCard key={idx} title={section.title} headers={section.tableHeaders || []} rows={section.tableRows || []} />;
          case 'voice_input':
            return <VoiceInputCard key={idx} prompt={section.voicePrompt || ''} sessionId={sessionId} subject={subject} />;
          case 'illustration':
            return <IllustrationCard key={idx} title={section.title} description={section.content || ''} />;
          case 'audio':
            return <AudioBlockCard key={idx} url={section.audioUrl || ''} duration={section.audioDuration} transcript={section.audioTranscript} label={section.audioLabel} autoplay={section.audioAutoplay} />;
          case 'image':
            return <ImageBlockCard key={idx} url={section.imageUrl || ''} alt={section.imageAlt || ''} caption={section.imageCaption} />;
          case 'geogebra':
            return <GeoGebraCard key={idx} materialId={section.geogebraMaterialId} instructions={section.geogebraInstructions || ''} width={section.geogebraWidth} height={section.geogebraHeight} />;
          case 'divider':
            return <DividerCard key={idx} variant={section.dividerVariant} label={section.dividerLabel} />;
          case 'code':
            return <CodeBlockCard key={idx} code={section.codeContent || ''} language={section.codeLanguage} title={section.title} />;
          default:
            return null;
        }
      })}
    </div>
  );
}
