---
description: Core rules, architecture, and guidelines for the Davar project - Minimalist Hebrew Bible Study App
---

# Davar Project - דבר - Minimalist Bible Study App for Hebrew Scriptures

Davar (דבר - "word") is a sacred, distraction-free digital tool for deep, contemplative engagement with Hebrew Scriptures (Tanakh + Besorah), including Qumran textual variants and a custom dictionary system.

## Project Overview

- Multi-language support: Hebrew (RTL priority), Spanish, English (future: Portuguese, native Hebrew dictionary, Arabic, Farsi)

## Architecture Guidelines

### Tech Stack

- Frontend: React Native + Expo (mobile), Bun + React (web)
- Data delivery: Static JSON on Cloudflare Pages + Supabase Storage for TS2009
- Offline support: Mobile SQLite with static bundle sync
- Build: Bun as JavaScript runtime and package manager

### Public vs Private Branches

- Public branch: Code + mock data only
- Private branch: Real ISR datasets, licensed fonts, translations

## Critical Reminders

### NEVER:

- Modify licensed content files
- Remove required attributions
- Commit sensitive data to public branches

### ALWAYS:

- Prioritize contemplative UX over feature complexity
- Maintain neumorphism design language
- Ensure full RTL compatibility for Hebrew text
- Test offline functionality thoroughly
- Respect all content licensing restrictions
- Write all code, comments, and documentation **only in English**

## Assistant Communication Preference

- Do not show code diffs in chat by default.
- Summarize what changed and list affected files.
- Show full diff output only when explicitly requested.

This project is a sacred tool for profound connection with Hebrew Scriptures — balance technical excellence with spiritual sensitivity.
