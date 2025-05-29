---
date: '2025-05-27T21:40:00-04:00'
draft: false
title: '03 面向对象编程'
mathjax: false
---

## 方法

- `this`变量：

  在方法内部，可以使用一个隐含的`this`变量，它指向当前实例。`this`可用于规避命名冲突。

  ```java
  class Point {
    private double x;
    private double y;

    /**
      * Move the point by `x` and `y` along the x and y axis
      */
    public void translate(double x, double y) {
      this.x += x;
      this.y += y;
    }
  }
  ```

- 可变参数

  通过`type... name`可以让一个方法接受一个名为`names`、类型为`type[]`的数组。

  ```java
  class Group {
    private String[] names;

    public void setNames(String... names) {
      this.names = names;
    }
  }
  ```

  我们可以向`Group.setNames`传入任意数量的`String`

  ```java
  Group g = new Group();
  g.setNames("Foo")
  g.setNames("Foo", "Bar", "Baz")
  g.setNames()
  ```

  值得注意的是，无参数时，`names`会是一个空数组，而非`null`。`g.setNames()`后，`Arrays.equals(names, new String[]{})`

- 传参与引用

  Java的变量有两种类型：基本类型和引用类型

  - 基本类型

    byte, short, int, long, float, double, char, boolean

    基本类型变量的值就是实际的值，比如`int a = 3`，那么`a`的值就是`3`。

  - 引用类型

    类、接口、数组、`null`

    引用类型变量的值是引用对象在堆内存中的地址

    > 确切地说，引用类型变量的值是对堆中对象的引用，只要能一一对应到堆的地址就可以，不一定真的是地址本身。如果想的话，你也可以把`地址 + 0xdeadbeaf`作为引用变量的值，然后魔改一个JVM来转换到真实的地址，这些操作理论上仍然符合标准。
    >
    > 另外，引用类型变量和C++中的指针有所不同，引用只能指向堆中的合法对象（类似一个地址永远合法的指针），或者不指向任何对象（值为`null`）。
    >
    > 方便起见，我们就直接说引用类型变量的值是引用对象的地址了。

  Java传参永远是值传递，但引用类型变量的值是引用对象在堆内存上的地址，所以传入引用类型变量时，传入的虽然是引用类型变量的值，但却是引用对象的地址。这就导致了以下现象

  ```java
  class Team {
      List<String> members;

      Team(List<String> members) {
          this.members = members;
      }

      void printMembers() {
          System.out.println(members);
      }
  }

  public class Main {
      public static void main(String[] args) {
          List<String> sharedList = new ArrayList<>();
          sharedList.add("Alice");

          Team team = new Team(sharedList);
          team.printMembers();  // [Alice]

          // 外部代码修改了 sharedList
          sharedList.add("Bob");

          // 类内部的成员变量也“变”了
          team.printMembers();  // [Alice, Bob]
      }
  }
  ```

## 构造方法

创建实例时，通过`new`操作符会调用类的构造方法，用以初始化实例。

任何类都有一个默认的构造方法

```Java
class Person {
    public Person() {
    }
}
```

`int`字段默认为`0`，`boolean`字段默认为`false`，引用类型字段默认为`null`

如果自定义了一个构造方法，那么编译器不会生成默认的构造方法

```Java
class Person {
    public Person(String name) {
      this.name = name;
    }
}

public class Main {
    public static void main(String[] args) {
        Person person = new Person(); // 报错
    }
}
```

我们可以定义多个不同签名的构造方法

```Java
class Person {
    private String name;
    private int age;

    public Person() {
    }

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

public class Main {
    public static void main(String[] args) {
        Person p1 = new Person("Xiao Ming", 15); // 既可以调用带参数的构造方法
        Person p2 = new Person(); // 也可以调用无参数构造方法
    }
}
```

## 方法重载

我们可以重载（overload）方法，即“定义一系列同名但不同参数的方法”，如

```
class Vector {
  private double x;
  private double y;

  public Vector(double x, double y) {
    this.x = x;
    this.y = y;
  }

  public void increment(Vector other) {
    this.x += other.x;
    this.y += other.y;
  }

  public void increment(double x, double y) {
    this.x += x;
    this.y += y;
  }
}

public class Main {
    public static void main(String[] args) {
        Vector v1 = new Vector(3, 4);
        Vector v2 = new Vector(2, 2);
        v1.increment(v2);       // v1 = (5, 6)
        v1.increment(-2, -2);   // v1 = (3, 4)
    }
}
```

## 继承

```java
class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

class Student extends Person {
    // 不要重复name和age字段/方法,
    // 只需要定义新增score字段/方法:
    private int score;
}
```

`class Student extends Person`表示`Student`类继承`Person`类。一个子类只能继承一个父类，Java只支持单继承。所有类的都有一个名为`Object`的父类。

### 多继承与菱形问题

不支持多继承是为了避免菱形问题。允许多继承的情况下，假如有父类A，类B和C继承A，类D又继承B和C。如果A有方法`run()`，B和C都可以覆写这一方法，编译器无法判断D应该继承谁的`run()`方法。

```java
  A
 / \
B   C
 \ /
  D
```

### `protected`

子类无法访问父类的`private`字段，但可以访问父类的`protected`字段。

### `super`

`super`表示父类。我们可以使用`super.fieldName`，在子类中访问父类的字段。

子类的构造方法必须在第一行调用父类的构造方法，如果没有明确写出，编译器会自动加一句`super()`。也就是说，这段代码

```java
public Person(String name, int age, int score) {
  this.score = score;
}
```

会被转换成

```java
public Person(String name, int age, int score) {
  super();
  this.score = score;
}
```

由于父类`Person`没有签名为`public Person()`的构造方法，`Person`在实例化时会报错！

正确的做法应该是

```java
public Person(String name, int age, int score) {
  super(name, age);
  this.score = score;
}
```

### 阻止继承

`final`关键词可以让一个类不能被其他类继承

```java
public final class Rect extends Shape {...}
```

Java 15开始，可以使用`sealed`和`permits`定义允许用于继承的子类

```java
public sealed class Shape permits Rect, Circle, Triangle {...}
```

### 向上转型（upcasting）与向下转型（downcasting）

子类的实例可以被转换成父类，这叫向上转型；父类的实例不可以被转换成子类，这叫向下转型。这是因为子类比父类具有更多的方法和字段，父类能做的子类一定都能做。

```java
Person p = new Student();   // 可以，Student实例会被转换成Person类型
Student s = new Person();   // 不可以
```

我们可以使用`instanceof`关键词来判断一个变量是否是某个类型，或者某个类型的子类

```java
Person p = new Person();
Student s = new Student();
p instance of Person  // true
p instance of Student // false
s instance of Student // true
s instance of Person  // true
```

Java 14后，我们也可以强制转型

```java
if (obj instance of String) {
    Strings s = (String) obj;
}
```

## 多态（Polymorphism）

子类可以覆写父类的方法

```java
class Person {
    public void run() {
        System.out.println("Person.run");
    }
}

class Student extends Person {
    @Override
    public void run() {
        System.out.println("Student.run");
    }
}
```

两个方法的签名必须一致，否则就只是在重载（Overload），而非覆写。

### `@Override`

我们可以使用`@Override`的注解（annotation），明确表示一个方法在覆写父类的方法。此时编译器会进行检查，如果没有覆写就会报错。但这不是必须的。

### 多态

值得注意的是，即使向下转型，调用`run`时还是会调用被覆写的子类的`run`

```java
Person p = new Student();
p.run()   // "Student.run"
```

这种行为被成为多态，即“编译时仅保证签名确定，运行时动态决定调用的方法”：

- 父类被覆写的方法可以使用`super`调用，如

```java
class Student extends Person {
    @Override
    public void run() {
        System.out.println("Student.run");
        System.out.println("then,");
        super.run();    // "Person.run"
    }
}
```

### 覆写`Object`的方法

`Object`是所有类的父类。它有几个重要的方法可被用于覆写

- `toString()``：把实例输出为`String`；

- `equals()`：判断两个实例是否逻辑相等；

- `hashCode()`：计算一个实例的哈希值。

例如

```java
class Person {
    ...

    // 显示更有意义的字符串:
    @Override
    public String toString() {
        return "Person:name=" + name;
    }

    // 比较是否相等:
    @Override
    public boolean equals(Object o) {
        // 当且仅当o为Person类型:
        if (o instanceof Person) {
            Person p = (Person) o;
            // 并且name字段相同时，返回true:
            return this.name.equals(p.name);
        }
        return false;
    }

    // 用 Person.name 的 hash 作为 Person 的 hash 
    @Override
    public int hashCode() {
        return this.name.hashCode();
    }
}
```

### `final`

`final`关键词用处很多

- 用于方法，确保一个方法不会被覆写。

- 用于类，确保一个类不能被继承

- 用于字段，确保一个字段只能在声明或构造时被初始化一次，之后就再不能被修改

## 抽象类

抽象类无法被实例化，仅用于被子类继承。

抽象类可以包含抽象方法。抽象方法无法被实现，继承抽象类的子类必须覆写抽象方法。

```java
abstract class Person {
  public String name;
  public abstract void run();
  public say_my_name() {
    System.out.printf("My name is %s\n", this.name);
  }
}

class Student extends Person {
  public Student(String name) {
    this.name = name;
  }

  @Override
  public void run() {
    System.out.println("A student is running...");
  }
}

class Employee extends Person {
  public Employee(String name) {
    this.name = name;
  }

  @Override
  public void run() {
    System.out.println("An employee is running...");
  }
}
```

抽象类和其子类也可以向上转型，例如

```java
void everyone_run(Person[] persons) {
  for (Person person : persons) {
    person.run();
  }
}

void main() {
  Person[] persons = new Person[] {
    new Student("Alice"),
    new Employee("Bob"),
  };
  everyone_run(persons);
}
```

可以发现，方法`everyone_run`只需要处理一个`Person`的数组，我们只需要知道处理的对象都有一个`run()`方法，而不需要关心具体是哪个子类继承了`Person`，以及`run()`是怎么被实现的。这一操作被称为面向抽象编程。其特征是

- 上层代码只定义规范（例如 `abstract class Person`）；

- 不需要子类就可以实现业务逻辑（正常编译）；

- 具体的业务逻辑由不同的子类实现，调用者并不关心。

## 接口

现代编程会更倾向于数据与逻辑分离。抽象类混杂了字段、抽象方法、具体方法（有实现的方法），同时定义了数据与行为，不太好。

对比抽象类，接口仅定义了一系列行为。

```java
interface Person {
  void run();
}

interface Hello {
  // 接口也可以定义抽象方法的默认实现，避免重复代码
  default public hello() {
    System.out.println("Hello!");
  }
}

class Student implements Person {
  public String name;

  public Student(String name) {
    this.name = name;
  }

  @Override
  public void run() {
    System.out.println("A student is running...");
  }
}

class Employee implements Person, Hello {
  public String name;

  public Employee(String name) {
    this.name = name;
  }

  @Override
  public void run() {
    System.out.println("An employee is running...");
  }
}
```

接口仅定义一系列抽象方法。接口可以给出抽象方法的具体实现

接口也可以继承别的接口

```java
interface Creature {
    void live();
}

interface Person extends Creature {
    void run();
    String getName();
}
```

一个类可以实现多个接口。菱形问题不适用于实现多个接口的情况，因为接口不会给出方法的具体实现，只有实现接口的类才会给出具体实现。

## 静态字段与静态方法

我们可以在一个类中定义静态字段和静态方法，调用时通过类名调用。静态字段和静态方法常用于定义辅助方法，如`Array.sort()`，`Math.PI`。

接口也可以定义静态字段（但没有静态方法）。接口的静态字段必须是`public static final`

```java
public interface Person {
    public static final int MALE = 1;
    public static final int FEMALE = 2;
}
```

可以简写成

```java
public interface Person {
    // 编译器会自动加上public static final:
    int MALE = 1;
    int FEMALE = 2;
}
```

## 常用类

### `String`和编码

### `StringBuilder`和`StringJoiner`

### 包装类型

`Integer`包装`int`，使我们可以赋值`null`给一个“整数”。

### JavaBean

### `Enum`

### `Record`

### `BigInteger`

### `BigDecimal`

### 常用工具类
