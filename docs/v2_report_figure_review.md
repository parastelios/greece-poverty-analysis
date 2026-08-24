# Report review — findings and figure changes

Reviewer observations, checked against the data and sharpened. Items marked
**[verified]** were confirmed against the artifacts; **[correction]** marks
places where the original observation was based on a wrong premise; **[reversal]**
marks a point that contradicts an earlier decision and needs a deliberate call.

---

## 1. The report takes too long to reach its argument

**Agreed, and this is the most important item on the list.**

The observation is not really about length. It is about time-to-headline: the
previous report could be understood in one sitting, and this one requires
walking all eight stages before the argument resolves.

**Recommendation: preserve the depth of the current report, but restore the
previous report's speed through a one-page findings summary, shorter stage
openings, and less repetition of limitations. Keep the full technical
qualifications available without making every reader encounter them before
reaching the result.**

Concretely, three changes:

- **A one-page summary before Stage 1**, carrying the size of the gap, the three
  things that account for part of it, the four things the evidence does not
  support, and the unexplained remainder. A reader who stops there should come
  away with an accurate headline.
- **Shorter stage openings.** Several stages currently spend two or three
  paragraphs restating where the argument has got to before adding anything.
- **Less repetition of limitations.** The same qualifications are currently
  stated in the stage that raises them, again in the conclusion, and again in
  the limitations section. Each should appear once, at full strength, in the
  place a reader needs it.

Note also that the "extended executive summary" role the previous report played
is now largely served by the narrative companion. The technical report should be
the document that does *not* compress.

---

## 2. Show all EU countries as context, not just Greece and the EU average

**Agreed. Apply to every Greece-vs-EU line chart** (the paradox chart, the
threshold chart, the three supported-measure tabs, the migration chart).

Implementation: all 27 countries drawn in grey as a background layer, Greece and
the EU median in front, a country's name and value revealed on hover or keyboard
focus.

Three constraints to settle before building:

- **Hover is not available on touch devices or by keyboard.** The highlight
  needs a tap and an arrow-key equivalent, or the context layer is decorative
  for a large share of readers.
- **The table fallback cannot carry 27 series.** For a ten-year window that is
  270 numbers. Proposal: the table continues to carry Greece and the EU median
  only, with the full country set available in the statistical appendix.
- **Grey must stay legible in both themes** — see item 10.

---

## 3. The AROPE figure is not intuitive

**Agreed, with a concrete replacement.**

The first tab currently plots two *derived gaps*, which asks the reader to hold
a subtraction in their head. Replace it with the three underlying series in
**% of households** — reported hardship, AROPE, and income poverty — so that
AROPE visibly sits between the other two and the reader sees the distance rather
than being told it.

Keep the second tab ("what AROPE actually closes") unchanged: it plots the
quantity the stage's conclusion rests on and it works.

---

## 4. The AROPE breakdown figure mixes two questions

Three separate points here.

**(a) The household categories look arbitrary — [correction]**
They are not arbitrary: "one adult aged 65+" and "two adults, at least one 65+"
are standard Eurostat household types, and they are the only two the extract
contains. The defect is real but it is a **labelling** failure, not a selection
failure — nothing on the figure tells the reader these are standard categories
rather than a choice we made. Either label them as such or drop the view.

**(b) Show gender instead — [verified, with a limit]**
A sex breakdown exists and can be plotted: Greece and the EU27, 2015–2025,
male/female/total. **It covers the 65-and-over group only.** So this can replace
the household view honestly, but the tab must be labelled "Aged 65 and over, by
sex" — not "by sex", which would imply whole-population coverage we do not have.

**(c) "What drove the 2025 increase?" should be standalone — agreed.**
It answers a different question (what drove one year's change) from the rest of
the figure (what sits behind AROPE over a decade). Tabs imply alternative views
of one question; this is a second question. Promote it to its own figure.

---

## 5. The threshold figure does not make its point

**Agreed on the diagnosis, but the proposed fix would not work.**

The confusion is the point of the observation: the first tab shows the real
threshold as an index, and an index of a threshold is two abstractions deep.

**A ladder will not fix the time-series tab — [correction].** A ladder ranks
countries at one moment; the point of this tab is movement over time. A ladder
is still worth having, but as a *separate* view of where Greece sits against
every other country in the latest year.

**Plotting the threshold beside the median income is also wrong — [correction].**
The threshold is mechanically 60% of median equivalised income, so the two
series are the same curve at two scales. It would look like corroboration while
adding no information.

Three options that do work, in order of preference:

1. **Nominal against inflation-adjusted threshold.** This is the one that shows
   the mechanism directly: the two lines separate, and the separation *is* the
   erosion the chapter is about. Nothing has to be inferred.

   **[verified]** Both series already exist in `analysis_dataset.csv`
   (`gr_arop_threshold_nominal_eur` and `gr_arop_threshold_real_2008eur`), so
   this is a relabelling of data we hold, not new work. The contrast is stark
   enough to carry the chapter on its own:

   | | Peak | 2025 | Change |
   |---|---:|---:|---:|
   | Threshold, cash terms | €7,178 (2010) | €7,020 | **&minus;2.2%** |
   | Threshold, 2008 purchasing power | €6,808 (2009) | €5,358 | **&minus;21.3%** |

   In cash terms the Greek poverty line is essentially back where it peaked. In
   what it actually buys, it is still a fifth below. That is the entire point of
   the chapter, and on this chart a reader sees it without being told.
2. **Real threshold indexed to 2008, with the baseline and the key values
   annotated on the chart.** Keeps the current form but stops asking the reader
   to decode an unlabelled index.
3. **A country ladder for the latest year**, as a separate view rather than a
   replacement.

---

## 6. The affordability scatter is hard to read

**Agreed it is hard to read. Recommend against the 3D proposal.**

A three-dimensional scatter with time on the z-axis would make it worse: points
occlude each other, position cannot be read without rotation, there is no
reliable way to compare two points, it is unusable on a phone, and it cannot be
made accessible.

Better options, in order of preference:

1. **Small multiples** — one small panel per affordability item, each showing the
   same relationship. Comparison becomes visual rather than cognitive.
2. **Greece's own path highlighted** — draw Greece's year-to-year trajectory as
   a connected line through the cloud, with the other countries as faint points.
   This shows time without a third axis.
3. **Keep the current form and reduce the load** — fewer years shown by default,
   with the full set behind a control.

Recommend 1, or 1 combined with 2.

---

## 7. The correlation heatmap

**(a) Restore the full matrix — [reversal, needs a deliberate decision]**
An earlier review asked for exactly the opposite: *"Each 13×13 correlation matrix
shows both symmetric halves and the diagonal. That buries the important result …
show one triangle."* The current triangle exists because of that instruction.

Both positions are defensible and this should be settled once. A middle option
that meets both concerns: **show the full matrix but blank the diagonal**, which
is always 1 and carries no information. That removes the genuinely redundant
cells without the half-empty appearance.

Terminology note for the shared version: what is currently hidden is the upper
**triangle**, not "the diagonals".

**(b) The hardship-only view should be standalone — agreed**, for the same reason
as item 4(c): it answers a different question from the matrices.

---

## 8. The rank-trajectory figure still does not work

**Agreed — this is the weakest figure in the report**, and the underlying reason
is structural rather than cosmetic. It asks the reader to read an *inverted rank
axis*, where two of the three series sit permanently at the same value, and where
a country's position changes when other countries move.

Recommend abandoning ranks for this figure. Instead show, for each of the three
indicators, **the actual distribution of all 27 countries with Greece marked** —
three small strips, one per indicator. "Worst on two, close to worst on the
third" then reads instantly, the values are real quantities rather than
positions, and the awkward inverted axis disappears.

---

## 9. The pre-crisis comparison may work better as a table

**Largely agreed.** With six observations and a ten-year gap, a table is
genuinely competitive with a chart, and the gap stops being a visual problem.

Recommend: **lead with the table** — one row per round, carrying Greece's level,
the comparison median, the gap and the rank — and keep a single small chart of
the *level* beneath it, because the level-recovered-but-position-did-not point is
easier to see than to read. Drop the rank tab; rank belongs in the table column.

---

## 10. Colour contrast — [verified, and worse than reported]

Measured against WCAG (4.5:1 for text, 3:1 for graphics):

| Token | On dark | On light | Verdict |
|---|---:|---:|---|
| Negative correlation (`--div-neg`) | **2.96:1** | 5.74:1 | **fails on dark, even for graphics** |
| Positive correlation (`--div-pos`) | 4.46:1 | 3.81:1 | marginal both themes |
| Axis labels (`--text-muted`, 11px) | 4.85:1 | **3.50:1** | **fails on light** |

Two things worth flagging:

- The axis-label token is **the same value in both themes**, which is why it
  fails in one of them. It was tuned for a light page.
- The worst failure is on **dark** for the correlation colours and on **light**
  for the axis labels, so this cannot be fixed by adjusting one theme.

This should be fixed once at the token level rather than per figure, and then
re-measured across all figures.

---

## 11. Institutional trust over time — [correction: not currently possible]

The report holds **two numbers only**: Greece 32% and the OECD average 39%, for
central government, 2023. There is no time series in the project.

Earlier OECD waves exist, but whether they yield a **consistent annual series**
for this indicator is unverified — question wording, country coverage and
periodicity would all need checking against the primary releases first. This
should be treated as a separate source review with an uncertain outcome, not as
data we can expect to obtain.

Until that review is done the figure remains a 2023 snapshot and must not be
redrawn as though a trend were available.

---

## Sequencing

Items 10 and 1 are independent of the rest and can be done first: the contrast
fix touches tokens, the summary touches only the report.

Items 2, 3, 4, 5, 6, 7, 8 and 9 all change figures, and each change touches the
visual manifest, the figure checks, and any document carrying that figure.
Recommend doing them as one pass rather than piecemeal, and re-running the figure
checks and the three document gates after each.
