'use client';

import { cn } from '@/lib/utils';

interface GeoGebraEmbedProps {
  appletId?: string;
  materialId?: string;
  width?: number;
  height?: number;
  className?: string;
}

export function GeoGebraEmbed({
  materialId = 'w9e6uasd',
  width = 600,
  height = 400,
  className,
}: GeoGebraEmbedProps) {
  const embedUrl = `https://www.geogebra.org/material/iframe/id/${materialId}/width/${width}/height/${height}`;

  return (
    <div className={cn('overflow-hidden rounded-xl border border-gray-200', className)}>
      <iframe
        src={embedUrl}
        width={width}
        height={height}
        className="w-full border-0"
        allowFullScreen
        title="GeoGebra Interactive Widget"
      />
    </div>
  );
}
