import React from "react";
import { Github, Lightbulb, Mail } from "lucide-react";

const proposalItems = [
  "telegram app",
  "blockchain integration",
  "arabic",
  "farsi",
  "japanese",
  "portuguese",
  "search anything (latin characters or hebrew)",
  "septuagint",
  "greek εὐαγγέλιον",
];

export function FeaturesScreen() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-sm tracking-[0.3em] uppercase text-[var(--copper-highlight)] mb-6">
          Proposal
        </div>
        <div className="space-y-3">
          {proposalItems.map((item) => (
            <div
              key={item}
              className="flex items-center justify-center gap-2 text-sm text-[var(--text-primary)]"
            >
              <Lightbulb className="w-4 h-4 text-[var(--copper-highlight)]" />
              <span style={{ fontFamily: "'Inter', sans-serif" }}>{item}</span>
            </div>
          ))}
        </div>
        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-[var(--text-secondary)]">
          <Github className="w-4 h-4" />
          <a
            href="https://github.com/edyhvh/davar"
            target="_blank"
            rel="noopener noreferrer"
            className="underline underline-offset-2 hover:text-[var(--text-primary)]"
          >
            davar
          </a>
          <span>
            this is an open source project, contribute and collaborate with your
            skills or ideas
          </span>
        </div>
        <div className="mt-3 flex items-center justify-center gap-2 text-sm text-[var(--text-secondary)]">
          <Mail className="w-4 h-4" />
          <a
            href="mailto:contact@davar.bible"
            className="underline underline-offset-2 hover:text-[var(--text-primary)]"
          >
            contact@davar.bible
          </a>
        </div>
      </div>
    </div>
  );
}
