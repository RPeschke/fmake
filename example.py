import fmake


@fmake.program
def example(test = "hello"):
    print(test)

    


@fmake.program
def example1(t1, t2 = "world"):
    return t1 + " " + t2


@fmake.program
def example2():
    return "123"