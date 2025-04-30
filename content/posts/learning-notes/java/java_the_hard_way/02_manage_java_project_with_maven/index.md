---
date: '2025-04-28T17:50:56-04:00'
draft: false
title: '02 Manage Java Project with Maven'
mathjax: false
---

To manage a Java project, and to collaborate with others on a Java project, we need to learn how to use Maven. Maven is a build automation and project management tool for Java projects.

> Note: We assume the reader has already finished the [Maven in 5 minutes](https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html) tutorial, which walks you through the usage of Maven without diving into how it works.

This post does not meant to be a detailed reference. Instead, it aims to explain what is going on under the hood in our daily usage of Maven. For example, what exactly happen when you run `mvn package`: what got executed, where is the execution logic stored, and where is that logic defined?

## POM (Project Object Model)

A POM is an XML file that defines a Maven project's structure and build configuration.

### Artifact

An artifact is a packaged unit such as `.jar` or `.war`. In `pom.xml`, an artifact is uniquely identified by three consecutive tags in `pom.xml`: `groupId`, `artifactId`, and `version`, which is abbreviated as GAV.

Examples:

- Your project is an artifact. It can be packaged into a jar, and thus be identified by GAV.

  ```xml
  <groupId>com.cloudcomputing.samza</groupId>
  <artifactId>nycabs</artifactId>
  <version>0.0.1</version>
  ```

- A third-party library like `junit` is distributed as a jar file. It can also be represented as an artifact in `pom.xml`, and identified by GAV.

  ```xml
  <dependencies>
      <dependency>
          <groupId>junit</groupId>
          <artifactId>junit</artifactId>
          <version>4.12</version>
      </dependency>
  </dependencies>
  ```

We can also optionally append additional tags to GAV. Below is the full list of optional tags

- `packaging`: Used in the project's artifact to specify the output type, e.g. `jar`.

<!-- - `classifier`: Applied to dependency. Distinguish artifacts w/ same GAV but different content, e.g. `sources`, `dist`, `javadoc`. -->
- `classifier`: TODO:

- `scope`: TODO:

- `type`: TODO:

- `optional`: TODO:

### Organization of Artifacts

Artifacts (in specific, GAVs) are organized inside different tags based on their roles.

- `<project>`

  Def:  
  The root element of a Maven POM file that defines the project's identity, versioning, and coordinates as an artifact.

  Artifact role:  
  The artifact being built (e.g., a JAR or WAR).

  Fully qualified XML snippet:

  ```xml
  <project xmlns="http://maven.apache.org/POM/4.0.0"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
  </project>
  ```

- `<project.dependencies.dependency>`

  Def:  
  A section used to declare external libraries that the project depends on for compilation, testing, or runtime.

  Artifact role:  
  A library or external artifact required by your code.

  Fully qualified XML snippet:

  ```xml
  <project>
    <dependencies>
      <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-lang3</artifactId>
        <version>3.12.0</version>
      </dependency>
    </dependencies>
  </project>
  ```

- `<project.build.plugins.plugin>`

  Def:  
  Declares plugins that provide goals used during the build lifecycle phases (like compile, test, package).

  Artifact role:  
  A plugin artifact that provides build-time functionality (e.g., compiler, jar packager).

  Fully qualified XML snippet:

  ```xml
  <project>
    <build>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.8.1</version>
        </plugin>
      </plugins>
    </build>
  </project>
  ```

- `<project.build.pluginManagement.plugins.plugin>`

  Def:  
  Defines plugin versions and configurations that can be inherited or reused, but are not automatically applied unless explicitly declared.

  Artifact role:  
  Centralized plugin configuration (typically in a parent POM).

  Fully qualified XML snippet:

  ```xml
  <project>
    <build>
      <pluginManagement>
        <plugins>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
          </plugin>
        </plugins>
      </pluginManagement>
    </build>
  </project>
  ```

- `<project.reporting.plugins.plugin>`

  Def:  
  Declares plugins used to generate project documentation or reports, typically executed with the `site` lifecycle.

  Artifact role:  
  Tooling for generating HTML reports and documentation (e.g., license, dependency trees).

  Fully qualified XML snippet:

  ```xml
  <project>
    <reporting>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-project-info-reports-plugin</artifactId>
          <version>3.3.0</version>
        </plugin>
      </plugins>
    </reporting>
  </project>
  ```

## Lifecycle

### Plugin and Goal

To understand what **lifecycle** is, we need to first understand what **plugin** and **goal** are.

A **plugin** is an artifact. Physically, it's a JAR file downloaded into your local repository at `~/.m2/repository`. For example, the plugin `org.apache.maven.plugins:maven-compiler-plugin:3.8.1` is downloaded to `~/.m2/repository/org/apache/maven/plugins/maven-compiler-plugin/3.8.1/maven-compiler-plugin-3.8.1.jar`.

A **goal** is a class defined in the plugin's JAR file. This class implements the `org.apache.maven.plugin.Mojo` interface that comes with an `execute()` method. The exact signature of `execute()` is

```java
public void execute() throws MojoExecutionException, MojoFailureException
```

To execute a goal is to execute the `execute()` method of the goal class.

When referring to a goal, we typically don't use the name of the class. Instead, we use a logical name that is assigned to the class via annotation. For example, the `CompilerMojo` class in the `maven-compiler-plugin` plugin can compile the project into `.class` files in `target/classes`. This class is defined by

```java
@Mojo(name = "compile", defaultPhase = LifecyclePhase.COMPILE)
public class CompilerMojo extends AbstractMojo {
    public void execute() throws MojoExecutionException, MojoFailureException {
        // Real compilation logic here
    }
}
```

As you can see, we assign a logical name `compile` in the annotation `@Mojo` when defining the class `CompilerMojo`. We would refer to this goal as `compile` instead of `CompilerMojo`.

There are two ways to execute a goal in a plugin

- Manually invoked the goal

  This is typically used when the goal itself acts like a tool, e.g. format checker, linter, etc.

  One way to do this is via

  ```bash
  mvn [<plugin-prefix>:]<goal>`
  ```

  Here, plugin prefix is inferred

  - either from the plugin's `artifactId` by stripping `-maven-plugin` suffix, e.g. the plugin prefix of `versions-maven-plugin` is `versions`

  - or using a built-in list of well-known plugin prefixes, e.g. the plugin prefix of `maven-compiler-plugin` is `compile`

  A more conservative way is to use the fully-qualified name of the goal, i.e.

  ```bash
  mvn <groupId>:<artifactId>:<version>:<goal>
  ```

  For example, here is a popular plugin

  ```xml
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>versions-maven-plugin</artifactId>
  ```

  There is a goal named `display-dependency-updates` in that plugin. It scans your project and shows which dependency have newer version available.

  To execute this goal, we can run

  ```bash
  mvn versions:display-dependency-updates
  ```

  Or run this to avoid any ambiguity

  ```bash
  mvn org.codehaus.mojo:versions-maven-plugin:2.15.0:display-dependency-updates
  ```

- Attached the goal to a phase in a lifecycle

  We will discuss this in the next section.

### Lifecycle and Phase

A lifecycle is a sequence of phases. A phase consists of a label like `validate`, `compile`, `package`, and zero or more goals attached to it. To execute a phase is to execute all goals attached to the phase. When running a specific phase, Maven will execute all previous phases in order, and then execute the current phase.

As an example, here is the (simplified) default lifecycle:

```text
validate 
-> compile 
-> test 
-> package 
-> verify 
-> install 
-> deploy
```

And here is the binding between phases and goals in the default lifecycle:

| Phase     | Goal                        | Plugin                     | How it's attached         |
|-----------|-----------------------------|----------------------------|---------------------------|
| validate  | (none)        | –                          | You can attach custom     |
| compile   | compile                     | maven-compiler-plugin      | Bound by default          |
| test      | test                        | maven-surefire-plugin      | Bound by default          |
| package   | jar                   | maven-jar-plugin | Bound by default |
| verify    | (none)         | –                          | You can attach custom     |
| install   | install                     | maven-install-plugin       | Bound by default          |
| deploy    | deploy                      | maven-deploy-plugin        | Bound by default          |

> Note: there is no built-in goals in Maven core: every goal comes from a plugin, even the ones bundled with the Maven distribution, such as `compile`

For some phases, Maven will attach goals to them automatically. For other phases, there will be no goal attached to it unless we explicity do so. We will talk about how to manually attach goal to phase in next section.

### Attach Custom Goal from Custom Plugin to a Phase

TODO: Finish this part by writing a custom plugin with a custom goal, and attach it to the phase of a custom project.

Maven will attach goals to some phases by default. We can also attach custom goal to certain phases. For example, we can attach a custom goal defined in a custom plugin to the `validate` phase.

## Resource

TODO:

## External Dependencies

TODO:

Ref: [Intro to Dependency](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)
