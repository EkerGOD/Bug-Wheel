def test1(func):
    func()
    print('hello')

def test2(func):
    for i in range(10):
        func()

@test1
@test2
def test3():
    print('?')

test3()