import os
import sys
from .config import Conf
import hashlib
from pandioml.core.artifacts import artifact
import zipfile
from appdirs import user_config_dir
import docker
from shutil import copyfile
dirname = os.path.dirname(os.path.realpath(__file__))

config = Conf()
if os.path.exists(user_config_dir('PandioCLI', 'Pandio')+'/config.json'):
    config.load(user_config_dir('PandioCLI', 'Pandio')+'/config.json')


def start(args):
    BUF_SIZE = 65536

    loops = -1
    if args.loops is not None:
        loops = int(args.loops)

    pipeline_name = None
    if args.pipeline_name is not None:
        pipeline_name = args.pipeline_name

    if not os.path.isfile(f"{args.project_folder}/function.py"):
        print(f"{args.project_folder} is invalid.")
        exit()

    val = input("Would you like to store artifacts (dataset, pipeline, model, etc.)? If no, only the model will be saved. (y,n): ")
    store = True if val.lower() == 'y' or val.lower() == 'yes' else False
    if store:
        print("Artifacts will be saved!")

        print("")

        name_id = input("Would you like to name this run? Leave blank for no name: ")

        print("")

        print("Generating artifact identifiers.")

        os.system(
            f"cd {args.project_folder} && rm -rf dist && rm -rf build && rm -rf function.spec && rm -rf __pycache__ && "
            f"PYTHONHASHSEED=1 && export "
            "PYTHONHASHSEED && pyinstaller -F --exclude-module scikit-learn "
            "--exclude-module river --exclude-module pandioml --exclude-module scikit-multiflow --exclude-module "
            "pulsar-client --exclude-module Faker --exclude-module scipy --exclude-module numpy --exclude-module "
            "pandas --exclude-module python-dateutil --exclude-module six --exclude-module test-unidecode "
            "--exclude-module ratelimit --exclude-module fastavro --exclude-module grpcio --exclude-module certifi "
            "--exclude-module prometheus-client --exclude-module apache-bookkeeper-client --exclude-module protobuf "
            "--exclude-module pytz --exclude-module sortedcontainers --exclude-module matplotlib --exclude-module "
            "requests --exclude-module pymmh3 --exclude-module setuptools --exclude-module pyparsing --exclude-module"
            " pillow --exclude-module cycler --exclude-module kiwisolver --exclude-module idna --exclude-module "
            "chardet --exclude-module urllib3 --exclude-module threadpoolctl --exclude-module sklearn "
            "--exclude-module pytest --exclude-module pickle function.py >/dev/null 2>&1 && unset PYTHONHASHSEED")

        md5 = hashlib.md5()

        with open(f"{args.project_folder}/dist/function", 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)

        os.system(f"cd {args.project_folder} && rm -rf dist && rm -rf build && rm -rf function.spec && rm -rf __pycache__")

        if len(name_id) > 0:
            artifact.set_name_id(name_id)

        artifact.set_pipeline_id(md5.hexdigest())

        print(f"Artifact pipeline id is: {artifact.get_pipeline_id()}")

        print(f"Artifact name id is: {artifact.get_name_id()}")
    else:
        print("NOT SAVING any artifacts!")

    body = ''
    with open(f"{args.project_folder}/function.py", 'r') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            body += data

    def zipit(storage_location):
        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for file in files:
                    rel_dir = os.path.relpath(root, path)
                    if 'test' not in file and 'runner.py' not in file and \
                            'artifacts' not in rel_dir and 'pycache' not in rel_dir:
                        rel_file = os.path.join(rel_dir, file)
                        ziph.write(os.path.join(root, file), rel_file)

        zipf = zipfile.ZipFile(storage_location + '/pipeline_files.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(args.project_folder, zipf)
        zipf.close()

    artifact.add('archive_pipeline', zipit)

    print("Starting execution of pipeline(s).")

    # sys.path.insert(1, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets'))
    # sys.path.insert(1, os.path.join(os.getcwd(), args.project_folder))
    # pm = __import__('runner')
    # pm.run(args.dataset_name, loops, pipeline_name=pipeline_name)
    #
    # exit()

    client = docker.from_env()
    path = os.path.join(os.getcwd(), args.project_folder)
    if os.path.exists(os.path.join(os.getcwd(), args.dataset_name, 'dataset.py')):
        dpath = os.path.join(os.getcwd(), args.dataset_name)
    else:
        dpath = None

    copyfile(os.path.join(dirname, 'assets/runner.py'),
             os.path.join(path, 'runner.py'))
    copyfile(os.path.join(dirname, 'assets/wrapper.py'),
             os.path.join(path, 'wrapper.py'))

    dataset_name = args.dataset_name

    volumes = {path: {'bind': '/code', 'mode': 'rw'}}
    if dpath is not None:
        dataset_name = '/dataset'
        volumes[dpath] = {'bind': dataset_name, 'mode': 'rw'}

    client.containers.run('pandioml/test', name='pandiocli', volumes=volumes,
                          detach=True)

    api = docker.APIClient()
    c = api.exec_create('pandiocli', f"python /code/runner.py --dataset_name {dataset_name} --loops {loops} "
                                     f"--pipeline_name {pipeline_name}", tty=True)
    s = api.exec_start(c, stream=True)
    for line in s:
        print(line)

    os.remove(os.path.join(path, 'runner.py'))
    os.remove(os.path.join(path, 'wrapper.py'))

    c = client.containers.get('pandiocli')
    c.remove(force=True)

    print("")
