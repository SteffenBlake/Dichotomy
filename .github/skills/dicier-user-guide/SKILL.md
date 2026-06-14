---
name: dicier-user-guide
description: the user guide for Dicier, an advanced and accessible analog games typeface. Use this for any work in the markdown files that will require dicier markdown, or, any python work on parsing/outputing the dicier font
---

=====SECTION 0: README.

------------------------------
-----0 1: The License.

----------
---0 1 1: Cliff notes version
	• Dicier’s available under the CC BY 4.0 license, so:
	• You can freely use it, even in commercial products...
	• ...as long as you credit Speak the Sky as its designer.
Within reason, I mean. If you’re making e.g. a business card game then don’t worry about the credit. Here’s how credit could look:
Dicier, by Speak the Sky, licensed under CC BY 4.0.

If you’re doing anything complicated (like editing the font files) then check out sections 0 1 3 and 0 1 4.

This license only applies to fonts within the family ‘Dicier’. Other versions, such as commissions in the family DicierX, have their own, individual licenses (and are generally not available to the public).


----------
---0 1 2: Creative Commons Attribution 4.0.

Dicier is available under the Creative Commons Attribution 4.0 International license, or CC BY 4.0. The rest of section 0 1 explains the license terms, though you can find the simple and full license terms at the following url: https://creativecommons.org/licenses/by/4.0/ .


----------
---0 1 3: What you can do with Dicier.

As long as you follow the license conditions in section 0 1 4:
	1. You can freely copy and redistribute Dicier in any medium for personal and commercial projects, and
	2. you can freely remix, transform, and build on Dicier for personal and commercial projects.

Personal and commercial projects include, but are not limited to:
	• Embedding part or all of Dicier into a .pdf (most apps that can export .pdfs will embed fonts automatically).
	• Including Dicier in a .epub or .mobi e-book, or website.
	• Modifying Dicier’s font files directly using a typeface design app.
	• Bundling Dicier’s license (“Dicier license.txt”) and any of its font files with a template (e.g. the Mini-zine (https://speakthesky.itch.io/mini-zine-template-pack) or Trifold (https://speakthesky.itch.io/trifold-template-pack) Template Packs by Speak the Sky). You could also give a url to download Dicier rather than bundling the files with your templates (so you won’t have to update your templates with Dicier updates).


----------
---0 1 4: What you have to do to use Dicier.

	1. You must give appropriate credit, by providing:
		• the designer’s name (Speak the Sky),
		• the license type (CC BY 4.0) and a link to its text (https://creativecommons.org/licenses/by/4.0/), and
		• optionally (but preferably), a link to the typeface (https://speakthesky.itch.io/typeface-dicier).
	2. You must indicate what changes were made, if any, and keep a record of previous changes.
	3. You may not apply any legal terms or technological measures to restrict others from doing anything the license permits.
	4. You may not suggest that the licensor endorses you or your use of the licensed work.

Example 1: You modify the font files, then pass them on to a third party who also modifies them. You must keep a record of the modifications you make, then pass on the record to the third party. The third party must add their own modifications to the record as well, then pass the expanded record on with the files if they transfer them to another party.

Example 2: You use Dicier when laying out a game. You must include appropriate credit in the credits section (within reason for the game’s size, e.g. I’m not bothered if you don’t add a credit on a business card game). For example:
Dicier (https://speakthesky.itch.io/typeface-dicier), by Speak the Sky, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).


------------------------------
-----0 2: Troubleshooting Dicier

----------
---0 2 1: Codes not working in MS Office.

If you’re using Microsoft Office apps like MS Word or Powerpoint and the only codes that work for you are pipped dice, try going to the ‘Advanced’ font features tab mentioned in SECTION 4 2 3: ...IN MS OFFICE and activating ‘standard ligatures’ and ‘contextual alternates’. These settings should be on by default, but are off in MS Office.


----------
---0 2 2: Translated wildcard die or joker fails.

For currently-unknown reasons, some translated wildcard dice results (e.g. D6_TOUT, D8_ALGUNO) don’t combine correctly in exported .pdf files in some cases. This affects French, Spanish, Galician, and Portuguese (which have die first, wildcard second). It may only occur in Affinity Publisher (the software used to lay out this file) or even in the specific .afpub file for the guide.

This problem affects the following codes:
D2_TOUT, D4_TOUT, D6_TOUT, etc.
D2_ALGUNO, D4_ALGUNO, D6_ALGUNO, etc.
D2_ALGUN, D4_ALGUN, D6_ALGUN, etc.
D2_ALGÚN, D4_ALGÚN, D6_ALGÚN, etc.
D2_ALGUMA, D4_ALGUMA, D6_ALGUMA, etc.

It has also been seen to affect some Portuguese coloured joker codes:
JOKER_VERMELHO.
JOKER_NEGRO.

The temporary fix is to include any affected codes earlier in the file, which causes the icons to display correctly throughout the file.


------------------------------
-----0 3: Credits.

----------
---0 3 1: Typeface design.

Dicier is designed by Speak the Sky and was made using the Glyphs app.


----------
---0 3 2: Translation credits.

French by themoonisacheese, Acccent, and angela quidam.
Spanish by gabichete.
Galician by gabichete.
Croatian (standard) by Ordoalea Publishing.
Portuguese (Brazilian) by Leonardo Andrade (additional notes for Portuguese (European) by hobbito do Shire).
German by Florik (additional notes by unique_uu).


=============================
=====SECTION 1: INTRODUCTION.

------------------------------
-----1 1: What is Dicier?

----------
---1 1 1: Dicier is an analog game typeface!

It's designed for putting icons for analog game tools (like dice and playing cards) in-line with text, in tables, and in lists—and, really, in any other way you want. It converts regular text into useful icons, while keeping the text underneath, similarly to alt-text.


----------
---1 1 2: Dicier is open to your feedback!

Check out Dicier’s itch forum (https://speakthesky.itch.io/typeface-dicier/community), particularly:
	• the Issues & Fixes thread (for reporting bugs),
	• the Translating Dicier thread (for translating codes out of English), and
	• the Request a Feature thread.


------------------------------
-----1 2: About this Guide.

----------
---1 2 1: Terms: glyphs, icons, and codes.

You’ll see the word ‘glyph’ sometimes in this guide. In typefaces, a glyph is more-or-less any character aside from empty spaces. The letter ‘A’, the number ‘1’, and the period after this sentence are glyphs. So’s everything in this guide. Everything you can type with Dicier is a glyph, except the spaces.

You’ll also see the word ‘icon’ as well. In this guide, icons are Dicier’s output—glyphs for dice etc. Not all of Dicier’s glyphs are icons—only those meant to be used in analog games texts.

You’ll see the word ‘code’, too. These are numbers, words, and phrases you can use to turn Dicier’s non-icon glyphs into icons.

This guide has a lot of ‘glyph lists’ that list glyphs with their numbers, letters, or codes beneath. For example:

Icon: die with the words 'Yes, and'.
Code: Y E S underscore A N D.





==============================
=====SECTION 2: HOW TO USE DICIER.

------------------------------
-----2 2: Building Blocks

----------
---2 2 1: The alphabet and the underscore.

Dicier includes uppercase Latin letters (A to Z and others) and the underscore. These appear as a guide when you type out Dicier's codes. New letters (and even entire scripts) will be added to support new translations.

Letters currently in Dicier: A, Á (A-acute), Ã (A-tilde), B, C, Ç (C cedilla), Ć (C-acute), Č (C-caron), D, E, È (E-grave), É (E-acute), Ê (E-circumflex), F, G, H, I, Í (I-acute), J, K, L, M, N, Ñ (N-tilde), O, Ó (O-acute), Œ (O E ligature), P, Q, R, S, Š (S-caron), T, U, Ú (U-acute), V, W, X, Y, Z, Ž (Z-caron).

Dicier currently includes Hebrew letters as alternative codes for some dreidel icons.


------------------------------
-----2 3: Building Dicier’s Codes.

----------
---2 3 1: Simple codes.

The simplest codes in Dicier are just one number: the numbers 1 to 9 and 0 (made using the numeral keys) (excluding dreidel letter codes). These produce a die face with the corresponding number of pips.

Because the underlying text is ordinary numerals, the numbered dice icons can easily be used in custom numbered lists, including in multi-layered lists.


----------
---2 3 2: Complex codes.

All the remaining codes in Dicier use more than one character—but they all describe their icons fairly well. For example:

Icon: die with the word 'No'.
Code: N O. NO.

Icon: domino with 1 pip on left and 7 pips on right.
Code: 1 underscore 7. 1_7.

Icon: coin showing heads.
Code: H E A D S. HEADS.

Icon: uppercase Q and diamonds suit symbol.
Code: Q U E E N underscore D I A M O N D S. QUEEN_DIAMONDS.

As you type a code, you’ll see the guide letters appear one by one until the code is complete and the font swaps them out for the icon.

Note: If you're using MS Office, see SECTION 4 2 3: ...IN MS OFFICE and activate 'standard ligatures' and 'contextual alternates' to enable Dicier's basic functions.

Some codes use characters found in other, shorter codes, e.g. dominoes (e.g. 3 underscore 4) use the same characters as numbered dice (e.g. 3, 4). As you type out a code, you may see icons of shorter code(s) appear and be over-written.

You could also type out the codes in another font, then change to Dicier to transform them into their icons. How you get from codes to icons is up to you!


----------
---2 3 3: Idiosyncracies of Dicier's codes.

Underscores are mostly used as spaces, but very occasionally they distinguish codes that are otherwise identical, or one letter long (excluding dreidel letter codes). For example:

Icon: die with the word 'mais', French for 'but'.
Code: M A I S. MAIS.

Icon: die with plus sign.
Code: M A I S underscore. MAIS_. (note: this is technically the incorrect spelling, see next table).

Icon: die with the word 'y', Spanish for 'and'.
Code: Y underscore. Y_.

Icon: die with the word 'e', Galician for 'and'.
Code: E underscore. E_.

Dicier includes diacritics, and any code with diacritics has a version without them. For example:

Icon: die with plus sign.
Code 1: M A-acute I S. MÁIS.
Code 2: M A I S underscore. MAIS_. (see note in table above).

Icon: circled star.
Code 1: C O M O D I-acute N. COMODÍN.
Code 2: C O M O D I N. COMODIN.

Icon: clubs suit symbol.
Code 1: T R E-grave F L E. TRÈFLE.
Code 2: T R E F L E. TREFLE.

Icon: die with the word 'sí'.
Code 1: S I-acute. SÍ.
Code 2: S I underscore. SI_.

For technical reasons relating to .pdf export from at least one popular layout app, all codes are 8 or fewer characters. Codes longer than 8 characters are combinations of shorter codes, and a few codes are cut short. For example:

Icon: uppercase A and spades suit symbol.
Code: A C E underscore S P A D E S. ACE_SPADES.
Part 1: A C E underscore. ACE_.
Part 2: S P A D E S. SPADES.

Icon: die with hatching (dense diagonal lines).
Code: A N Y underscore O N underscore D 6. ANY_ON_D6.
Part 1: A N Y underscore O N underscore. ANY_ON_.
Part 2: D 6. D6.

Icon: circled pentacle.
Code: P E N T A C L E. PENTACLE.
Note: for pentacles.


------------------------------
-----2 4: Accessibility.

----------
---2 4 1: Using Dicier in an accessible way.

Dicier is designed to be accessible to both creators of analog games and users of text-to-speech software. However, as a creator, you have to use it accessibly as well.

Always put a space between Dicier codes. This helps text-to-speech (TTS) software read the icons. For example, S I X A C E A N Y T E N 6 3 will produce sight-readable icons for a card six, a card ace, a wildcard die, a card ten, a six-pip die, and a 3-pip die, but the text is “SIXACEANYTEN63”. TTS software may read that as something like “six ass anyton sixty-three”.

Putting punctuation between icons may not help. For example, putting a period between two numbered dice can make TTS software read it as a decimal. Slashes, dashes, and colons may be ignored, treated as pauses, or read aloud.

.pdf isn’t a very TTS-friendly format. It hasn’t fully outgrown its origin as a way to share visual info, so .pdf readers may not recognise spaces (because visually, there’s no difference between a space character and a gap), or underscores (for some reason). This is a problem with .pdf and .pdf readers, not Dicier, but you should be aware of this issue in general.


------------------------------
-----2 5: Customising Dicier.

----------
---2 5 1: Modes.

Dicier has 4 visual Modes that can be selected as font traits in a similar way to bold or italic:
	• Round, which has rounded corners and stroke caps.
	• Flat, which is square corners and stroke caps.
	• Pixel, which has low-resolution pixel icons, but has fewer features due to its low resolution. For a full list, see SECTION 4 4: LIMITED FEATURES IN DICIER PIXEL.
	• Block, which has a grid-like octagonal shape.


----------
---2 5 2: Weights.

Dicier has 3 visual Weights that can be selected as font traits in a similar way to bold or italic:
	• Light, which has thin strokes in some icons.
	• Heavy, which has thick strokes in some icons.
	• Dark, which inverts the colour (e.g. die faces are filled in, and pips are clear) and mixes stroke widths from Light and Heavy.

The specific strokes affected are:
	• outlines for dice, dominoes, suits, dreidels, and coins.
	• hatching in wildcard dice, dominoes, and coins.
	• Heckadeck arrows and talismans.
	• Chinese domino pips and pip patterns.•	
	• rock-paper-scissors symbols and gestures.

You can use different Weights to, for example:
	• distinguish between different types of dice (e.g. first and second dice in a d66 roll);
	• match the weight to your body text font’s weight; or
	• represent red vs black playing card suits.

You can use these to, for example, distinguish between different types of dice (e.g. first and second dice in a d66 roll) or match the thickness of the outline to the weight of your body font.


------------------------------
-----2 6: Dicier Webfonts.

----------
---2 6 1: Files.

Dicier includes webfont (.woff and .woff2) files for reduced file-sizes when using Dicier online or in .epub files. These files are approximately 60% smaller than the full .otf files.


----------
---2 6 2: CSS for Dicier.

First, target your chosen files with @font-face, then activate the following features in your text style: kern (k e r n), liga (l i g a), calt (c a l t). These may be active by default in your browser. For any text using double-digit dice codes (e.g. 13 on a d20), activate dlig (d l i g). Finally, check Chapter 4: Advanced Features for the 4-character names of extra features (e.g. ss01, cv26, zero). Your style code should look something like this:

@font-face {
font-family: Dicier;
src: url('/Fonts/Dicier-Round-Heavy.woff2');
}

.dicier {
font-family: Dicier, sans-serif;
font-feature-settings: “liga” 1, “kern” 1, “calt” 1;
}

This lets your styles use the selected Dicier font (here, Round-Heavy), then defines a class, 'dicier', that uses Round-Heavy with the basic features activated. If Dicier fails to load, the browser will display the underlying Dicier code in a sans-serif font.

For further information, search online for tutorials on CSS in general and @font-face and font settings in particular.




==============================
=====SECTION 3: CODES.

------------------------------
-----3 1: Dice.
----------
---3 1 1: Dice overview.

Dicier includes codes for numbered dice, Yes/And/No/But dice, Fudge dice, and various other die types and symbols, including a wildcard die face. The numbered dice are the only icons that use exactly one character in their codes.

You can adjust some types of dice icon using these OpenType features (see SECTION 4: ADVANCED FEATURES for further information):
	• number and wildcard styles (ss01-11);
	• d4, d8, d10, d12, and d20 (ss12-16);
	• vertical and horizontal barrel dice (ss17-18);
	• mixing pip patterns (cv01-09);
	• triangular 3-pip patterns (cv13);
	• blank-zero numerals (cv14);
	• larger 1-pip on Asian dice (cv15);
	• rotated 6-, 7-, 8-, 2-, and 3-pip (cv16-20);
	• dotted Arabic numerals 6 and 9 (cv21);
	• dice size indicators (cv24);
	• dice-less Taoist trigrams (cv25);
	• dice-less pips (cv26);
	• 100-on-d100 vertical barrel dice (cv28);
	• pipped d12 (cv31);
	• d2 (cv33-36);
	• toggle open and slashed 0 (zero).


----------
---3 1 2: Numbered dice.

Icon: die face with 0 pips.
Code: 0.

Icon: die face with 1 pips.
Code: 1.

Icon: die face with 2 pips.
Code: 2.

Icon: die face with 3 pips.
Code: 3.

Icon: die face with 4 pips.
Code: 4.

Icon: die face with 5 pips.
Code: 5.

Icon: die face with 6 pips.
Code: 6.

Icon: die face with 7 pips.
Code: 7.

Icon: die face with 8 pips.
Code: 8.

Icon: die face with 9 pips.
Code: 9.


----------
---3 1 3: Fudge dice.

Icon: die with plus sign.
Code: P L U S. PLUS.

Icon: die with minus sign.
Code: M I N U S. MINUS.

Icon: blank die.
Code: B L A N K. BLANK.


----------
---3 1 4: Yes, No, And, But... dice.
Icon: die with the word 'Yes'.
Code: Y E S. YES.

Icon: die with the word 'No'.
Code: N O. NO.

Icon: die with the word 'And'.
Code: A N D. AND.

Icon: die with the word 'But'.
Code: B U T. BUT.

Icon: die with the word 'Yes, And'.
Code: Y E S underscore A N D. YES_AND.

Icon: die with the word 'Yes, But'.
Code: Y E S underscore B U T. YES_BUT.

Icon: die with the word 'No, And'.
Code: N O underscore A N D. NO_AND.

Icon: die with the word 'No, But'.
Code: N O underscore B U T. NO_BUT.


----------
---3 1 5: Dice shapes.

Icon: a die silhouette that's circular on the left and square on the right.
Code: D 2.

Icon: an equilateral triangular die silhouette pointing up.
Code: D 4.

Icon: a square die silhouette.
Code: D 6.

Icon: a d8 silhouette (diamond shape).
Code: D 8.

Icon: a flat hexagonal die silhouette.
Code: D 1 0. D10.

Icon: a regular pentagonal die silhouette pointed up.
Code: D 1 2. D12.

Icon: a regular hexagonal die silhouette.
Code: D 2 0. D20.

Icon: a tall, thin barrel die silhouette with the points facing up and down.
Code: B A R R E L. BARREL.

Icon: a wide barrel die silhouette with the points facing left and right.
Code: H underscore B A R R E L. H_BARREL.


----------
---3 1 6: Dice results.

Icon: Arabic numeral 0 on a die outline.
Code: 0 underscore O N underscore D 6. 0_ON_D6.

Icon: Arabic numeral 1 on a die outline.
Code: 1 underscore O N underscore D 6. 1_ON_D6.

Icon: Arabic numeral 2 on a die outline.
Code: 2 underscore O N underscore D 6. 2_ON_D6.

Icon: Arabic numeral 3 on a die outline.
Code: 3 underscore O N underscore D 6. 3_ON_D6.

etc. for every die, with every result up to the maximum on that die.

Icon: hatching on a die outline.
Code: A N Y underscore O N underscore D 6. ANY_ON_D6.

Note 1: These combine 2 codes: result (e.g. 2 underscore O N underscore, 2_ON_) and die (e.g. D 6, D6). Unfortunately, they won’t display correctly in Dark weight.
Note 3: To create d4, d8, d10, d12, d20, and barrel dice using only standard number and wildcard codes (e.g. numbers like 0, 1, 3, 7, the wildcard code A N Y (ANY)), see SECTION 4 3 6: D4, D8, D10, D12, AND D20 DICE, SECTION 4 3 7: BARREL DICE, and SECTION 4 3 25: D2.


----------
---3 1 7: Taoist trigram dice.

Icon: die with heaven trigram (3 horizontal lines).
Code: H E A V E N. HEAVEN.

Icon: die with lake/marsh trigram (a split horizontal line above 2 horizontal lines).
Code 1: L A K E. LAKE.
Code 2: M A R S H. MARSH.

Icon: die with fire trigram (2 horizontal lines with a split horizontal line between).
Code: F I R E. FIRE.

Icon: die with thunder trigram (2 split horizontal lines with a horizontal line beneath).
Code: T H U N D E R. THUNDER.

Icon: die with wind trigram (2 horizontal lines with a split horizontal line beneath).
Code: W I N D. WIND.

Icon: die with water trigram (two split horizontal lines with a horizontal line between).
Code: W A T E R. WATER.

Icon: die with mountain trigram (a horizontal line above 2 split horizontal lines).
Code: M O U N T A I N. MOUNTAIN.

Icon: die with earth/ground trigram (3 split horizontal lines).
Code 1: E A R T H. EARTH.
Code 2: G R O U N D. GROUND.


----------
---3 1 8: Other symbol dice.

Icon: die with exclamation mark.
Code: E X C L A I M. EXCLAIM.

Icon: die with question mark.
Code: Q U E S T I O N. QUESTION.

Icon: die with diagonal slash.
Code: S L A S H. SLASH.

Icon: die with a nought, circle, or ring.
Code 1: N O U G H T. NOUGHT.
Code 2: C I R C L E. CIRCLE.
Code 3: R I N G. RING.

Icon: die with a cross.
Code: C R O S S. CROSS.

Icon: die with a tick or checkmark.
Code 1: C H E C K. CHECK.
Code 2: T I C K. TICK.

Icon: die with hatching (dense diagonal lines).
Code: A N Y. ANY.

Note 1: The any die face is a wildcard used to represent a die face that could be any number (or any other face, depending on the context).
Note 2: The exclamation and question mark die faces are currently sidelined. They will not be included in translations or developed further. This may change in the future.


----------
---3 1 9: Even and odd dice.

Icon: square die face with a text banner with the word 'even' written on it.
Code: E V E N (EVEN).

Icon: square die face with a text banner with the word 'odd' written on it.
Code: O D D (ODD).

Note: To create even and odd versions of d4, d8, d10, d12, d20, and barrel dice, see SECTION 4 3 6: D4, D8, D10, D12, AND D20 DICE and SECTION 4 3 7: BARREL DICE. For even and odd versions of d2 dice, see SECTION 4 3 25: D2.


------------------------------
-----3 2: Dominoes.

----------
---3 2 1: Dominoes overview.

Dicier includes codes for dominoes with up to 9 pips on each side and wildcards—sides with any number of pips. The two sides of each domino are separated by an underscore. Blank sides are represented using 0. You can create a generic domino with the code D O M I N O (DOMINO).

You can adjust some types of domino icon using these OpenType features (see SECTION 4: ADVANCED FEATURES for further information):
	• number and wildcard styles (ss01-11);
	• Chinese dominoes (ss03-05);
	• blank-zero numerals (cv14);
	• dotted Arabic numerals 6 and 9 (cv21);
	• toggle open and slashed 0 (zero).


----------
---3 2 2: Numbered dominoes.

Icon: domino with 0 pips on left and 0 pips on right.
Code: 0 underscore 0. 0_0.

Icon: domino with 0 pips on left and 1 pip on right.
Code: 0 underscore 1. 0_1.

Icon: domino with 0 pips on left and 2 pips on right.
Code: 0 underscore 2. 0_2.

Icon: domino with 0 pips on left and 3 pips on right.
Code: 0 underscore 3. 0_3.

Icon: domino with 0 pips on left and 4 pips on right.
Code: 0 underscore 4. 0_4.

Note: The pattern “number underscore number” can be repeated with any numbers from 1 to 9 and 0 on either side of the domino.


----------
---3 2 3: Wildcard dominos.

Icon: domino with hatching on both sides.
Code 1: A N Y underscore A N Y. ANY_ANY.
Code 2: A N Y underscore D O M. ANY_DOM.

Icon: domino with hatching on left and 0 pips on right.
Code: A N Y underscore 0. ANY_0.

Icon: domino with hatching on left and 1 pips on right.
Code: A N Y underscore 1. ANY_1.

Icon: domino with hatching on left and 2 pips on right.
Code: A N Y underscore 2. ANY_2.

Icon: domino with hatching on left and 3 pips on right.
Code: A N Y underscore 3. ANY_3.

Icon: domino with hatching on left and 4 pips on right.
Code: A N Y underscore 4. ANY_4.

Note: The pattern “A N Y underscore number” or "number underscore A N Y" can be repeated with any numbers from 1 to 9 and 0 on either side of the domino.
Note 2: The any domino sides are wildcards used to represent sides that could be any number. For example, the domino 6 underscore A N Y represents a domino where one side (which may specifically be the left side) has 6 pips and the other side can have any number of pips from 1 to 9 or 0.


------------------------------
-----3 3: Playing cards.

----------
---3 3 1: Playing cards overview.

Dicier includes codes for typical card suits and values (numbers, aces and faces, and jokers) and combinations of values and suits such as the ace of spades.

The codes for numbered playing card values (e.g. T H R E E (THREE), N I N E (NINE), F I V E (FIVE)) are the words for those numbers, spelled out in uppercase letters. The numeral keys (e.g. 3, 9, 5) are dice codes.

You can adjust some types of playing card icon using these OpenType features (see SECTION 4: ADVANCED FEATURES for further information):
	• poker dice (cv10-12);
	• dotted Arabic numerals 6 and 9 (cv21);
	• pentacle-shaped coins (cv22);
	• swap staves/staffs and batons (cv23);
	• crown jewels (cv29);
	• circled star joker (cv30);
	• crossed swords (cv39);
	• toggle open and slashed 0 (zero).


----------
---3 3 2: Card values.

Icon: uppercase A.
Code: A C E. ACE.

Icon: numeral 2.
Code: T W O. TWO.

Icon: numeral 3.
Code: T H R E E. THREE.

Icon: numeral 4.
Code: F O U R. FOUR.

Icon: numeral 5.
Code: F I V E. FIVE.

Icon: numeral 6.
Code: S I X. SIX.

Icon: numeral 7.
Code: S E V E N. SEVEN.

Icon: numeral 8.
Code: E I G H T. EIGHT.

Icon: numeral 9.
Code: N I N E. NINE.

Icon: numeral 10.
Code: T E N. TEN.

Icon: uppercase J.
Code: J A C K. JACK.

Icon: uppercase Q.
Code: Q U E E N. QUEEN.

Icon: uppercase K.
Code: K I N G. KING.


----------
---3 3 3: Card suits.
Icon: hearts suit symbol.
Code: H E A R T S. HEARTS.

Icon: diamonds suit symbol.
Code: D I A M O N D S. DIAMONDS.

Icon: clubs suit symbol.
Code: C L U B S. CLUBS.

Icon: spades suit symbol.
Code: S P A D E S. SPADES.


----------
---3 3 4: Jokers.

Icon: jester face with pointed cap.
Code: J O K E R. JOKER.

Icon: jester face with pointed cap, and the word 'RED' underneath.
Code: R E D underscore J O K E R. RED_JOKER.

Icon: jester face with pointed cap, and the word 'BLACK' underneath.
Code: B L A C K underscore J O K E R. BLACK_JOKER.

Note: The coloured jokers are actually combinations of two codes: the colour (e.g. R E D, RED) and the joker with an underscore (underscore J O K E R, _JOKER). Both parts must use the same Weight and Mode.


----------
---3 3 5: Card value and suit combinations.

Icon: uppercase A and hearts suit symbol.
Code: A C E underscore H E A R T S. ACE_HEARTS

Icon: numeral 2 and hearts suit symbol.
Code: T W O underscore H E A R T S. TWO_HEARTS

Icon: numeral 3 and hearts suit symbol.
Code: T H R E E underscore H E A R T S. THREE_HEARTS

Icon: numeral 4 and hearts suit symbol.
Code: F O U R underscore H E A R T S. FOUR_HEARTS

Icon: numeral 5 and hearts suit symbol.
Code: F I V E underscore H E A R T S. FIVE_HEARTS

Note 1: The pattern “value underscore suit” can be repeated with any other pair of value and suit, e.g. the eight of spades is E I G H T underscore S P A D E S, or the six of clubs is S I X underscore C L U B S.
Note 2: These are actually combinations of two codes: the value followed by underscore (e.g. S I X underscore) and the suit (e.g. C L U B S). This means that you can edit each half (e.g. change Modes, Weights, and colours) separately.
