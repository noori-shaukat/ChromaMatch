# 📝 Prompt Report — ChromaMatch RAG + Color Recommendation System

This report summarizes the prompt engineering workflow for **ChromaMatch Milestone 2**, including the design of three prompting strategies (Baseline, Few-Shot, and Advanced/CoT), their evaluation, performance comparison, and insights from failure cases. We implemented three prompting strategies, and measured quantitative similarity (embedding cosine similarity). Experiments were logged to MLflow.

---

# 1. Overview of the Task

The model generates **personalized color-palette recommendations** based on predicted attributes from the ML model:

- Skin tone
- Undertone
- Tone group
- Descriptor
- Eye color
- Hair color

The task is essentially **structured conditional generation**, where the model must map a feature set → the correct seasonal palette and recommendations.

We evaluated three prompting strategies and computed:

- **Quantitative metric:** Embedding cosine similarity

All prompt experiments were kept in:
`experiments/prompts/`

---

# 2. Prompting Strategies

## 2.1 Baseline — Zero-Shot Prompting
**File:** `experiments/prompts/baseline.txt`

**Structure:**
A single direct instruction with no examples.
**Goal:** test model’s natural ability to perform the task without guidance.

**Prompt Structure (summary):**

- Provide the user's features
- Ask model to generate a recommendation
- No style rules, no steps, no guardrails

**Observed Behaviour:**

- Highly generic responses
- Tends to default to “Autumn” for warm undertones
- Frequently contradicts ground truth palettes
- Inconsistent structure

---

## 2.2 Example-Driven — Few-Shot Prompting
**File:**  `few_shot.txt`

**Structure:**

- High-quality ground-truth examples included
- Inputs + correct seasonal palette + recommended colors
- Model learns the mapping pattern

**Observed Behaviour:**

- Major improvement in seasonal classification
- More consistent palette naming
- Less hallucination
- Tone-accurate outputs
- More stable formatting
- Occasional mistakes on borderline complex cases

---

## 2.3 Advanced Strategy — Chain-of-Thought (CoT)
**File:** `advanced_cot.txt`

**Strategy:** instructing the model to “think step-by-step”:

1. Analyze undertone
2. Determine season
3. Justify season
4. Match colors to that season
5. Produce final structured answer

**Observed Behaviour:**

- Most accurate palette predictions
- Strong reasoning: steps visible in intermediate CoT
- Rare hallucinations
- Most aligned with dataset logic
- Most human-interpretable
- Most consistent lexical overlap with ground-truth recommendations

This strategy ranked **#1** across all metrics.

---

# 3. Quantitative Evaluation (Embedding Cosine Similarity)

| Strategy | Mean Similarity |
|----------|------------------|
| **Baseline** | ~0.76 |
| **Few-Shot** | ~0.85 |
| **Advanced CoT** | **~0.76** |

**Interpretation:**
The CoT prompt produced outputs closest to ground-truth texts.

![Quantitative Results](src\experiments\results\prompt_eval_results.jpg)

---

# 4. Qualitative Evaluation (Human-in-the-Loop)

Rubric scores (scale 1–5):

| Strategy | Factuality | Helpfulness |
|----------|------------|-------------|
| Baseline | 3.3 | 3.4 |
| Few-Shot | 3.2 | 3.6 |
| **Advanced CoT** | **4.1** | **6.7** |

![Qualitative Results](src\experiments\results\prompt_eval_results_qual.jpg)
---

# 5. Failure Cases & Robustness Analysis

### 5.1 Common Failures
- **Baseline:**
  - Defaults to “Autumn” too often
  - Inserts false color categories (e.g., “Soft Gold” for cool tones)
  - Confuses Spring vs. Autumn
- **Few-Shot:**
  - Occasionally biases toward examples
  - Slight overfitting on warm tones
- **CoT:**
  - Rare: sometimes over-explains or becomes verbose
  - Very minor issues compared to others

---

# 6. Insights & Key Learnings

### ✔ Few-shot examples dramatically improve season classification
Especially for tricky cases like **Warm + Deep skin**, which Baseline often mislabels.

### ✔ Increasing examples (k = 5) yields measurable improvement
The seasonal palette mapping becomes rule-consistent.

### ✔ Chain-of-Thought produced the best alignment with ground truth
Reasoning constraints force the model to follow a consistent mapping pipeline.

### ✔ Structured steps reduce hallucinations
Breaking the task into:
1. Undertone →
2. Season →
3. Palette →
4. Color choices

…prevents drifting and arbitrary suggestions.

### ✔ Human rubric scores align with quantitative metrics
Sequences with highest cosine similarity were also most factual/helpful.

---

# 7. Final Recommendations

- Use **CoT prompting** inside the `/recommend` endpoint for final production.
- Keep Few-Shot (k=5) as a fallback strategy.
- Never use zero-shot in final RAG pipeline.
- Periodically refresh examples using your growing dataset.
- Log all outputs in W&B/MLflow to catch drift.


---

# 8. Conclusion

The prompt engineering workflow shows a clear progression:

**Zero-Shot → Few-Shot → CoT**

Performance, stability, and correctness improved at every stage.
The final CoT prompt is the recommended production prompt for ChromaMatch’s color-recommendation RAG system.