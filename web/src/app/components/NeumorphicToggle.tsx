import React from 'react';

interface NeumorphicToggleProps {
  enabled: boolean;
  onToggle: () => void;
  size?: 'sm' | 'md';
  label?: string;
  ariaLabel: string;
  iconRenderer?: (enabled: boolean) => React.ReactNode;
}

const sizes = {
  sm: { outer: 32, inner: 12 },
  md: { outer: 40, inner: 16 },
};

export function NeumorphicToggle({
  enabled,
  onToggle,
  size = 'md',
  label,
  ariaLabel,
  iconRenderer,
}: NeumorphicToggleProps) {
  const { outer, inner } = sizes[size];

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={ariaLabel}
      className="flex flex-col items-center gap-2"
    >
      <span
        className={`relative flex items-center justify-center rounded-full transition-all duration-300 ${
          enabled
            ? 'shadow-[inset_4px_4px_8px_var(--neomorph-inset-shadow-dark),inset_-4px_-4px_8px_var(--neomorph-inset-shadow-light)]'
            : 'shadow-[-6px_-6px_12px_var(--neomorph-shadow-light),6px_6px_12px_var(--neomorph-shadow-dark)]'
        }`}
        style={{
          width: `${outer}px`,
          height: `${outer}px`,
          backgroundColor: 'var(--neomorph-bg)',
          border: '1px solid var(--neomorph-border)',
        }}
      >
        {iconRenderer ? (
          <span className="text-[var(--text-secondary)]">{iconRenderer(enabled)}</span>
        ) : (
          <span
            className={`rounded-full transition-all duration-300 ${
              enabled
                ? 'bg-[var(--accent)]'
                : 'bg-[var(--neomorph-bg)]'
            }`}
            style={{
              width: `${inner}px`,
              height: `${inner}px`,
              boxShadow: enabled
                ? '0 0 12px rgba(0, 0, 0, 0.12)'
                : 'inset 2px 2px 4px var(--neomorph-inset-shadow-dark), inset -2px -2px 4px var(--neomorph-inset-shadow-light)',
            }}
          />
        )}
      </span>
      {label && (
        <span
          className="text-[10px] uppercase tracking-[0.3em] text-[var(--text-secondary)]"
          style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
        >
          {label}
        </span>
      )}
    </button>
  );
}
