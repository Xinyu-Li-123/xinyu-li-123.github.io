---
layout: math_post
title: My first post in markdown
---

This is my first post written in markdown

{% for quote in site.data.random_quotes %}

* {{ quote.content }} --{{ quote.source }}

{% endfor %}

```python
def foo(n=10):
    print("f" + "o"*n)
```

Start time: {{ site.time | slice: 0, 16}}

This is an equation: $$ \sqrt{x} = 2 $$. This is another but on a different line

$$ y^2 = 3 $$

<img src="/images/lucky_star.jpg" />

