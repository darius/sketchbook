from multitask import make_channel, ready, spawn, call, run

# A dumb example of using the library

def main():
    cput, cget = make_channel()

    def ping():
        for i in range(20):
            cput(i)
            yield ready

    def pong():
        while True:
            print (yield call(whee))

    def whee(answer):
        x = yield cget
        y = yield cget
        answer(x+y)

    spawn(pong())
    spawn(ping())
    run()

main()
#. 1
#. 5
#. 9
#. 13
#. 17
#. 21
#. 25
#. 29
#. 33
#. 37
#. 
