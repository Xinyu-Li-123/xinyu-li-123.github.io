---
date: '2025-02-28T20:20:02-05:00'
draft: false
title: 'Bash Cheatsheet'
---

## Bash Concepts

### Variables

```bash
foo1=bar
foo2="bar bar bar"
foo3="bar bar bar"
echo $foo1
echo $foo2
echo $foo3
```

### Quotes

Quotes in bash can be a bit confusing:

- no quote: evaluate all special characters

- single quote: pure string, prevent all evaluation

- double quote: formatted string, only retain the special meaning of `$`, `\`, and ```.

  - `$`: evalaute an expression, e.g.

    ```bash
    echo "$foo"
    echo "$(date)"
    ```

  - `\`: escape character, only escapes `$`, ```, `"`, `\`, or newline `n`

- backtick: *deprecated!*

Below is an example showing their difference

```bash
foo="bar1 bar2"
echo $foo           # "bar1 bar2" is printed
echo '$foo'         # "$foo" is printed
echo "$foo"         # "bar1 bar2" is printed

echo ":)"           # ":)" is printed
echo :)             # bash: syntax error near unexpected token `)'

```

Just to make things worse, here is another example showing code you should never write

```bash
'echo' Huh? $foo    # "Huh? bar1 bar2" is printed
```

### Control Flow

We only cover the commonly used ones.

while loop: while `test-commands` has a zero exit status, execute `consequent-commands`

```bash
while test-commands; 
    do consequent-commands;
done

# download segments of video until all are downloaded (which will raise an error), with 1s gap
while ./download_video_segment;
    do sleep 1
done

# An infinite loop
while true
    do echo ":)"
done
```

until loop: while `test-commands` has a non-zero exit status, execute `consequent-commands`

```bash
until test-commands; do 
    consequent-commands;
done

# brute-force password with 1s gap
until ./guess_password; do 
    sleep 1
done
```

for loop:

```bash
for name [ [in [word1 word2 ...]] ; ] do 
    commands; 
done

for (( init_expr; stop_conditiion_expr; update_expr )); do 
    commands; 
done

# simple for loop: print a,b,c,d in four lines
for char in a b c d; do 
    echo $char
done

# print from 1 to 10, left-right-inclusive
# seq is a command to print a sequence of numbers
for i in $(seq 1 10); do
    echo $i
done

# print from 1 to 10, left-right-inclusive
for (( i=1; i<=10; i++)); do
    echo $i
done

# echo all input args, each on a line
for arg in $@; do 
    echo "arg: $arg"
done
```

if statement:

```bash
if condition; then
    commands
[elif condition; then
    consequent-commands]
[else commands]
fi
```

The `condition` can be

- a command, e.g. `./myprogram`, `true`

- a `[[...]]``.

  This is an alias of the Bash `test` command. `[[...]]` is the same as `test ...`. E.g.

  ```bash
  if [[ 3 -lt 10 ]]; then
    echo wow
  else
    echo ehh
  fi
  ```

- a `[...]`.

  This is also an alias of test, except this one is alias of POSIX `test` command, while `[[...]]` is an alias of the more powerful Bash `test`. `[[...]]` is recommended b/c it also supports reges operator and has safer variables (prevent word splitting).

### Arguments

- `$0`: Name of Script

- `$1`-`$9`: Argument #1 to #9 to the script.

- `$@`: All the arguments

- `$#`: Number of arguments

- `$?`: Return code of the previous command

- `$$`: Process identification (PID) of the current script

- `!!`: Entire last command, including arguments.

  Common usecase: if `vi secret_file.txt" failed due to missing permission, you can do`sudo !!` to execute the last command with sudo.

- `$_`: Last argument from the last command. Don't know why we need this...

### Functions

```bash
myfunc() {
        echo "Calling myfunc with $# argument(s): $@"
}

myfunc
# output: Calling myfunc with 0 argument(s): 
myfunc aa bb
# output: Calling myfunc with 2 argument(s): aa bb
```

### Common Pitfalls

- `foo = bar` is **incorrect** if you want to create a variable named `foo`. This will be intepreted as calling a command named `foo` :/

  Space is generally used as separator of arguments. Below is a similar example

- Use `"$(expr)"`, instead of `"$expr"`, to evaluate an expression and use the output as string. This is better b/c it allows the use of space character in the expression.

  ```bash
  >>> echo "example: $(echo "hello world" | wc)"
  example:       1       2      14
  >>> echo example: $(echo "hello world" | wc)
  example:  "hello world" | wc
  ```

## Examples of Bash Script

If you want to solidate your understanding of bash syntax, here are some practice problems that can be solved by a bash script.

### macro-and-polo

Write bash functions marco and polo that do the following. Whenever you execute marco the current working directory should be saved in some manner, then when you execute polo, no matter what directory you are in, polo should cd you back to the directory where you executed marco.

```bash
#!/bin/bash

TMP_FILE=/tmp/cmd.txt

macro () {
    pwd > $TMP_FILE
}

polo() {
    # return if cd fail
    cd "$(cat $TMP_FILE)" || return
}
```

### Run until error

There is a buggy script named `buggy.sh`. It has a very low chance of throwing an error. Write a script to run the `buggy.sh` until error occur, save both normal and error output to a file and print it in the end.

Note: `((...))` is arithmetic expression in bash

```bash
i=0
while ./buggy.sh 2>&1 >> output.tmp; do 
    ((i=i+1))
done

echo "Number of success run before first failure: $i"
echo "Output:"
cat output.tmp
rm output.tmp
```
