---
date: '2025-11-11T21:46:57-05:00'
draft: false
title: '如何减少 LLM 的不确定性？'
---

## 关于 LLM 的输入

### 使用模板，程序化生成输入

尽量降低人类输入的灵活度

[dspy](https://dspy.ai/)

[jinja](https://jinja.palletsprojects.com/en/stable/)

### Agent，Tool Use，Function Call

使用更加有效地获取信息

与环境互动，生成信息，获取信息

保险起见，应该默认开启只读模式（plan mode）

## 关于 LLM 的输出

从输出的角度，我们可以通过对输出进行程序化验证，消灭 LLM 输出的不确定性。

LLM （GPT）的本质是一个概率模型。这意味着假如我们问 ChatGPT 100 次“1 + 1 等于几”，无论实际上回答正确的概率有多高，从数学理论上，我们都无法保证 ChatGPT 的回答一直是 2 [^1]。
作为聊天助手，这没什么问题，毕竟这种错误的概率很小，而且错了也没啥影响。但如果我们想把 LLM 融入代码程序中，把它当成一个函数调用，那我们就必须要考虑到 LLM 本质上的不确定性。

在依赖 LLM 的代码中，我认为我们应当**把 LLM 当成人类对待**，这意味着：

- **LLM 适合做需要人来做的事**：对比程序，人类（LLM）更适合处理无法用代码解决的、不确定因素多的事情，例如评判一段文本的情感；而一些代码已经做的很好的事情，就不应该让人（LLM）来做，例如质因数分解。

- **应当像验证人类输入一样，使用代码验证 LLM 的输出内容**：一段程序在处理人类的输入时，需要做各种验证，例如检查格式、语法语义错误（输出的数字是否是正整数，输入的除法是否有除以 0）。同样的，我们也应该对 LLM 的输出做相似的验证。

  值得注意的是，通过程序化，我们只能将 LLM 的输出控制在一个人为划定的范围，但这并不能避免 LLM 犯错。比如，我们可以预先给定一批标签，然后让 LLM 对一段文本选择一个标签。我们可以通过程序化验证保证 LLM 要么输出我们预设的标签，要么报错，而不会输出一个不存在的标签；但我们无法保证 LLM 对文本做出的分类是正确的。

## 具体案例

以下是一些对 LLM 输出内容进行验证的具体案例

### [输出] 对一个文本文档的每一行生成一个标签

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

### [输出] 使用 jinja 模板，填空生成一个特定格式的 JSON 文件

> 源自这个 GitHub Repository：[eval-setup-agent](https://github.com/CMU-MCDS-Capstone-LLM/eval-setup-agent) 。

我们希望 LLM 生成一系列不同类型的变量的值，用来填充一个 jinja2 模板，以此生成一个 JSON 文件。具体来说，我们想让 LLM 阅读一个 python 的代码，生成一个 Dockerfile 用来配置该代码库的环境（例如需要在系统安装 Postgresql，并在 python 的虚拟环境里运行 `pip install -r dep/requirements-dev.txt`）。但直接生成一个完整的 Dockerfile 自由度太高了，LLM 可能犯错的地方太多了。因此，我们预先确定一个 Dockerfile 的模板，然后只要求 LLM 填充其中的变量。

```python
def main():
  template: str = get_template_from_path("/path/to/jinja2_template")
  args = parse_args()
  codebase_path = get_codebase_from_config(args.config)
  decisions = ask_llm(codebase_path)
  output = fill_template_with_vars(decisions, template)
```

我们可以制定一个 [JSON Schema](https://json-schema.org/)，用来规定生成的 JSON Object 的每个域的类型和值域，然后使用代码验证 LLM 的输出。

```json
TODO: ...
```

### [输出] 选择性地将 Latex VSCode snippet 转换成 Typst VSCode snippet

Vscode snippet 是一个 JSON 对象。我想将一个现有的 Latex 的 VSCode Snippet 转换成 Typst 的 VSCode snippet。但 Latex 中有些 snippet 没什么必要转换成 Typst（例如`\subsubsection{xxx}`，Typst 直接打`=== xxx`就行）。我的思路是让 LLM Chatbot 生成 JSON-only 的输出，然后使用 JSON Schema 过一遍格式，再用 python 脚本确认 LLM 没有凭空捏造新的 snippet。

LLM 的输出格式是

- 如果应该生成 Typst snippet，输出

  ```json
  {
    "snippet-name": {
      "is_needed_for_typst": { "const": true },
      "prefix": { "type": "string", "minLength": 1 },
      "body": { "type": "string" },
      "description": { "type": "string" }

    }
  }
  ```

- 如果不应该生成 Typst snippet，输出

  ```json
  {
    "snippet-name": {
      "is_needed_for_typst": { "const": false },
      "reason": { "type": "string", "minLength": 1 }
    }
  }
  ```

以下是我的 prompt 和脚本：

#### Prompt

Given the following latex.json snippet file. For each snippet, determine if it's needed in typst. If not, provide a one-line reason. If needed, generate a typst version of keymap. You must follow this json schema, and output in the same order as the provided latex json file:

JSON Schema for your output (`schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": { "$ref": "#/$defs/typstEntry" },

  "$defs": {
    "typstEntry": {
      "oneOf": [
        { "$ref": "#/$defs/needed" },
        { "$ref": "#/$defs/notNeeded" }
      ]
    },

    "needed": {
      "type": "object",
      "additionalProperties": false,
      "required": ["is_needed_for_typst", "prefix", "body", "description"],
      "properties": {
        "is_needed_for_typst": { "const": true },
        "prefix": { "type": "string", "minLength": 1 },
        "body": { "type": "string" },
        "description": { "type": "string" }
      }
    },

    "notNeeded": {
      "type": "object",
      "additionalProperties": false,
      "required": ["is_needed_for_typst", "reason"],
      "properties": {
        "is_needed_for_typst": { "const": false },
        "reason": { "type": "string", "minLength": 1 }
      }
    }
  }
}
```

[`latex.json`](https://github.com/rafamadriz/friendly-snippets/blob/main/snippets/latex.json):

```json
{
    "item": {
        "prefix": "item",
        "body": "\n\\item ",
        "description": "\\item on a newline"
    },
    "subscript": {
        "prefix": "__",
        "body": "_{${1:${TM_SELECTED_TEXT}}}",
        "description": "subscript"
    },
    "superscript": {
        "prefix": "**",
        "body": "^{${1:${TM_SELECTED_TEXT}}}",
        "description": "superscript"
    },
    <Actual content truncated due to its length>
}
```

#### 脚本

文件夹结构

```
.
├── latex.json
├── llm-output.json
├── llm-output-to-snippet.py
├── schema.json
├── typst.json
└── validate-json.py
```

`validate-json.py`: 根据 `schema.json`（），验证 LLM 输出的 JSON `llm-output.json` 是否符合标准。

```python
#!/usr/bin/env python3
#./validate-json.py
import json
import sys
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError, SchemaError


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(
    schema_path: str = "schema.json", instance_path: str = "llm-output.json"
) -> int:
    try:
        schema = load_json(schema_path)
        instance = load_json(instance_path)

        # Ensure the schema itself is valid for this draft
        Draft202012Validator.check_schema(schema)

        # Validate instance
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))

        if not errors:
            print(f"OK: '{instance_path}' is valid against '{schema_path}'")
            return 0

        print(f"FAIL: '{instance_path}' is NOT valid against '{schema_path}'")
        for err in errors:
            path = "$" + "".join(
                f"[{p!r}]" if isinstance(p, str) else f"[{p}]" for p in err.path
            )
            print(f"- {path}: {err.message}")
        return 1

    except FileNotFoundError as e:
        print(f"File not found: {e.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(
            f"Invalid JSON in '{e.doc}' at line {e.lineno}, col {e.colno}: {e.msg}",
            file=sys.stderr,
        )
        return 3
    except SchemaError as e:
        print(f"SchemaError: {e.message}", file=sys.stderr)
        return 4
    except ValidationError as e:
        # In case you switch to validator.validate(...) elsewhere
        print(f"ValidationError: {e.message}", file=sys.stderr)
        return 5


def validate_content(input_path: str, output_path: str) -> int:
    with open(input_path, "r") as f:
        input_json = json.load(f)

    with open(output_path, "r") as f:
        output_json = json.load(f)

    input_keys = list(input_json.keys())
    output_keys = list(output_json.keys())
    assert sorted(input_keys) == sorted(output_keys), (
        "Input and output doesn't have same key content"
    )

    print(f"OK: {input_path} and {output_path} have same key content.")
    return 0


def main(schema_path: str, input_path: str, output_path: str) -> int:
    ret = validate_schema(schema_path, output_path)
    if ret != 0:
        return ret

    ret = validate_content(input_path, output_path)
    return ret


if __name__ == "__main__":
    schema_path = sys.argv[1] if len(sys.argv) > 1 else "schema.json"
    input_path = sys.argv[2] if len(sys.argv) > 2 else "latex.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "llm-output.json"
    raise SystemExit(main(schema_path, input_path, output_path))
```

`llm-output-to-snippet.py`：提取被 LLM 标记为 `is_needed_for_typst: true` 的 snippet。

```python
#!/usr/bin/env python3
#./llm-output-to-snippet.py
import json
from typing import Dict

llm_output_path = "llm-output.json"
snippet_output_path = "typst.json"

with open(llm_output_path, "r") as f:
    llm_output_json: Dict[str, dict] = json.load(f)

snippet_json = {}
for k, v in llm_output_json.items():
    if not v["is_needed_for_typst"]:
        continue

    snippet_json[k] = v
    snippet_json[k].pop("is_needed_for_typst")

with open(snippet_output_path, "w") as f:
    json.dump(snippet_json, f)
```

### [输出] 把一份巨大的 Tex 文件按章节分成多个小的 Tex 文件

LLM will generate one tex file for one section. We concatenate all section tex, and compare with original big text using `diff`

## 一些有趣的反例

学习一个东西的一个方法是举反例，学习 LLM 的使用也不例外。在这个章节里，我们收集了一些使用 LLM 的反面教材，有的只是思维实验，有的是在真实世界中遇到的案例。

### [输入, 输出] 万能的自然语言编译器

既然 LLM 那么有用，干脆一步到位，也别说什么取代程序员了，直接取代编程语言吧。我们设计一个基于 LLM 的自然语言编译器：

> 给定一段自然语言描述的需求，和一个目标平台（如 x86_64 ），通过 LLM 直接输出机器码，将自然语言翻译成可以跑在目标平台的可执行文件（如 ELF ）。

我们假设在 x86_64 平台，使用`debian:bookworm-slim` 的 Docker 镜像作为执行程序的环境（开个 Docker 以防 LLM 把我电脑炸了，毕竟我们在做得是让 LLM 在我们的机器上执行任意程序）。

按照我们前文的说法，我们应当把 LLM 当成人类，人类怎么和电脑互动，LLM 就怎么和电脑互动。那人该怎么手动输入机器码，生成一个可执行文件呢？问了一下 ChatGPT，一个简单的方法是在命令行里使用`xxd`，在 stdin 里输入十六进制，输出到一个文件。例如：

```bash
cat <<'EOF' | xxd -r -p > my_prog
<hex num> <hex num> <hex num> ...
EOF

chmod +x my_prog
./my_prog
```

我们使用 ELF 格式（Unix / Unix-like 系统，x86 处理器上的可执行文件格式）。

## 相关框架

### [dspy](https://dspy.ai/)

### 这个演讲

[一个软工人的辩白](https://www.bilibili.com/video/BV1KEinBtEU6)，演讲者jyy

第二部分和本文相关

TODO: Summarize that talk in this blog post

## 脚注

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
