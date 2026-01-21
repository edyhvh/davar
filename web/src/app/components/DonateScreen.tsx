import React from 'react';
import { CopyableWallet } from './CopyableWallet';

const DONATION_CONFIG = {
  wallets: {
    ethereum: '0x8B190393c13458A16c93c121983cefc74b6fC92e',
    bitcoin: 'bc1qe9z8d5ll8724qlhl3lvumh9z06x4km575luj38',
    solana: 'FZh8zAUrG78ZuK2oFbyJu8Ss56yqzisqQJt5ZoqomQtN',
  },
  githubSponsor: 'https://github.com/sponsors/edyhvh',
} as const;

const EthereumIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 320 512" fill="currentColor">
    <path d="M311.9 260.8L160 353.6 8 260.8 160 0l151.9 260.8zM160 383.4L8 290.6 160 512l152-221.4-152 92.8z" />
  </svg>
);

const BitcoinIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 512 512" fill="currentColor">
    <path d="M504 256c0 136.967-111.033 248-248 248S8 392.967 8 256 119.033 8 256 8s248 111.033 248 248zm-141.651-35.33c4.937-32.999-20.191-50.739-54.55-62.573l11.146-44.702-27.213-6.781-10.851 43.524c-7.154-1.783-14.502-3.464-21.803-5.13l10.929-43.81-27.198-6.781-11.153 44.686c-5.922-1.349-11.735-2.682-17.377-4.084l.031-.14-37.53-9.37-7.239 29.062s20.191 4.627 19.765 4.913c11.022 2.75 13.007 10.056 12.675 15.846l-12.7 50.864c.759.194 1.744.473 2.825.905l-2.873-.716-17.8 71.333c-1.352 3.352-4.785 8.373-12.53 6.465.272.396-19.765-4.913-19.765-4.913l-13.5 31.097 35.417 8.833c6.586 1.647 13.034 3.37 19.398 5.002l-11.26 45.132 27.198 6.781 11.153-44.732c7.421 2.016 14.63 3.879 21.678 5.635l-11.113 44.508 27.213 6.781 11.26-45.07c46.38 8.79 81.26 5.247 95.956-36.727 11.826-33.95-.588-53.53-25.0-66.148 17.777-4.106 31.199-15.82 34.744-39.995zm-62.161 87.159c-8.401 33.95-65.826 15.606-84.388 10.999l14.93-59.792c18.562 4.632 78.098 13.812 69.458 48.793zm8.402-87.646c-7.674 30.862-55.225 15.178-70.739 11.324l13.532-54.432c15.513 3.854 65.436 11.083 57.207 43.108z" />
  </svg>
);

const SolanaIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 397.7 311.7" fill="currentColor">
    <path d="M64.6 237.9c2.4-2.4 5.7-3.8 9.2-3.8h317.4c5.8 0 8.7 7 4.6 11.1l-62.7 62.7c-2.4 2.4-5.7 3.8-9.2 3.8H6.5c-5.8 0-8.7-7-4.6-11.1l62.7-62.7z" />
    <path d="M64.6 120.1c2.4-2.4 5.7-3.8 9.2-3.8h317.4c5.8 0 8.7 7 4.6 11.1l-62.7 62.7c-2.4 2.4-5.7 3.8-9.2 3.8H6.5c-5.8 0-8.7-7-4.6-11.1l62.7-62.7z" />
    <path d="M64.6 3.8C67.1 1.4 70.4 0 73.8 0h317.4c5.8 0 8.7 7 4.6 11.1l-62.7 62.7c-2.4 2.4-5.7 3.8-9.2 3.8H6.5c-5.8 0-8.7-7-4.6-11.1L64.6 3.8z" />
  </svg>
);

const TetherIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 339.43 295.27">
    <path
      fill="currentColor"
      d="M191.19,144.8v0c-1.2.09-7.4.46-21.23.46-11,0-18.81-.33-21.55-.46v0c-42.51-1.87-74.24-9.27-74.24-18.13s31.73-16.25,74.24-18.15v28.91c2.78.19,10.93.67,21.74.67,13,0,19.82-.56,21-.66v-28.9c42.42,1.89,74.08,9.29,74.08,18.13s-31.65,16.24-74.08,18.12h0Zm0-39.25V79.68h59.2V40.23H89.21V79.68h59.2v25.86c-48.2,2.21-84.47,11.42-84.47,22.5s36.27,20.29,84.47,22.5v69.56h42.78V150.54c48.09-2.21,84.36-11.42,84.36-22.5s-36.27-20.29-84.36-22.5Z"
    />
    <path
      className="crypto-icon-internal usdt-internal"
      fill="#fff"
      d="M191.19,156.89c-1.11.08-7,.46-21.23.46-11,0-18.81-.33-21.55-.46v0c-42.51-1.87-74.24-9.27-74.24-18.13s31.73-16.25,74.24-18.15v28.91c2.78.19,10.93.67,21.74.67,13,0,19.82-.56,21-.66v-28.9c42.42,1.89,74.08,9.29,74.08,18.13s-31.65,16.24-74.08,18.12h0Zm0-39.25V91.77h59.2V52.32H89.21V91.77h59.2v25.86c-48.2,2.21-84.47,11.42-84.47,22.5s36.27,20.29,84.47,22.5v69.56h42.78V162.64c48.09-2.21,84.36-11.42,84.36-22.5s-36.27-20.29-84.36-22.5Z"
    />
  </svg>
);

const USDCIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 2000 2000">
    <path
      fill="currentColor"
      d="M1000 2000c554.17 0 1000-445.83 1000-1000S1554.17 0 1000 0 0 445.83 0 1000s445.83 1000 1000 1000z"
    />
    <path
      className="crypto-icon-internal usdc-internal"
      fill="#fff"
      d="M787.5 1595.83c-325-116.66-491.67-479.16-370.83-800 62.5-166.67 191.66-295.84 358.33-358.34 16.67-8.33 25-20.83 25-41.66v-58.34c0-16.66-8.33-29.16-25-33.33-4.17 0-12.5 0-16.67 4.17-395.83 125-612.5 545.83-487.5 941.66 75 233.34 254.17 412.5 487.5 487.5 16.67 8.34 33.34 0 37.5-16.66 4.17-4.17 4.17-8.34 4.17-16.67v-58.33c0-12.5-12.5-29.17-37.5-37.5zm479.16-1208.33c-16.66-8.33-25-20.83-25-41.66v-58.34c0-16.66 8.34-29.16 25-33.33 4.17 0 12.5 0 16.67 4.17 395.83 125 612.5 545.83 487.5 941.66-75 233.34-254.17 412.5-487.5 487.5-16.67 8.34-33.34 0-37.5-16.66-4.17-4.17-4.17-8.34-4.17-16.67v-58.33c0-12.5 12.5-29.17 37.5-37.5 325-116.66 491.67-479.16 370.83-800-62.5-166.67-191.66-295.84-358.33-358.34z"
    />
    <path
      className="crypto-icon-internal usdc-internal"
      fill="#fff"
      d="M1245.83 1058.33c0-145.83-87.5-195.83-262.5-216.66-125-16.67-150-50-150-108.34s41.67-95.83 125-95.83c75 0 116.67 25 137.5 87.5 4.17 12.5 16.67 20.83 29.17 20.83h66.66c16.67 0 29.17-12.5 29.17-29.16v-4.17c-16.67-91.67-91.67-162.5-187.5-170.83v-100c0-16.67-12.5-29.17-33.33-33.34h-62.5c-16.67 0-29.17 12.5-33.34 33.34v95.83c-125 16.67-216.67 91.67-216.67 204.17 0 154.17 120.83 195.83 262.5 216.67 137.5 20.83 162.5 58.33 162.5 112.5 0 83.33-66.67 108.33-141.67 108.33-108.33 0-150-45.83-166.67-108.33-4.17-16.67-16.67-25-33.33-25h-66.67c-16.67 0-29.16 12.5-29.16 29.17v4.16c16.66 116.67 100 179.17 229.16 195.83v100c0 16.67 12.5 29.17 33.34 33.34h62.5c16.66 0 33.33-16.67 33.33-33.34v-95.83c141.67-20.83 229.17-112.5 229.17-212.5z"
    />
  </svg>
);

const GithubSponsorsIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.5-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
    />
  </svg>
);

const CreditCardIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v1h14V4a1 1 0 0 0-1-1H2zm13 4H1v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7z" />
  </svg>
);

export function DonateScreen() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="space-y-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          <CopyableWallet
            icon={
              <div className="flex items-center gap-1">
                <EthereumIcon className="w-6 h-6" />
                <TetherIcon className="w-5 h-5" />
                <USDCIcon className="w-5 h-5" />
              </div>
            }
            name="Ethereum"
            address={DONATION_CONFIG.wallets.ethereum}
          />

          <CopyableWallet
            icon={<BitcoinIcon className="w-6 h-6" />}
            name="Bitcoin"
            address={DONATION_CONFIG.wallets.bitcoin}
          />

          <CopyableWallet
            icon={
              <div className="flex items-center gap-1">
                <SolanaIcon className="w-6 h-6" />
                <TetherIcon className="w-5 h-5" />
                <USDCIcon className="w-5 h-5" />
              </div>
            }
            name="Solana"
            address={DONATION_CONFIG.wallets.solana}
          />

          <div className="flex items-center justify-center gap-3 text-base">
            <div className="flex items-center gap-1">
              <GithubSponsorsIcon className="w-6 h-6" />
              <CreditCardIcon className="w-5 h-5" />
            </div>
            <span className="font-medium">Github Sponsor</span>
            <a
              href={DONATION_CONFIG.githubSponsor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline underline-offset-2 transition-colors"
            >
              @edyhvh
            </a>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 pt-6">
            <a
              href="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Download on the App Store"
            >
              <img
                src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
                alt="Download on the App Store"
                className="h-12"
              />
            </a>
            <a
              href="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Get it on Google Play"
            >
              <img
                src="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
                alt="Get it on Google Play"
                className="h-14"
              />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
