---
date: '2025-05-30T08:31:00-04:00'
draft: false
title: '04 异常处理'
mathjax: false
---

## 异常

异常分为 Exception 和 Error，其继承关系如下

TODO: Insert inheritance image

Exception 是可以被处理的异常，如`NullPointerException`或`IllegalArgumentException`；Error 是不一定能被处理的异常，如`OutOfMemoryError`，`NoClassDefFoundError`

如果 Exception 没有被处理，那么程序无法被编译。

方法可以通过`throw`关键词表示调用方法时可能抛出的异常，如`String.getBytes(String)`的签名

```Java
public byte[] getBytes(String charsetName) throws UnsupportedEncodingException {
    ...
}
```

在调用`String.getBytes(String)`时，必须使用一个 try-catch 块处理`UnsupportedEncodingException`。

不过如果在另一个被标记为`throws UnsupportedEncodingException`的方法里调用`String.getBytes(String)`，我们就不需要处理异常。异常处理会被下放到调用该方法的其他方法。最坏情况我们必须要在`main`方法里处理该异常，除非`main`也被标记为`throws UnsupportedEncodingException`。如

```java
```

在处理异常时，我们可以使用`printStackTrace()`打印异常栈，如

```java
try {
  // ...
} catch (UnsupportedEncodingException e) {
  e.printStackTrace();
}
```

## try-catch 语句

多个 catch 语句按顺序分别处理不同异常

使用`catch (ExceptionA | ExceptionB)`同时处理多个异常

使用 finally 语句，无论异常是否发生，都在最后执行特定逻辑，如清理资源

## 抛出异常

使用`throw`关键词抛出异常

## 自定义异常

在大型项目中，我们会定义一套异常继承体系。

首先自定义一个`BaseException`，然后继承这一根异常，定义其他异常。

`BaseException`本身通常继承自`RuntimeException`。

## `NullPointerException` (NPE)

为避免 NPE，可以

- 使用空数据，而非`null`。例如，返回一个空数组，或空字符串

- 使用`Optional<T>`

## 断言

`assert`

## 日志（log）

### `Java.util.logging`

### Common Logging

### Log4j

### SLF4J 和 Logback

## 杂项

- 如果 catch 和 finally 都抛出了异常，只有 finally 的异常会被处理，catch 的异常会被屏蔽（Suppressed Exception）。不推荐这么做。
