from pandioml.function import FunctionBase
from pandioml.core import Pipeline, Pipelines
from pandioml.core.artifacts import artifact
from pandioml.model import LogisticRegression
from pandioml.model import StandardScaler
from pandioml.data.record import Record, Null, Boolean, Integer, Long, Float, Double, Bytes, String, Array, Map
from pandioml.metrics import Accuracy
from pandioml.model import ModelUtility


class Output(Record):
    prediction = Boolean()


class Function(FunctionBase):
    model = artifact.add('LogisticRegression_model',
                         ModelUtility.load_or_instantiate('LogisticRegression_model.pickle', LogisticRegression))
    metric = Accuracy()  #Optional
    scaler = StandardScaler()  #Optional

    def feature_extraction(self, result={}):
        result['features'] = {'feature_one': 0, 'feature_two': 1}

        return result

    # Optional
    def scale(self, result={}):
        result['features'] = self.scaler.learn_one(result['features']).transform_one(result['features'])
        return result

    def label_extraction(self, result={}):
        result['labels'] = 0

        return result

    def done(self, result={}):
        # Optional
        self.metric = artifact.add('Accuracy_Metric', self.metric.update(result['labels'], result['prediction']))

        return Output(prediction=result['prediction'])

    def pipelines(self, *args, **kwargs):
        return Pipelines().add(
            'inference',
            Pipeline(*args, **kwargs)
                .then(self.feature_extraction)
                .then(self.scale)  # Optional
                .then(self.label_extraction)
                .then(self.fit)
                .final(self.predict)
                .done(self.done)
                .catch(self.error)
        )
