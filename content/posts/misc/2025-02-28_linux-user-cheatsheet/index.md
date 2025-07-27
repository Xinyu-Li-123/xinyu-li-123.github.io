---
date: '2025-02-28T20:20:02-05:00'
draft: false
title: 'Linux User Cheatsheet'
---

This is a cheatsheet for people who use Linux, specifically Ubuntu + Gnome, for their day-to-day OS: you write code, play games, or even draw on a Linux computer. This means, besides terminal stuff, we will also focus on better desktop usage.

## File Compression / Decompression

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

## Linter for Shell Scripts

See [ShellCheck](https://github.com/koalaman/shellcheck).

## Do something when a program fail

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

## Chain of commands

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

## Get output of a command as a variable

```bash
>>> export ans=$(echo "1+1=$(python -c "print(1+1)")")
>>> echo $ans
1+1=2
```

## Generate similar argumnets (file1, file2, file3, ...)

```bash
upload_image.py {mountain,sea}.{png,jpg}
```

## Managing an AppImage on Ubuntu + GNOME

### What is AppImage

An AppImage to Linux is what exe is to Windows. It allows you to run an application on all common Linux distributions by simply executing an `myapp.AppImage` file. All you needs are

```bash
chmod a+x myapp.AppImage
./myapp.AppImage
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

### Install an AppImage

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

### Update and Delete an AppImage

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
