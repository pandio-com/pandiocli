import logging, os, zipfile, hashlib, sys
from .configuration import Conf
import json
from shutil import copyfile, rmtree
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from appdirs import user_config_dir
dirname = os.path.dirname(os.path.realpath(__file__))

config = Conf()
if os.path.exists(user_config_dir('PandioCLI', 'Pandio')+'/config.json'):
    config.load(user_config_dir('PandioCLI', 'Pandio')+'/config.json')


def start(args):
    print(args)
    if args.command == 'upload':
        if 'project_folder' in args:
            root_path = os.getcwd()
            tmp_path = '/tmp/'
            path = root_path + '/' + args.project_folder
            if os.path.isdir(path):
                if os.path.exists(f"{path}/config.py"):
                    if not os.path.exists(f"{path}/deps"):
                        os.makedirs(f"{path}/deps")
                    sys.path.append(path)
                    project_config = __import__('config')

                    # Only one pipeline is supported for now
                    fnc = __import__('function')
                    pipeline_key = fnc.Function().pipelines().get_keys()[0]

                    print("Getting project requirements...")

                    f = open(f"{path}/pandio_requirements.txt", "w")
                    f.write("pandioml>=1.0.6")
                    f.close()

                    hash = hashlib.md5(bytes(args.project_folder, 'utf-8'))
                    tmp_path = tmp_path + hash.hexdigest() + '/'
                    if not os.path.exists(tmp_path):
                        os.makedirs(tmp_path)
                    tmp_file = args.project_folder.split('/')[-1:][0] + '.zip'
                    zipf = zipfile.ZipFile(tmp_path + tmp_file, 'w', zipfile.ZIP_DEFLATED)
                    zipf.write(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets/wrapper.py'), 'wrapper.py')
                    zipdir(path, zipf, args.project_folder)
                    zipf.close()
                    print(f"File located at {tmp_path}{tmp_file}")

                    if os.path.exists(f"{path}/deps"):
                        rmtree(f"{path}/deps")

                    if os.path.exists(f"{path}/pandio_requirements.txt"):
                        os.remove(f"{path}/pandio_requirements.txt")

                    arr = {
                        "name": project_config.pandio['FUNCTION_NAME'],
                        "userConfig": {
                            "pipeline": pipeline_key
                        },
                        "inputs": project_config.pandio['INPUT_TOPICS'],
                        "parallelism": 1,
                        "log-topic": project_config.pandio['LOG_TOPIC'],
                        "className": 'wrapper.Wrapper',
                        "py": tmp_file,
                        "runtime": "PYTHON"
                    }

                    mp_encoder = MultipartEncoder(
                        fields={
                            'functionConfig': ('functionConfig', json.dumps(arr), 'application/json'),
                            'data': (tmp_file, open(tmp_path + tmp_file, 'rb'), 'application/octet-stream')
                        }
                    )

                    headers = {'Content-Type': mp_encoder.content_type}

                    _token = getattr(config, 'PANDIO_CLUSTER_TOKEN')
                    if _token is not None:
                        headers['Authorization'] = f"Bearer {_token}"

                    if 'ADMIN_API' in project_config.pandio:
                        cluster = project_config.pandio['ADMIN_API']
                    else:
                        cluster = getattr(config, 'PANDIO_CLUSTER')

                    if 'TENANT' in project_config.pandio:
                        tenant = project_config.pandio['TENANT']
                    else:
                        tenant = getattr(config, 'PANDIO_TENANT')

                    if 'NAMEPSACE' in project_config.pandio:
                        namespace = project_config.pandio['NAMESPACE']
                    else:
                        namespace = getattr(config, 'PANDIO_NAMESPACE')

                    response = requests.post(
                        f"{cluster}/admin/v3/functions/{tenant}/{namespace}/{project_config.pandio['FUNCTION_NAME']}",
                        data=mp_encoder,  # The MultipartEncoder is posted as data, don't use files=...!
                        # The MultipartEncoder provides the content-type header with the boundary:
                        headers=headers
                    )

                    if os.path.exists(tmp_path + tmp_file):
                        os.remove(tmp_path + tmp_file)

                    if response.status_code == 204:
                        print("Function uploaded successfully!")
                    else:
                        raise Exception(f"The function could not be uploaded: {response.text}")
                else:
                    raise Exception(f"File ({path}/config.py) could not be found.")
            else:
                raise Exception(f"Path ({path}) could not be found.")
        else:
            raise Exception('--folder-name must be specified')
    elif args.command == 'generate':
        if 'project_name' not in args:
            raise Exception("--project_name must be specified.")

        if not os.path.exists(args.project_name):
            logging.debug(f"Creating folder {args.project_name}")
            try:
                os.makedirs(args.project_name)
            except:
                raise Exception("Could not create folder for the project: {args.project_name}")

        copyfile(os.path.join(dirname, 'assets/function_template.py'), f"{args.project_name}/function.py")
        copyfile(os.path.join(dirname, 'assets/config_template.py'), f"{args.project_name}/config.py")
        copyfile(os.path.join(dirname, 'assets/requirements_template.txt'), f"{args.project_name}/requirements.txt")

        print(f"New function project created in: `{args.project_name}`")
        print("")
        print(f"Open {args.project_name}/function.py to begin defining your model.")
        print("")
        print(f"For help creating your function, see existing examples or read the documentation in the README.")
        print("")
    else:
        raise Exception('Nothing matched the action: {0}'.format(args.command))


def zipdir(path, ziph, project_folder):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if 'test' not in file and 'runner.py' not in file:
                rel_dir = os.path.relpath(root, path)
                if rel_dir == '.' or rel_dir == 'deps':
                    project_folder = str(project_folder).split("/")[-1:][0]
                    if rel_dir == '.':
                        rel_dir = f"{project_folder}/src"
                    if rel_dir == 'deps':
                        rel_dir = f"{project_folder}/deps"
                    rel_file = os.path.join(rel_dir, file)
                    if file == 'function.py':
                        ziph.write(os.path.join(root, file), rel_file.replace('function.py', 'fnc.py'))
                    else:
                        ziph.write(os.path.join(root, file), rel_file)
