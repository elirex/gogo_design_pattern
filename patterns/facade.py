class SubSystem1:
    def hahaha(self):
        print('子系統一方法')


class SubSystem2:
    def yoyoyo(self):
        print('子系統二方法')


class Facade:

    def __init__(self):
        self._subsys_1 = SubSystem1()
        self._subsys_2 = SubSystem2()

    def methodA(self):
        self._subsys_2.yoyoyo()

    def methodB(self):
        self._subsys_1.hahaha()

    def methodC(self):
        self.methodA()
        self.methodB()

if __name__ == '__main__':
    facade = Facade()

    facade.methodA()
    """Excepted Result
    子系統二方法
    """
    print()

    facade.methodB()
    """Excepted Result
    子系統一方法
    """
    print()

    facade.methodC()
    """Excepted Result
    子系統二方法
    子系統一方法
    """
