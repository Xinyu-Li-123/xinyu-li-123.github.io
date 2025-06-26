---
date: '2025-02-28T20:20:02-05:00'
draft: false
title: 'Bash Cheatsheet'
---

For details, see the [bash reference manual](https://www.gnu.org/software/bash/manual/html_node/index.html)

## Commonly Used Unix Utils 

### File Compression / Decompression

We can compress file into either `tar.gz` or `zip`. `tar.gz` works better for Linux/Unix b/c it retains perrmissions, older version of zip doesn't preserve it.

- `.tar.gz`

  The files are first archived into a single `.tar` file using tar, then gzip is used to compress the single file into `.gz` format.

- `.zip`

  zip compresses each file separately, then archives them together.

Compress multiple files / folders into one `.targ.gz`

```bash
# [c]reate an archive and write it to a [f]ile:
tar czf output.tar.gz file1 folder2 file3 folder4 ...
```

Extract a `.tar.gz` into the current directory

```bash 
tar xvf output.tar.gz
```

Extract a `.tar.gz` into a target directory

```bash 
tar xvf output.tar.gz --directory target/
```

List the content of a tar / tar.gz file 

```bash 
# Lis[t] the contents of a tar [f]ile [v]erbosely:
tar tvf output.tar.gz
```


## Commonly Used Bash Commands / Snippets / Tricks

### Linter for Shell Scripts

See [ShellCheck](https://github.com/koalaman/shellcheck).

### Do something when a program fail

```bash
for file in "$@"; do
    grep foobar "$file" > /dev/null 2> /dev/null
    # When pattern is not found, grep has exit status 1
    # We redirect STDOUT and STDERR to a null register since we do not care about them
    if [[ $? -ne 0 ]]; then
        echo "File $file does not have any foobar, adding one"
        echo "# foobar" >> "$file"
    fi
done
```

### Chain of commands

To chain multiple commands, we can

- use `;` to chain commands, and execute commands in sequence. `;` only separate commands.

- use the AND operator `&&` to chain commands. Shortcircuit. Execute next if cur returns nonzero.

    ```
    >>> true && echo "foo"
    foo
    >>> echo "shortcircuit!" && false && echo "foo"
    shortcircuit!
    ```

- use the OR operator `||` to chain commands. Shortcircuit. Execute next if cur returns zero.

    ```
    >>> false && echo "foo"
    foo
    >>> echo "shortcircuit!" && true && echo "foo"
    shortcircuit!
    ```

### Get output of a command as a variable

```bash
>>> export ans=$(echo "1+1=$(python -c "print(1+1)")")
>>> echo $ans
1+1=2
```

### Generate similar argumnets (file1, file2, file3, ...)

```bash
upload_image.py {mountain,sea}.{png,jpg}
```

### Managing an AppImage on Ubuntu + GNOME

#### What is AppImage

An AppImage to Linux is what exe is to Windows. It allows you to run an application on all common Linux distributions by simply executing an `myapp.AppImage` file. All you needs are

```bash
$ chmod a+x myapp.AppImage
$ ./myapp.AppImage
```

AppImage features

- no installation: just download and run

- self-contained: includes all dependencies

- Doesn't modify the system: everything needed is in the AppImage, and it can be runned without `sudo`

- Portable: just one file

However, there are some tradeoff

- no shared dependencies: this is not necessarily a bad thing. but it is a tradeoff.

- no automatic update: you must manually download the new versions and replace it. Some AppImage supports `appimageupdate` though.

- need to manually integrate into the system: this is just unavoidable for a portable format like AppImage.

#### Install an AppImage

Sure, you can just execute the AppImage like any other program, but what if I want to use it as if it was installed by a package manager?

We use [Krita](https://krita.org/en/) as an example. Krita is a professional free and open source painting program, free alternative to Photoshop, SAI, or CSP.

1. Download the AppImage

    ```bash
    # download to a file named krita.AppImage
    wget --output-document krita.AppImage https://download.kde.org/stable/krita/5.2.9/krita-5.2.9-x86_64.AppImage
    ```

2. Place the AppImage in `~/Application/krita/`, and make it executable

    ```bash
    mkdir ~/Application/krita
    mv krita.AppImage ~/Application/krita/
    cd ~/Application/krita
    chmod +x krita.AppImage
    ```

3. Extract the app icon from the AppImage, so that we can create a desktop entry for it later.

    This can be done in several ways. One way I find convenient is to first mount the AppImage somewhere in `/tmp` folder, then copy the icon.

    ```bash
    # this will mount krita to /tmp/.mount_kritaXXXXX
    ./krita.AppImage --appimage-mount

    # the command above will block the current bash shell
    # so open another shell to run this
    cp /tmp/.mount_kritaXXXXX/krita.png .
    ```

    The exact path to icon in the AppImage may differ for diff apps, but the logic is the same.

4. Create a desktop file, so that it's accessible in the application menu

    Create a desktop file

    ```bash
    touch ~/.local/share/applications/krita.desktop
    ```

    Add the following to the file

    ```ini
    [Desktop Entry]
    Name=MyApp
    Exec=/home/<username>/Applications/krita/krita.AppImage
    Icon=/home/<username>/Applications/krita/krita.png
    Type=Application
    Categories=Utility;
    ```

    Update the GNOME's application database

    ```bash
    update-desktop-database ~/.local/share/applications/
    ```

Now, you should be able to see the Krita icon in the GNOME application menu!

#### Update and Delete an AppImage

To update the AppImage, simply replace the AppImage file with the newer version one

```bash
cd ~/Applications/krita
rm krita.AppImage
wget --outut-document krita.AppImage "<link to AppImage of newer version>"
# don't forget to make the new AppImage exectuable
chmod +x krita.AppImage
```

To delete an AppImage, simply remove the entire app folder and the desktop entry
```bash
rm -rf ~/Applicatioins/krita
rm ~/.local/share/applications/krita.desktop
update-desktop-database ~/.local/share/applications/
```

## Commonly Used Git Operations

### Stash all changes and Pop them later

`git stash` allows you to temporarily shelves your changes in the working directory, so you can work on something else, and come back to them later. This is useful if you want to switch branches or pull changes from a remote repository without committing your current changes.

By default, **tracked files** and **staged chagnes** (added by `git add`) are stashed. If specified, **untracked and ignored files** can also be stashed.

Below are commonly used commands related to stash

- Normal stashing
    
    ```bash
    git stash
    ```

- Stash untracked files

    ```bash
    git stash -u
    ```

- Stash untracked and ignored files

    ```bash
    git stash -a
    ```

- List stashes

    ```bash
    git stash list
    ```

    This will print something like this 

    ```
    stash@{0}: On main: second stash, including untracked files
    stash@{1}: On main: first stash
    ```

    Note that `stash@{1}` is created earlier than `stash@{0}`, though its number is larger. This is because stash is maintained a stack, LIFO.

- Apply latest stash without removing it

    ```bash
    git stash apply
    ```

- Apply specific stash

    ```bash
    git stash apply stash@{0}
    ```

- Apply and drop latest stash

    ```bash
    git stash pop
    ```

- Apply and drop specific stash

    ```bash
    git stash pop stash@{0}
    ```

- Drop specific stash

    ```bash
    git stash drop stash@{0}
    ```

- Clear all stashes

    ```bash
    git stash clear
    ```

- Create a stash with a message

    ```bash
    git stash push -m "your message here"
    ```

- Stash only staged changes

    ```bash
    git stash --keep-index
    ```

- Stash only unstaged changes

    ```bash
    git stash --patch
    ```

    

## Concepts

<!-- 
```bash
```
 -->
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

  Common usecase: if `vi secret_file.txt" failed due to missing permission, you can do `sudo !!` to execute the last command with sudo.

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

## Common Pitfalls

- `foo = bar` is **incorrect** if you want to create a variable named `foo`. This will be intepreted as calling a command named `foo` :/

  Space is generally used as separator of arguments. Below is a similar example

- Use `"$(expr)"`, instead of `"$expr"`, to evaluate an expression and use the output as string. This is better b/c it allows the use of space character in the expression.

  ```bash
  >>> echo "example: $(echo "hello world" | wc)"
  example:       1       2      14
  >>> echo example: $(echo "hello world" | wc)
  example:  "hello world" | wc
  ```

## Practice

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
