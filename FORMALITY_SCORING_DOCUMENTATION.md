"""
FORMALITY SCORING SYSTEM DOCUMENTATION
======================================

## Overview
The formality scoring system quantifies how formal or informal a person's speech is on a scale from 0-100. This is crucial for lie detection analysis as speech formality often changes under stress or deception.

## Algorithm Details

The scoring algorithm identifies various categories of formal and informal words/phrases. Their frequencies, relative to the total word count, are used to adjust a baseline score.

### Word Categories & Examples

#### 1. Formal Indicators
These words and phrases contribute positively to the formality score. They are grouped in the code for nuanced detection but aggregated for the `formal_ratio`.
-   **Formal Transitions & Conjunctions**: `furthermore, however, nevertheless, therefore, consequently, moreover, additionally, subsequently, accordingly, thus, hence, whereas, albeit, notwithstanding, indeed, inasmuch as, insofar as, heretofore, henceforth`
-   **Professional Courtesy & Politeness**: `sir, madam, please, thank you, kindly, respectfully, sincerely, cordially, graciously, humbly, your honor, your excellency, distinguished, esteemed`
-   **Legal/Business Formal Language**: `pursuant to, in accordance with, with regard to, concerning, regarding, herein, thereof, whereby, wherein, whereof, aforementioned, subsequent to, prior to, in lieu of`
-   **Academic/Professional Qualifiers**: `substantially, significantly, predominantly, fundamentally, essentially, particularly, specifically, generally, typically, consistently, primarily, principally, ultimately, comprehensively`
-   **Formal Expressions & Phrases**: `allow me to, permit me to, if I may, with your permission, I would like to express, I wish to convey, it is my understanding, it has come to my attention, I am compelled to, I feel obligated to`

#### 2. Informal Indicators
These words and phrases contribute negatively, with different penalty weights.

**a. Highly Casual Words & Spoken Contractions (Higher Penalty)**
These contribute to the `casual_informal_ratio`.
-   **Casual Interjections & Responses**: `yeah, yep, nah, yup, uh-huh, mm-hmm, nope, sure thing, no way, for real, totally, whatever, awesome, cool, sweet, nice, dude, buddy, man, bro, sis`
-   **Spoken/Informal Contractions**: `gonna, wanna, gotta, kinda, sorta, dunno, shoulda, woulda, coulda, lemme, gimme, betcha, whatcha, lookin, doin, nothin, somethin, anythin, everythin`
-   **Slang & Very Informal Expressions**: `ok, okay, alright, right on, no biggie, no prob, my bad, oh well, so what, big deal, kinda like, sorta like, you know what I mean, if you know what I mean`

**b. Standard English Contractions (Lighter Penalty)**
These contribute to the `standard_contractions_ratio`.
-   **Common Contractions**: `ain't, can't, won't, shouldn't, wouldn't, couldn't, isn't, aren't, wasn't, weren't, haven't, hasn't, hadn't, don't, doesn't, didn't, I'm, you're, he's, she's, it's, we're, they're, I've, you've, we've, they've, I'll, you'll, he'll, she'll, we'll, they'll, I'd, you'd, he'd, she'd, we'd, they'd`

### Calculation Formula

The score is calculated based on the frequency of different categories of formal and informal words, adjusted from a baseline.

1.  **Ratios Calculation**:
    *   `formal_ratio = count_of_formal_words / total_word_count`
    *   `casual_informal_ratio = count_of_highly_casual_words_and_spoken_contractions / total_word_count`
    *   `standard_contractions_ratio = count_of_standard_english_contractions / total_word_count`

2.  **Score Calculation**:
    *   `baseline = 50` (Neutral starting point)
    *   `formal_boost = formal_ratio * 500`
    *   `casual_penalty = casual_informal_ratio * 250`
    *   `standard_contractions_penalty = standard_contractions_ratio * 100`
    *   `raw_score = baseline + formal_boost - casual_penalty - standard_contractions_penalty`

3.  **Final Score**:
    *   `final_formality_score = max(0, min(100, raw_score))` (Score is clamped between 0 and 100)

This approach allows for a nuanced score where different types of informality have different impacts.

### Score Interpretation
- **80-100:** Very High Formality (Professional/Legal language)
- **60-79:** High Formality (Business/Academic discourse)
- **40-59:** Moderate Formality (Semi-formal conversation)
- **20-39:** Low Formality (Casual everyday speech)
- **0-19:** Very Low Formality (Informal/Slang heavy)

## Behavioral Analysis Applications

### Deception Detection Indicators
1. **Sudden Formality Increase:** May indicate rehearsed or prepared responses
2. **Formality Decrease:** Could signal stress, nervousness, or loss of composure
3. **Inconsistent Formality:** Rapid changes may indicate cognitive load from deception

### Baseline Establishment
- Compare current formality to person's normal speaking pattern
- Consider context (formal interview vs casual conversation)
- Account for cultural and educational background

### Stress Indicators
- Formal speakers becoming informal under pressure
- Informal speakers becoming overly formal when nervous
- Mixed formal/informal patterns indicating uncertainty

## Technical Implementation Notes

### Why 1000x/500x Weighting?
- Formal words are typically rare but highly impactful
- Informal words are common but should still affect score
- 2:1 ratio allows for natural speech mixing both styles
- 1% formal words = 10 points, 1% informal words = -5 points

### Pattern Matching
- Case-insensitive matching for natural speech variations
- Word boundary matching to avoid partial word matches
- Multi-word phrase support for complex formal expressions

### Limitations
- Cultural context not considered (though word lists can be expanded).
- Professional jargon specific to certain fields might not be fully captured as "formal" unless explicitly listed.
- Sarcasm/irony detection is not part of this specific scoring module.
- Regional dialect variations that use non-standard contractions or unique casual terms might not be accurately scored.

## Technical Implementation Notes - Updated Weighting Rationale

The weighting system aims to balance the impact of different word types:
- **Baseline (50)**: Assumes speech starts from a neutral formality level.
- **Formal Words (Boost Factor: 500x)**: Formal words, while potentially less frequent, have a strong positive impact on perceived formality. A small percentage of these words can significantly elevate the score.
- **Highly Casual/Slang Words (Penalty Factor: 250x)**: These words have a moderate negative impact. Their presence clearly reduces formality.
- **Standard Contractions (Penalty Factor: 100x)**: Standard contractions (e.g., "can't", "it's") are common even in semi-formal speech but do reduce strict formality. They have a lighter penalty compared to slang or spoken contractions like "gonna".

This multi-factor approach allows for a score that reflects common speech patterns where a mix of word types might occur, rather than a simple binary formal/informal count.

## Future Enhancements
1. Context-aware scoring (e.g., adjusting baseline or weights based on detected conversation context like "interview" vs "casual chat").
2. Personal baseline learning
3. Industry-specific formal vocabulary
4. Cultural formality norms
5. Temporal formality change detection
6. Integration with other linguistic indicators
"""
