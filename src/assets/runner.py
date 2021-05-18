from pandioml.function import Context
from pandioml.core.artifacts import artifact
import signal
import argparse
import tracemalloc
import wrapper as wr
import os, sys
from goodconf import GoodConf
from appdirs import user_config_dir

config = GoodConf()
if os.path.exists(user_config_dir('PandioCLI', 'Pandio')+'/config.json'):
    config.load(user_config_dir('PandioCLI', 'Pandio')+'/config.json')

shutdown = False
tracemalloc.start(10)


def run(dataset_name, loops, pipeline_name=None):
    import time
    try:
        if os.path.exists(dataset_name+'/dataset.py'):
            sys.path.insert(1, os.path.join(os.getcwd(), dataset_name))
            _dataset = __import__('dataset')
            generator = _dataset.Dataset()
        else:
            _dataset = getattr(__import__('pandioml.data', fromlist=[dataset_name]), dataset_name)
            if 'pandio_token' in _dataset.__init__.__code__.co_varnames:
                generator = _dataset(pandio_token=getattr(config, 'PANDIO_DATA_TOKEN'))
            else:
                generator = _dataset()
    except Exception as e:
        raise Exception(f"Could not find the dataset specified at ({dataset_name}): {e}")

    w = wr.Wrapper(dataset_name=dataset_name, pipeline_name=pipeline_name)

    index = 0
    while True:
        start = time.time()
        c = Context()

        if shutdown or (index >= loops and loops != -1):
            break

        event = generator.next()

        w.process(generator.schema().encode(event).decode('UTF-8'), c)

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
