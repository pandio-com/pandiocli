<a href="https://pandio.com"><img src="https://pandio-com.github.io/static/files/assets/pandio_225_blue-05.svg" alt="Pandio Logo"></a>

# PandioCLI - Pandio.com Machine Learning CLI Tool

This repository contains the PandioCLI tool to develop and deploy machine learning for streaming data.

## Quick Links

#### [Pandio.com/PandioML](https://pandio.com/pandioml) - [Pandio.com](https://pandio.com) - [Getting Started](./guides/GETTING-STARTED.md) - [Quick Start](./guides/QUICK-START.md) - [PyPi PandioML](https://pypi.org/project/pandioml/) - [PyPi PandioCLI](https://pypi.org/project/pandiocli/)

### Installation

`pip install pandiocli`

## Requirements

Python 3.5 - 3.8
PIP > 20.0.0

### Commands

#### `pandiocli function generate --project_name example`

Generates a project template in the current working directory at `./example`
      
1. `./example/function.py`

      This is the file where all of your logic should be placed.

1. `./example/requirements.txt`

      This file should contain all the necessary Python packages to power `function.py`. The contents of this will automatically be installed for you when deploying to Pandio's platform. When running locally, make sure to install as you normally would `pip install -r requirements.txt`

1. `./example/config.py`

      This contains non-sensitive configuration parameters for the project. Sensitive configuration parameters are set via the PandioCLI.
      
      Acceptable values are:
      
  ```buildoutcfg
'FUNCTION_NAME': 'exampleFunction123',
'CONNECTION_STRING': 'pulsar://localhost:6651',
'ADMIN_API': 'http://localhost:8080',
'TENANT': 'public',
'NAMESPACE': 'default',
'INPUT_TOPICS': ['non-persistent://public/default/in'],
'OUTPUT_TOPICS': ['non-persistent://public/default/out'],
'LOG_TOPIC': 'non-persistent://public/default/log',
'ARTIFACT_STORAGE': "./artifacts"
```


#### `pandiocli function upload --project_folder path_to_folder`

Package up your function project and upload it to Pandio's platform.

#### `pandiocli dataset generate --project_name example`

Generates a project template in the current working directory at `./example`

1. `./example/dataset.py`

      This is the file where all of your logic should be placed.
      
      Three things need to be defined to complete the dataset:
      
      * `__init__`
      
          Establish a connection or load your data. Returns an iterable.
          
      * `next`
      
          Returns a single record from the dataset.
      
      * `schema`
      
          Defines the schema used for the dataset.
          
      For more information on schemas, see the Schema Registry.
      
1. `./example/wrapper.py`

      This is a wrapper class for the dataset to allow it to work on the Pandio platform.
      
      *Note: You should not need to ever modify this file.*

1. `./example/requirements.txt`

      This file should contain all the necessary Python packages to power `dataset.py`. The contents of this will automatically be installed for you when deploying to Pandio's platform. When running locally, make sure to install as you normally would `pip install -r requirements.txt`

1. `./example/config.py`

      This contains non-sensitive configuration parameters for the project. Sensitive configuration parameters are set via the PandioCLI.

      Acceptable values are:
      
```buildoutcfg
'FUNCTION_NAME': 'exampleFunction123',
'CONNECTION_STRING': 'pulsar://localhost:6651',
'ADMIN_API': 'http://localhost:8080',
'TENANT': 'public',
'NAMESPACE': 'default',
'INPUT_TOPICS': ['non-persistent://public/default/in'],
'OUTPUT_TOPICS': ['non-persistent://public/default/out'],
'LOG_TOPIC': 'non-persistent://public/default/log'
```

Additional parameter of `--type` can be specified to generate a dataset with a template.

Currently supported templates are:

* mysql
* trino
* csv

#### `pandiocli dataset upload --project_folder path_to_folder`

Package up your dataset project and upload it to Pandio's platform.

#### `pandiocli config show`

This will output the current configuration for the PandioCLI

#### `pandiocli config file`

This will output the current configuration file location for the PandioCLI

#### `pandiocli config reset`

This will delete all settings for the PandioCLI

#### `pandiocli config set --key PANDIO_TOKEN --value ABC123`

This command allows you to manually set the configuration parameters for PandioCLI

These values are first set when you use the register command.

* PANDIO_CLUSTER
* PANDIO_TENANT
* PANDIO_NAMESPACE
* PANDIO_CLUSTER_TOKEN
* PANDIO_EMAIL
* PANDIO_DATA_TOKEN

*Note: These values can be found from inside of your Pandio.com Dashboard*

#### `pandiocli test --project_folder folder_name --dataset_name FormSubmissionGenerator --loops 1000`

This is a helper method to running the `folder_name/runner.py` file manually with Python. It includes performance metrics which is helpful to debug excessive resource usage such as memory leaks.

**project_folder** is the relative path to the project folder from where the command is being executed.

**dataset_name** is the name of the `pandioml.data` datasets and generators available inside of PandioML or the relative path to the folder of the dataset generated by the `pandiocli dataset generate` command.

**loops** is the number of events to process. Most streams of data are infinite, so this allows iterative testing with limited data.

**pipeline_name** is the number of events to process. Most streams of data are infinite, so this allows iterative testing with limited data.

#### `pandiocli register your@email.com`

This command registers a Pandio.com account for you. An email with a link to verify your registration will be sent.

Once the link is clicked, the local PandioCLI will be configured successfully with your new Pandio account.

If you already have a Pandio.com account, you'll need to use the `pandiocli config` command to manually set the configuration with values inside of the Pandio.com Dashboard.

## Contributing

All contributions are welcome.

The best ways to get involved are as follows:

1. [Issues](./issues)

    This is a great place to report any problems found with PandioCLI. Bugs, inconsistencies, missing documentation, or anything that acted as an obstacle to using PandioCLI.
    
1. [Discussions](./discussions)

    This is a great place for anything related to PandioCLI. Propose features, ask questions, highlight use cases, or anything else you can imagine.
    
If you would like to submit a pull request to this library, please read the [contributor guidelines](./CONTRIBUTING.md).

## License

PandioCLI is licensed under the [SSPL license](./LICENSE).