---
description: Core rules, architecture, and guidelines for the Davar project - Minimalist Hebrew Bible Study App
---

# Davar Project - דבר - Minimalist Bible Study App for Hebrew Scriptures

Davar (דבר - "word") is a sacred, distraction-free digital tool for deep, contemplative engagement with Hebrew Scriptures (Tanakh + Besorah), including Qumran textual variants and a custom dictionary system.

## Project Overview

- Multi-language support: Hebrew (RTL priority), Spanish, English (future: Portuguese, native Hebrew dictionary, Arabic, Farsi)

## Architecture Guidelines

### Tech Stack

- Frontend: React Native + Expo
- Backend: FastAPI + PostgreSQL
- Offline support: via FastAPI

### Public vs Private Branches

- Public branch: Code + mock data only
- Private branch: Real ISR datasets, licensed fonts, translations

## Critical Reminders

### NEVER:

- Modify licensed content files
- Remove required attributions
- Break the one-verse-per-screen constraint
- Commit sensitive data to public branches

### ALWAYS:

- Prioritize contemplative UX over feature complexity
- Maintain neumorphism design language
- Ensure full RTL compatibility for Hebrew text
- Test offline functionality thoroughly
- Respect all content licensing restrictions
- Write all code, comments, and documentation **only in English**

This project is a sacred tool for profound connection with Hebrew Scriptures — balance technical excellence with spiritual sensitivity.
