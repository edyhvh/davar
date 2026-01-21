import React from 'react';

interface StickyNoteProps {
  label: string;
  qumranWord: string;
  masoreticWord: string;
  color?: 'yellow' | 'pink' | 'green' | 'lime' | 'red' | 'teal';
  isFullChapter?: boolean;
  onQumranClick?: () => void;
  onMasoreticClick?: () => void;
}

export function StickyNote({ 
  label, 
  qumranWord, 
  masoreticWord, 
  color = 'yellow',
  isFullChapter = false,
  onQumranClick,
  onMasoreticClick,
}: StickyNoteProps) {
  // Size adjustments based on mode
  const fontSize = isFullChapter ? '20px' : '16px';
  const padding = isFullChapter ? '12px 16px' : '10px 14px';
  const labelSize = isFullChapter ? '11px' : '9px';
  const spacing = isFullChapter ? '6px' : '4px';

  return (
    <div className="inline-block relative" style={{ verticalAlign: 'middle' }}>
      {/* Tape effect at top - realistic masking tape */}
      <div 
        className="absolute -top-2 left-1/2 -translate-x-1/2"
        style={{
          width: '30px',
          height: '12px',
          backgroundColor: 'rgba(160, 160, 140, 0.7)',
          transform: 'translateX(-50%)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.15), inset 0 1px 2px rgba(255,255,255,0.3)',
          borderRadius: '1px',
        }}
      />
      
      {/* Sticky note body - warm yellow that works in both themes */}
      <div 
        className="relative shadow-lg"
        style={{
          backgroundColor: 'var(--copper-highlight)',
          padding: padding,
          borderRadius: '3px',
          transform: 'rotate(-1deg)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
        }}
      >
        {/* Label */}
        <div 
          className="uppercase tracking-wider mb-1"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: labelSize,
            fontWeight: 700,
            color: 'var(--foreground)',
            opacity: 0.9,
          }}
        >
          {label}
        </div>

        {/* Qumran variant word */}
        <div 
          className="font-semibold mb-1 cursor-pointer hover:opacity-80 transition-opacity"
          style={{
            fontFamily: "'Cardo', serif",
            fontSize: fontSize,
            direction: 'rtl',
            lineHeight: 1.4,
            color: 'var(--foreground)',
          }}
          onClick={onQumranClick}
        >
          {qumranWord}
        </div>

        {/* Divider line */}
        <div 
          className="my-1"
          style={{
            height: '1px',
            backgroundColor: 'var(--foreground)',
            opacity: 0.3,
            margin: `${spacing} 0`,
          }}
        />

        {/* Masoretic word (smaller, below) */}
        <div 
          className="text-xs cursor-pointer hover:opacity-80 transition-opacity"
          style={{
            fontFamily: "'Cardo', serif",
            fontSize: isFullChapter ? '14px' : '12px',
            direction: 'rtl',
            lineHeight: 1.3,
            color: 'var(--foreground)',
            opacity: 0.7,
          }}
          onClick={onMasoreticClick}
        >
          {masoreticWord}
        </div>
      </div>
    </div>
  );
}