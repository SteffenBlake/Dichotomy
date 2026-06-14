---
name: markdown-editting
description: Guide for any work in the content.md file, including our styling and how we format stuff
---

# Markdown Editing Guide

## Content Structure

Edit `content.md` to document your tabletop game:
- Use `#` for top-level sections (major game components)
- Use `##` for subsections (specific mechanics or rules)
- Use `###` for sub-subsections (detailed explanations)
- The table of contents will be automatically generated from these headers

### Example Structure

```markdown
# Game Overview

Introduction to the core concepts and theme of the game.

## Components

What you need to play the game.

### The Deck

Description of the card deck and its composition.

## How to Play

Core gameplay loop and turn structure.

### Setup

How to prepare the game for play.

### Turn Actions

What players can do on their turn.
```

## Writing Style Guidelines

1. **Professional Tone**: Always write content in a professional and polished manner
2. **Readability**: Focus on ease of readability and consistent terminology
3. **No Em Dashes**: Avoid using the "em dash" (—) anywhere on the site
4. **No Emoji**: Avoid use of emoji anywhere, it looks unprofessional

## Dicier Font Usage

We use the "Dicier" font pack to help generate screen reader friendly icons for things like dice and card suits for game rules.

### Syntax

Use the `{dicier:CODE}` syntax in your markdown, which will be converted to `<span class="dicier">CODE</span>` in the HTML output.

**Example:**
```markdown
# Game Title {dicier:JOKER}
```

This will display the title with a joker symbol that is screen-reader friendly.

For detailed information on available codes and proper usage, refer to the dicier-user-guide skill file.

## Rebuilding

After making changes to `content.md`, rebuild the site:
```bash
python build.py
```