---
date: '2025-04-21T19:50:00-04:00'
draft: false
title: '01 Build Java Project from Scratch'
mathjax: false
---

<!-- TODO:

- [ ] Add Java Bytecode pseudocode here and there -->

In this post, we will build and run Java projects in command-line, with no reliance on an IDE. By diving into the nitty-gritty details, we would have a better understanding of what an IDE is doing behind the scene when you click that shiny "run" button.

To follow alone with the examples in this section, one should have JDK installed in their system, and have it accessible from command-line. If you don't know what that mean, you could refer to [this blog](https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-22-04#step-1-installing-java) that explains step-by-step how to setup Java. It's written for Ubuntu, but the process is almost the same for other OS.

Note that

- This post only discuss what JDK offers. Later posts will cover non-official (but useful) tools like Maven, JUnit, etc.

- This post won't cover language details such as "how to write a for loop", or "how to use ArrayList`.

## Single File, Single Class

Code for this example is in `single_class/`

First, let's look at how a single java source code file is processed.

Java source code is compiled by a Java compiler into platform-independent bytecode, and the Java Virtual Machine (JVM) can execute the bytecode.

- Bytecode to JVM is what machine code to CPU.

When running a java program, the entry point is always the public `main` **method** of a public class, which must be compiled from a file with exactly the same name as the class. To be more accurate, the entry point must be a method of this signature

```java
public static void main(String[] args);
```

- `public`: the method is a public method. Other classes have access to this method.

- `static`: the method is a static method. It belongs to the class itself, not to the instances of the class. I.e. its output is independent of how the instance is initialized.

- `void`: the method returns nothing.

- `main`: name of the method

- `String[] args`: the method takes an argument named `args` of type `String[]`, i.e. array of `String`. This is the list of command-line arguments passed to the java program.

For example, we have a `HelloWorld.java` file that defines a public class `HelloWorld` which has a `main` method as follows

```java
// file: single_class/HelloWorld.java

public class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello World!");
  }
}
```

We can compile this file with the Java compiler using

```bash
javac HelloWorld.java
```

This would generate a `HelloWorld.class`, which contains the Java bytecode of the `HelloWorld` class.

We can then execute the program with JVM using

```bash
java HelloWorld
```

This command tells the JVM to load the class named `HelloWorld`. JVM will search for the compiled file `HelloWorld.class` within a path called "class path", which by default is the current directory. When the file is found, JVM will load it into memory and execute the `main` method defined in the class.

## Packages (Multiple Files, Multiple Classes)

In this section, we will discuss the case where we want to modularize our code by having multiple classes across multiple files.

### What is package?

To achieve this goal, we need to learn about **package**.

In Java, a **package** is a **namespace** - a way to group related classes together and avoid name collisions. This is similar to namespaces in C++, or modules in Python, or even directories in file systems.

To define a package, we need to work on two sides

- Source Code

  In the source code, we must declare the package at the **top of the file** before any class definition

  ```java
  package com.example.util;

  public class MathUtils {
      public static int doubleIt(int x) {
          return x * 2;
      }
  }
  ```

  This tells Java

  > the class `MathUtils` belongs to the package `com.example.util`

- Folder Structure

  The **folder structure must match the package definition**.

  For example, the `com.example.util.MathUtils` class above must be defined in the folder

  ```text
  <BASE_DIR>/com/example/util/MathUtils.java
  ```

  It doesn't matter what the `<BASE_DIR>` is, so long as the subfolder matches the package definition.

  - that is, we can also define the package as `example.util` in the source code of `MathUtil.java`.

### A full example of package

Code for this example is in `multi_class/`

Here is a more interesting example where we have a main class that invokes classes from other packages. This is what you will likely be using in most java projects.

```java
// multi_class/src/com/example/service/Greeter.java
package com.example.service;

public class Greeter {
    public static void sayHello() {
        System.out.println("Hello from Greeter!");
    }
}
```

```java
// multi_class/src/com/example/util/MathUtils.java
package com.example.util;

public class MathUtils {
    public static int doubleIt(int n) {
        return n * 2;
    }
}
```

```java
// multi_class/src/com/example/app/MainApp.java
package com.example.app;

import com.example.util.MathUtils;
import com.example.service.Greeter;

public class MainApp {
    public static void main(String[] args) {
        Greeter.sayHello();
        int doubled = MathUtils.doubleIt(21);
        System.out.println("Doubled: " + doubled);
    }
}
```

Here, we have a `MainApp` class that contains the `main` method. This classes uses classes from other packages, that is, `MathUtils` from `com.example.util`, and `Greeter` from `com.example.service`.

To compile everything into byte code, we can use

```bash
javac -d target $(find src -type f -name "*.java")
```

We use `-d` to specify the output folder of the class files. The `$(find src -type f -name "*.java")` means to compile all files named `*.java` within the subfolder of `src/`.

For source code files of this folder structure

```text
multi_class/
├── Makefile
└── src
    └── com
        └── example
            ├── app
            │   └── MainApp.java
            ├── service
            │   └── Greeter.java
            └── util
                └── MathUtils.java
```

The command above would compile them into class files of this folder structure

```text
multi_class/
└── target
    └── com
        └── example
            ├── app
            │   └── MainApp.class
            ├── service
            │   └── Greeter.class
            └── util
                └── MathUtils.class
```

To execute the `main` method of `MainApp` class, we can use

```bash
java -cp target/ com.example.app.MainApp
```

Here, we specify the class path using `-cp` argument to be `target/` folder, and we identify the main class by specifying both package name `com.example.app` and class name `MainApp`.

The execution result would be

```text
Hello from Greeter!
Doubled: 42
```

To be more organized, we can even define a Makefile that automates the build and execution process as follows

```Makefile
# where we store source code
SRC_DIR=src

# where the compiled class file should reside
BIN_DIR=bin

# find the ".java" source code files for all the classes
CLASSES=$(shell find $(SRC_DIR) -name "*.java")

# define the entry point of the program
MAIN_CLASS=com.example.app.MainApp

.PHONY: all run clean

build:
 @mkdir -p $(BIN_DIR)
 javac -d $(BIN_DIR) $(CLASSES)

run: all
 java -cp $(BIN_DIR) $(MAIN_CLASS)

clean:
 rm -rf $(BIN_DIR)
```

In later section, we will learn about more mature build tools like Maven or Gradle. They offer more advanced features than our handwritten Makefile, such as management of third-party library. However, in terms of the build process, they are essentially doing the same thing as this Makefile.

## Packaging

To make it easier to distribute our compiled program, say, upload it to an instance on the cloud, we can **package all class files into a `.jar` file**. `.jar` stands for **Ja**va **A**rchive. It is the standard way to distribute Java applications.

### What is JAR?

A `.jar` file is a **zip-compressed archive** that contains

- `.class` files

- metadata

  E.g. a file that defines the entry point, i.e. the path to a class whose `main` method we should invoke when we "execute" the `.jar` file.

- resources (optional)

  E.g. image, audio. Think of Minecraft mod where textures are packaged within the mod's `.jar` file.

### Package into JAR and Execute the JAR

Code for this example is in `packaging/`

We will reuse the example from the section above. We first compile all source code into `.class` files. To reiterate, we will have the following folder structure after the compilation:

```text
packaging/
└── target
    └── com
        └── example
            ├── app
            │   └── MainApp.class
            ├── service
            │   └── Greeter.class
            └── util
                └── MathUtils.class
```

Now, we can follow these steps to package everything into a `.jar` file.

1. Create a Manifest file

  This file tells JVM which class has the `main()` method.

  ```Manifest
  // ./manifest.mf
  Main-Class: com.example.app.MainApp

  ```

  > Note: This file must end with a newline.

2. Package into `.jar`

  ```bash
  jar cfm target/app.jar manifest.mf -C target .
  ```

  Explanation:

- `c`: **c**reate

- `f`: specify output **f**ile

- `m`: include a **m**anifest

- `-C target .`: change directory to `target/` and include everything inside in the `.jar` file

3. Execute the `.jar`

  ```bash
  java -jar target/app.jar
  ```

Again, we can automate this process in the Makefile by adding the additional target `package` and `run-jar` into our earlier Makefile.

```Makefile
SRC_DIR=src
TARGET_DIR=target
JAR_FILE=app.jar
MAIN_CLASS=com.example.app.MainApp
CLASSES=$(shell find $(SRC_DIR) -name "*.java")

# Path to manifest file
MANIFEST_FILE=manifest.mf

# To keep things clear, we store both manifest file and jar file in target/
JAR_PATH=$(TARGET_DIR)/$(JAR_FILE)
MANIFEST_PATH=$(TARGET_DIR)/$(MANIFEST_FILE)

.PHONY: build run package run-jar clean

build:
 @mkdir -p $(TARGET_DIR)
 javac -d $(TARGET_DIR) $(CLASSES)

run: build
 java -cp $(TARGET_DIR) $(MAIN_CLASS)

package: build
 # we create the manifest file on the fly using our definition of main class
 echo "Main-Class: $(MAIN_CLASS)" > $(MANIFEST_PATH)
 jar cfm $(JAR_PATH) $(MANIFEST_PATH) -C $(TARGET_DIR) .

run-jar: package
 java -jar $(JAR_PATH)

clean:
 rm -rf $(TARGET_DIR)
```

## Built-in Libraries and JDK

### Built-in Libraries

First, let's clarify two terms: application and library. This is not formal, but typically,

- An application is a java program that has an entry point. It's meant to be executed JVM directly.

- A library is a set of Java classes. It is typically organized as a single package and packaged as a `.jar` with no entry point. It's meant to be used by other programs.

Java provides a list of built-in libraries, such as the `System.out.println` we used in our program above that print stuff on the screen.

You could simply import built-in libraries in your code and use them. For example,

```java
import java.util.ArrayList;
import java.util.Scanner;

public class Demo {
    public static void main(String[] args) {
        // Class representing an array
        ArrayList<String> names = new ArrayList<>();
        names.add("Alice");
        names.add("Bob");

        // Read from stdin
        Scanner scanner = new Scanner(System.in);
        System.out.print("Your name? ");
        String name = scanner.nextLine();

        System.out.println("Hello, " + name + "! Here's the list: " + names);
    }
}
```

I won't go into details in this post about built-in libraries. The best way to learn them is always by reading the official documentation and by using it in your code. For different versions of Java, the official doc is at

```text
https://docs.oracle.com/javase/<Java Version>/docs/api/index.html
```

For example, the doc for Java 8 is at [https://docs.oracle.com/javase/8/docs/api/index.html](https://docs.oracle.com/javase/8/docs/api/index.html)

### JDK

The built-in libraries of Java are provided by the JDK itself, more specifically, by JRE.

JDK means Java Development Kit. It is a complete toolkit for **developing** Java applications. JRE is Java Runtime Environment. It provides everything we need for **running** Java applications.

JDK consists of

- The Java compiler `javac`

- The Java debugger `jdb`

- Tools like `jar`, `javadoc` (), `javap` ()

  - `javadoc`: Generates HTML pages of API documentation from Java source files.

  - `javap`: Disassembles one or more class files.

- JRE

  JRE consists of

  - JVM

  - Core Java class libraries, i.e. the built-in libraries

  Note that JRE is a collection of files that is required to **run** Java programs, not develop them. Thus, it does not include things like compiler, debugger, or other tools, which are only needed when developing Java program.

## Third-Party Libraries

### Build a Java Application that Depends on Third-Party Libraries

Code for this example is in `third_party_library/`

Most of the time we would want to use a third-party library in our project, i.e. a collection of pre-written Java classes and methods created by someone else, which you can reuse in your own applications.

As we mentioned in the last section, a java project is distributed using `.jar` format. This applies to third-party library as well. The creator of a library will package the library into a single `.jar` file, and the user of library could simply download the `.jar`, and reference it in some way during the execution of the java program.

In this section, we will use the `Gson` library in a simple project. Citing from the official GitHub repo, `Gson` is

> A Java serialization/deserialization library to convert Java Objects into JSON and back

We will create a class `com.example.model.Person`, instantiate a `Person` object in our `com.example.app.MainApp`'s `main` function, and serialize the `Person` object into a Json string using `Gson`.

To achieve this, we need to both modify the source code and include the dependency during compilation and execution.

1. Modify the source code

    ```java
    // third_party_library/src/com/example/model/Person.java
    package com.example.model;

    public class Person {
        private String name;
        private int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }
    }
    ```

    ```java
    // third_party_library/src/com/example/app/MainApp.java
    package com.example.app;

    import com.example.model.Person;
    import com.google.gson.Gson;

    public class MainApp {
        public static void main(String[] args) {
            Person p = new Person("Alice", 30);
            Gson gson = new Gson();
            String json = gson.toJson(p);
            System.out.println("JSON: " + json);
        }
    }
    ```

2. Add the `Gson` dependency

    This simply means downloading the jar of `Gson` somewhere on your system. To make things organized, we will download the jar to `lib/`. We will use `gson-2.10.1` from Maven's repo.

      ```bash
      mkdir lib
      cd lib
      wget https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar
      ```

3. During compilation, reference `Gson` jar with `-cp` parameter

    To recap, `-cp` stands for **c**lass**p**ath. It tells `javac` or `java` where to search for a specific class. Arguments to `-cp` can either be path to (or folder containing) `.class` file, or `.jar` file. If multiple paths are provided, they should be separated by `:`.

    Note that compiling your code does not bundle Gson jar into your project —`javac`` simply generates .class files for your own classes. Then why do we need to provide classpath at compile time?

    This is because the java compiler need to access `.class` file in the Gson library to understand the method and types you are using. This information allows the compiler to check for correctness of code. For example, it needs to know if the method `Gson.toJson` exists, and if so, what is its signature.

    The command to compile our project is

    ```bash
    javac -cp lib/ -d target $(find src -type f -name "*.java")
    ```

4. During execution, reference `Gson` jar with `-cp` parameter

    Again, we append the `Gson` jar to the class path

    ```bash
    java -cp target:lib/gson-2.10.1.jar com.example.app.MainApp
    ```

    The output should be

    ```text
    JSON: {"name":"Alice","age":30}
    ```

    > Sidenote: the order we append to classpath matter: the class is search from left to right. This means, if we pass in `-cp <DIR1>:<DIR2>`, and both `<DIR1>` and `<DIR2>` contains a class `X`, any usage of class `X` will resolve to the class `X` in `<DIR1>`.

Again, the entire process can be automated using a Makefile.

```Makefile
# Directories
SRC_DIR=src
LIB_DIR=lib
TARGET_DIR=target

# Files and classes
MAIN_CLASS=com.example.app.MainApp
GSON_JAR=$(LIB_DIR)/gson-2.10.1.jar
CLASSPATH=$(GSON_JAR):$(TARGET_DIR)

# Find all .java source files
SOURCES=$(shell find $(SRC_DIR) -name "*.java")

.PHONY: build run clean

# Compile all Java source files
build:
 @mkdir -p $(TARGET_DIR)
 javac -cp $(GSON_JAR) -d $(TARGET_DIR) $(SOURCES)

# Run the main class
run: build
 java -cp $(CLASSPATH) $(MAIN_CLASS)

# Remove compiled files
clean:
 rm -rf $(TARGET_DIR)
```

Now, we have cover the basic of how an external package is included in a Java project. That said, there are much, much more to the management of third-party libraries. Although we won't cover them in this section, it's nice to know what we didn't cover

- How to specify dependency efficiently

    Currently, the dependency is hardcoded in the Makefile, and you still need to manually download the jar file. You could further automate this process by using another config file that lists all the dependencies, and write a custom script to do the downloading. In fact, this is exactly what `pom.xml` is for in Maven.

- Where to download dependency

- How to manage dependency conflict

- What about dependency of dependency?

- How to do things platform-agnostic

    We use `find` to find all class files. This works on Linux and MacOS, but won't work on Windows.

- ...

Maybe I will discuss all these in later section that talks about Maven, and try to build our own Maven.

### Package a Java Application that Depends on Third-Party Libraries

To package everything, including the Gson jar, into a single jar, we can unpack the jar and move all the unpacked class files into `target/`, and package everything in jar the same way as before. This kind of all-encompassing jar is usually called a "fat jar", or "uber jar".

```bash
# 1. Compile
javac -cp lib/gson-2.10.1.jar -d target $(find src -name "*.java")

# 2. Unpack gson into target. The actual class files will be in target/com/google/gson/
cd target && jar xf ../lib/gson-2.10.1.jar && cd ..

# 3. Create manifest
echo "Main-Class: com.example.app.MainApp" > manifest.txt

# 4. Package into single jar
jar cfm app.jar manifest.txt -C target .

# 5. Run it
java -jar app.jar
```

This is also roughly what happens internally when you use a packaging tools like `maven-shade-plugin`.

## Building A Library Package

Sometimes, you may need to build your own library, or tweak others libraries to fit your need. In this section, we will build a reusable library from scratch, and use it in another application. We will modularize our code, and save the library and the application in two separate directories, although they will share part of the namespace.

Using knowledge from sections above, we can achieve this goal by

1. Write the library and package it into a Jar without entry point

2. Wirte the application and provide the library jar in class path during compilation and execution

    We may also package our application with the library into a fat jar.

You could do this by yourself as an exercise. To make things simple, you could simply work on the example from the section "Packages". You could separate the `MainApp` from other classes, and have something like this

```text
custom_library/
├── my-app
│   └── src
│       └── com
│           └── example
│               └── myapp
│                   └── MainApp.java
└── my-lib
    └── src
        └── com
            └── mylib
                ├── service
                │   └── Greeter.java
                └── util
                    └── MathUtils.java
```

The `MainApp.java` defines the class `MainApp` that locates at the package `com.example.myapp.MainApp`, and it would import from `com.mylib.service.Greeter` and `com.mylib.util.MathUtils`.

## Misc

This section is a collection of command-line tools that comes in handy when working with a Java project.

- `javap`: Disassemble a `.class` file.

    E.g. Given the java file 

    ```java
    // file: HelloWorld.java
    public class HelloWorld {
        public static void main(String[] args) {
            System.out.println("Hello World!");
        }
    }
    ```

    We can compile it with `javac HelloWorld.java`, and obtain a `HelloWorld.class` file.

    We can also disassemble the `HelloWorld.class` file to obtain the package, protected and public fields, and methods of the classes. Running `javap HelloWorld.class`, we get

    ```text
    Compiled from "HelloWorld.java"
    public class HelloWorld {
    public HelloWorld();
    public static void main(java.lang.String[]);
    }
    ```