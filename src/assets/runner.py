from pandioml.function import Context
from pandioml.core.artifacts import artifact
import signal
import argparse
import tracemalloc
import wrapper as wr
import os, sys

shutdown = False
tracemalloc.start(10)


def run(dataset_name, loops):
    import time
    try:
        if os.path.exists(dataset_name+'/dataset.py'):
            sys.path.insert(1, os.path.join(os.getcwd(), dataset_name))
            _dataset = __import__('dataset')
            generator = _dataset.Dataset()
        else:
            generator = getattr(__import__('pandioml.data', fromlist=[dataset_name]), dataset_name)()
    except Exception as e:
        raise Exception(f"Could not find the dataset specified at ({dataset_name}): {e}")

    w = wr.Wrapper(dataset_name=dataset_name)

    index = 0
    while True:
        start = time.time()
        c = Context()

        if shutdown or (index >= loops and loops != -1):
            break

        event = generator.next()

        print('event')
        print(event)

        result = w.process(generator.schema().encode(event).decode('UTF-8'), c)

        print('result')
        print(result)

        print('result')
        print(w.result)

        if w.result is not None:

            print(f"Actual: {int(w.result['labels'])}")
            print(f"Prediction: {int(w.result['prediction'])}")
            print("")

        end = time.time()
        print(f"Runtime ({index}) of the program is {round(end - start, 3)}")

        w.output = None

        index = artifact.add('dataset_index', (index + 1))

    w.fnc.shutdown()


def shutdown_callback(signalNumber, frame):
    global shutdown
    shutdown = True


signal.signal(signal.SIGINT, shutdown_callback)
signal.signal(signal.SIGTERM, shutdown_callback)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test your PandioML project')
    parser.add_argument('--dataset_name', type=str, help='The name of the data set inside of pandioml.data')
    parser.add_argument('--loops', type=str, help='The number of events to process before finishing the test.',
                        required=False)

    args = parser.parse_args()
    loops = -1
    if 'loops' in args:
        loops = int(args.loops)

    run(args.dataset_name, loops)

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')[:10]
    for stat in top_stats:
        print(stat)
