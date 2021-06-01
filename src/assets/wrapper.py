import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from pandioml.core import Pipelines
import fnc as pm
import config
from pandioml.core.artifacts import artifact
import time
from pandioml.data.record import JsonSchema

artifact.set_storage_location(config.pandio['ARTIFACT_STORAGE'])


class Wrapper:
    fnc = None
    result = None
    input_schema = None
    pipeline_name = None

    def __init__(self, dataset_name=None, pipeline_name=None):
        self.pipeline_name = pipeline_name
        artifact.add('runtime_settings', {'config.pandio': config.pandio, 'sys.version': sys.version,
                                          'timestamp': time.strftime("%Y%m%d-%H%M%S")})

        if dataset_name is not None:
            try:
                if os.path.exists(dataset_name + '/dataset.py'):
                    sys.path.insert(1, os.path.join(os.getcwd(), dataset_name))
                    _dataset = __import__('dataset')
                    self.input_schema = _dataset.Dataset.schema()
                else:
                    self.input_schema = getattr(__import__('pandioml.data', fromlist=[dataset_name]),
                                                dataset_name).schema()
            except Exception as e:
                raise Exception(f"Could not find the dataset specified at ({dataset_name}): {e}")
        else:
            if hasattr(pm.Function, 'input_schema'):
                self.input_schema = pm.Function.input_schema

    def process(self, input, context):
        if hasattr(pm.Function, 'input_schema') and hasattr(pm.Function.input_schema, 'decode'):
            self.fnc = pm.Function(self.input_schema.decode(input), context, config)
        else:
            self.fnc = pm.Function(input, context, config)
        try:
            self.fnc.startup()
        except Exception as e:
            raise Exception(f"Could not execute startup method: {e}")

        try:
            p = self.fnc.pipelines()
        except Exception as e:
            raise Exception(f"Could not build pipelines: {e}")

        if isinstance(p, Pipelines) is False:
            raise Exception(f"Method pipelines should return a Pipelines object!")

        if self.pipeline_name is None:
            if context.get_user_config_value('pipeline') is not None:
                self.pipeline_name = context.get_user_config_value('pipeline')
            else:
                self.pipeline_name = p.get_keys()[0]

        output = p.go(self.pipeline_name, self.fnc)
        if isinstance(output[self.pipeline_name], tuple) and isinstance(output[self.pipeline_name][0], Exception):
            raise Exception(f"An exception occurred in the pipeline: {output[self.pipeline_name][0]} {output[self.pipeline_name][1]}")
            # TODO, see if this should be a print and continue, or halt the entire execution

        self.result = self.fnc.get_result()

        if 'OUTPUT_TOPICS' in config.pandio:
            for output_topic in config.pandio['OUTPUT_TOPICS']:
                if output is not None:
                    context.publish(output_topic, JsonSchema(getattr(pm, output[self.pipeline_name].schema()['name'])).encode(output[self.pipeline_name]).decode('UTF-8'))
                else:
                    print("Warning, output variable is empty, should be defined in self.fnc.done method.")

        if artifact.get_name_id() is not None:
            context.incr_counter(artifact.get_name_id(), 1)

            count = context.get_counter(artifact.get_name_id())

            if count > 0 and count % 1000 == 0:
                if artifact.get_pipeline_id() is not None:
                    artifact.save(checkpoint=True)

        return input
