import React, { useState } from 'react';

const CopyIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 512 512"
    fill="none"
    stroke="currentColor"
    strokeWidth="32"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="128" y="128" width="336" height="336" rx="57" ry="57" />
    <path d="M383.5 128l.5-24a56.16 56.16 0 00-56-56H112a64.19 64.19 0 00-64 64v216a56.16 56.16 0 0056 56h24" />
  </svg>
);

const CheckmarkIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 512 512"
    fill="none"
    stroke="currentColor"
    strokeWidth="32"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="416 128 192 384 96 288" />
  </svg>
);

interface CopyableWalletProps {
  icon: React.ReactNode;
  name: string;
  address: string;
}

export function CopyableWallet({ icon, name, address }: CopyableWalletProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(address);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = address;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
          const successful = document.execCommand('copy');
          if (!successful) throw new Error('Copy failed');
        } finally {
          document.body.removeChild(textArea);
        }
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy address:', error);
      const range = document.createRange();
      const selection = window.getSelection();
      const textNode = document.createTextNode(address);
      document.body.appendChild(textNode);
      range.selectNodeContents(textNode);
      selection?.removeAllRanges();
      selection?.addRange(range);
      document.body.removeChild(textNode);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-center gap-2 sm:gap-3 text-lg group max-w-full">
      <div className="flex items-center justify-center gap-2 sm:gap-3">
        {icon}
        <span className="font-medium text-[var(--text-secondary)] text-center sm:text-left">
          {name}
        </span>
      </div>
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer touch-manipulation min-h-[44px] px-2 py-1 rounded"
        title={`Copy ${name} address`}
      >
        <span className="font-mono text-sm text-[var(--text-secondary)] break-all sm:break-normal truncate max-w-[220px] sm:max-w-none">
          {address}
        </span>
        {copied ? (
          <CheckmarkIcon className="w-4 h-4 text-green-600 flex-shrink-0" />
        ) : (
          <CopyIcon className="w-4 h-4 text-[var(--text-secondary)] opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity flex-shrink-0" />
        )}
      </button>
    </div>
  );
}
