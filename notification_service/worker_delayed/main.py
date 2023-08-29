from rmq import Rmq


if __name__ == '__main__':
    rmq = Rmq()
    rmq.channel.start_consuming()
