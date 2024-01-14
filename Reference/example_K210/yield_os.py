def event():
    print('start yield')
    # return next(task) and yield next(task.send('set_two'))
    one = yield 'get_one'
    assert(one == 'set_two')
    print(one)
    yield 'get_two'  # return next(task) and yield next(task.send('set_two'))
    print('exit yield')
    yield  # yield next() to exit or raise StopIteration

task = event()
run_one = next(task)  # need next(task) init and next(task) == task.send(None)
# so next(task) => yield 'get_one' => run_one = 'get_one'
assert(run_one == 'get_one')
run_two = task.send('set_two')
assert(run_two == 'get_two')
print('run : ', run_one, ' and ', run_two)

try:
    next(task)
    print('run end')
    next(task)  # will raise StopIteration
except Exception as e:
    print('yield StopIteration')

if __name__ == '__main__':

    def task():
        while True:
            print('hello')
            yield

    tmp = task()
    while True:
        next(tmp)

    while True:
        print('hello')























class Task:

    def __init__(self, event=(lambda: print('task running'))):
        self.event = event
        self.cb = self.pre()
        next(self.cb)
        print('task init')

    def pre(self):
        print('task start')
        flag = True
        while flag is True:
            flag = yield flag
            self.event()
        print('task exit')

    def run(self, flag=True):
        try:
            res = self.cb.send(flag)
            return res
        except StopIteration as e:
            return False


if __name__ == "__main__":
    tmp = Task()

    assert(tmp.run())
    assert(tmp.run())
    assert(False == tmp.run(False))

    print(tmp.run())
    print(tmp.run(False))

    class music:

        def __init__(self):
            self.task = Task(self.pre)
            self.args = None
            print('music init')

        def pre(self):
            print('pre ', self.args)

        def play(self, size=10):
            self.args = list(range(size))
            print(self.task.run())

        def stop(self):
            print(self.task.run(False))
            self.__init__()

        def loop(self):
            self.alive = False
            while self.alive:
                self.play()
            stop()

    tmp = music()
    tmp.play()
    tmp.stop()
    tmp.play()

