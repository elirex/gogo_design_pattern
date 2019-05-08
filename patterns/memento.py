from queue import Queue


class Memento:
    def __init__(self, state):
        self.state = state


class Application:
    state = 'init state'

    def backup(self) -> Memento:
        return Memento(self.state)

    def rollback(self, memento: Memento):
        self.set_state(memento.state)

    def set_state(self, state):
        self.state = state

    def __str__(self):
        return self.state


class RecoverManager:
    q = Queue()

    def add(self, memento: Memento):
        self.q.put(memento)

    def get(self) -> Memento:
        return self.q.get()


if __name__ == '__main__':
    recover = RecoverManager()
    app = Application()
    print(app)

    app.set_state('State 2')
    print(app)
    recover.add(app.backup())
    # TODO: backup State 2

    app.set_state('State 3')
    print(app)

    # TODO: roll back to State2
    app.rollback(recover.get())
    print(app)

    """Excepted Result
    init state
    State 2
    State 3
    State 2
    """


