---
date: '2025-11-11T21:46:57-05:00'
draft: false
title: 'Deterministic Usage of LLM'
---

When using LLM, one of the major concern is the **indeterminism of output**. For example, if I need LLM to generate a JSON of a specific schema for 100 times, I can't guarantee that, in all 100 times, LLM will generate a valid JSON, or a JSON following the schema. This is fine when using LLM as a chatbot, but unacceptable when using LLM as part of a program.

Compared to chat sessions, programs need determinism: `print(1 + 1)` will always print `2` in python, no matter what version of python you use, or what environment you are in. Yet in the case of LLM, nothing has a 100% probability, even when asking LLM what 1 + 1 is. This is just the nature of LLM, that it is based on a probabilistic math model. This doesn't mean we can't have determinism when using LLM.

The one and only way to bring determinism to LLM output is to **run deterministic check on LLM output**, the same way we would validate a human input. This is so obvious, yet often forgotten when designing a workflow involving LLM.

Beyond JSON validation, there are also many other use cases where we can apply similar method to deterministically validate LLM output, and eliminate the possibility of treating an invalid output as valid. The section below shows a list of some very specific examples that I have personally encountered.

## Very specific examples of LLM output validation

### Categorize a list of text excerpt, and compute frequency of category

Given

- a file of text excerpts, where each line is one text excerpt

- a list of categories

We want to label each line with one category using LLM.

We need to ensure each excerpt is classified as is. This means,

- LLM should not modify the excerpt

- LLM should not miss some excerpts

- LLM should not add new excerpt out of nowhere

Here is how I work with LLM in this case:

- ask LLM this question

  ```markdown
  Here is a file of text excerpts. Each line is one excerpt. 
  You need to classify each line into one of these categories: 
    
    <a list of categories>. 

  You should output a csv file of the format

    `text_excerpt,category`
  ```

- Download the csv, and run this python program to validate output

  We validate these facts

  - the LLM-generated csv has all the required columns

  - the text excerpt from LLM-generated csv is exactly the same as the input excerpt (ignoring order)

  ```python
  import pandas as pd
  llm_out = pd.read_csv("llm-output.csv")
  assert all(lr.columns == ['reason', 'categories']), "llm output doesn't have the required columns"

  with open("input-excerpt.txt", "r") as f:
    input_text_li = [line.strip() for line in f.readlines()]

  # Ensure llm keep the original input text as is
  llm_out_li = sorted(list(llm_out["text_excerpt"]))
  assert len(llm_out_li) == len(input_text_li), "number of text excerpts in llm output doesn't match original list of text excerpts"
  assert all([llm_out_li[i] == input_text_li[i] for i in range(len(llm_out_li))]), "some text excerpt in llm output doesn't match original list of text excerpts"
  ```

- After this check, we know with 100% probability that

  - LLM doesn't modify the excerpt

  - LLM doesn't miss some excerpts

  - LLM doesn't add new excerpt out of nowhere

  We can safely count the frequency with this code

  ```python
  print("Frequency of each category:")
  print(llm_out["category"].value_counts())
  ```

### Split a big tex file into multiple files by section

LLM will generate one tex file for one section. We concatenate all section tex, and compare with original big text using `diff`
