---
date: '2025-11-11T21:46:57-05:00'
draft: false
title: '如何消除 LLM 的不确定性？'
---

LLM （GPT）的本质是一个概率模型。这意味着假如我们问 ChatGPT 100 次“1 + 1 等于几”，无论实际上回答正确的概率有多高，从数学理论上，我们都无法保证 ChatGPT 的回答一直是 2 [^1]。
作为聊天助手，这没什么问题，毕竟这种错误的概率很小，而且错了也没啥影响。但如果我们想把 LLM 融入代码程序中，像这样把它当成一个函数调用，那我们就必须要考虑到 LLM 本质上的不确定性。

```python
def main():
  args = parse_args()
  step_1_ans = step_1(args)
  # A magical step where we ask LLM for an answer
  step_2_ans = ask_llm(step_1_ans)
  result = step_3(step_2_ans)
  print(result) 
```

## LLM 适合做什么事？

一句话总结，在代码中，我们应当**把 LLM 的输出当成人类的输出**

- 对比程序，人类更适合处理无法用代码解决的、不确定因素多的事情。例如评判一段文本的情感。

- 一段程序在处理人类的输入时，需要做各种验证，例如检查格式、语法语义错误（输出的数字是否是正整数，输入的除法是否有除以 0）。

### 反例：1 + 1 = ?

```python
def ask_llm(prompt: str) -> str:
  # 向 LLM 输入 prompt，返回输出的字符串
  return "xxx"

def llm_add(x: int, y: int) -> int:
  return int(ask_llm(f"输出 {x} + {y} 的结果"))

def main():
  nums_str = input("请输入两个数字：")
  x, y = [int(n) for n in nums_str.split(" ")]
  ans = ask_llm(x, y)
  print(f"LLM 跟我说 {x} + {y} = {ans}")
```

在这段代码中，验证 LLM 输出的唯一方法就是用 python 也算一遍`x + y`。emmmmm

### 正例：生成一个特定格式的 JSON 文件

When using LLM, one of the major concern is the **indeterminism of output**. For example, if I need LLM to generate a JSON of a specific schema for 100 times, I can't guarantee that, in all 100 times, LLM will generate a valid JSON, or a JSON following the schema. This is fine when using LLM as a chatbot, but unacceptable when using LLM as part of a program.

Compared to chat sessions, programs need determinism: `print(1 + 1)` will always print `2` in python, no matter what version of python you use, or what environment you are in. Yet in the case of LLM, nothing has a 100% probability, even when asking LLM what 1 + 1 is. This is just the nature of LLM, that it is based on a probabilistic math model. This doesn't mean we can't have determinism when using LLM.

The one and only way to bring determinism to LLM output is to **run deterministic check on LLM output**, the same way we would validate a human input. This is so obvious, yet often forgotten when designing a workflow involving LLM.

Beyond JSON validation, there are also many other use cases where we can apply similar method to deterministically validate LLM output, and eliminate the possibility of treating an invalid output as valid. The section below shows a list of some very specific examples that I have personally encountered.

## 具体案例

以下是一些 LLM + Validation 的具体案例

### 对一个文本文档的每一行生成一个标签

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

### 把一份巨大的 Tex 文件按章节分成多个小的 Tex 文件

LLM will generate one tex file for one section. We concatenate all section tex, and compare with original big text using `diff`

[^1]: 准确的说，这里其实有两层问题：

    1. 反复输入同一个问题，无论输入的问题有多简单，我们都无法保证 GPT 每次输出的答案是相同的

        这个问题更多是一个工程问题，比较容易解决。

        决定 GPT 模型输出的因素有两个：**模型参数**和**解码策略**。

        - 模型参数：固定模型参数，输入一段 token ，模型输出的是下个 token 的概率分布，即词表中每个 token 被选做下个 token 的概率。例如，输入“煎饼果”，GPT 会输出一个概率分布：这个分布中，“子”的概率可能是 99.999999999%（“煎饼果子”），"肉"的概率可能是 0.0000000009%（因为“果肉”也是一个中文词组），而英文单词“banana”或者日文字符“あ”的概率则远小于 0.0000000001%。

          > token 的定义不太直观，例如一个英文单词“encoding”可以被分词器（tokenizer）分成两个 token ：“encod”，“ing” 。目前 token 一词没有很好的翻译，我比较喜欢的翻译是“词元”，但这里我们就不翻译了。

        - 解码策略：解码策略决定了从模型输出的概率分布中采样的方法。它由**温度**和**采样策略**组成。

          - 温度：温度是一个数字，它能对模型输出的分布进行调整，温度越高，低概率的 token 被选中的概率越高，模型的“想象力”越丰富。

          - 采样策略：常见的采样策略有：

            - 贪心策略：选概率最大的 token 作为输出

            - top k：在概率最高的 k 个 token 中，按它们的概率选一个作为输出

        如果我们真的想要确保同样输出，多次输出相同，我们可以固定模型参数、并采用温度为 0 、贪心采样的解码策略。

    2. 无论输入的问题有多简单，我们都无法保证 GPT 输出的答案是正确的

        这个问题无法被真正解决，其本质是源于 GPT 模型的结构限制。以 1 + 1 为例：

        - CPU 计算 1 + 1，是通过特定组合的电路（算术逻辑单元 ALU），把数字编码成二进制电平，再按照事先设计好的加法逻辑运算。在理想条件下，同样的输入必然得到正确的输出，这是可以形式化证明的。

        - GPT 计算 1 + 1，则是用模型参数定义了一个函数：输入一串 token，输出“下一个 token 的概率分布”。当你输入“1 + 1 =”时，它只是学会了给“2”一个很高的概率，但也可能给“3”，“0”一些非零概率。训练目标是“拟合语料中的下一个 token”，而不是“实现一个严格正确的加法算法”。

        所以，即使我们固定模型参数、使用完全确定性的解码策略，也只能保证同样的输入每次得到**同一个**输出，而不能保证这个输出在数学上永远是**正确**的。
