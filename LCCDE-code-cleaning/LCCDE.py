# rewrote LCCDE() function from original paper, abstracted it to work with
# a list of models instead of three hard-coded models


from itertools import groupby
from river import stream
from statistics import mode
import numpy as np


class LCCDE_Model:
    """Represents a base learner in the Leader Class and Confidence Decision Ensemble (LCCDE)."""
    def __init__(self, model, name: str):
        # base learner object that should have the predict() and predict_proba() functions (e.g. XGBClassifier())
        self.model = model
        # string name
        self.name = name
        # the following attributes are for evaluation metrics
        self.accuracy = None
        self.precision = None
        self.recall = None
        self.f1_avg = None  # average of F1 scores
        self.f1 = None  # list of F1 scores for each class
        # the following attributes are for storing predictions for one data point
        self.predicted_class = None  # predicted class
        self.highest_predicted_prob = None  # class with highest confidence score

    def __repr__(self):
        return "LCCDE_Model({m}, {n})".format(m=self.model, n=self.name)

    # this method is not tested here
    # def store_eval_metrics(self, y_test, y_pred):
    #     self.accuracy = accuracy_score(y_test, y_pred)
    #     self.precision = precision_score(y_test, y_pred, average='weighted')
    #     self.recall = recall_score(y_test, y_pred, average='weighted')
    #     self.f1_avg = f1_score(y_test, y_pred, average='weighted')
    #     self.f1 = f1_score(y_test, y_pred, average=None)


def all_equal(iterable):
    """Returns whether all values in an Iterable are equal
    (https://stackoverflow.com/a/3844832).
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def all_unique(lst):
    """Returns whether all values in an Iterable are unique
    (https://www.geeksforgeeks.org/python-check-if-list-contains-all-unique-elements/).
    """
    # use the unique function from numpy to find the unique elements in the list
    unique_elements, counts = np.unique(lst, return_counts=True)
    # return True if all elements in the list are unique (i.e., the counts are all 1)
    return all(counts == 1)


def LCCDE_predict_class(xi, models: list[LCCDE_Model], leader_models: dict):
    """Classifies a data record using the LCCDE model.
    Returns the model's predicted class.
    :param xi: features for a data record
    :param models: list of LCCDE_Model objects
    :param leader_models: a dictionary with Labels as keys, the value of each key should be m.model for any m in in models
    """
    if all_equal([m.predicted_class for m in models]):
        # if all models predict the same class, use that as final predicted class
        final_pred_class = models[0].predicted_class

    elif all_unique([m.predicted_class for m in models]):
        # if all models predict a different class, choose final predicted class based on class leaders

        # find models that are the leader for their predicted class
        matching_models = []
        for m in models:
            if leader_models[m.predicted_class] == m.model:
                matching_models.append(m)
        if len(matching_models) == 1:
            # if only one model is the leader for its predicted class, then use its prediction
            final_pred_class = matching_models[0].predicted_class
        else:
            # otherwise, use the prediction of the model with highest confidence
            highest_confidence = max([m.highest_predicted_prob for m in models])
            most_confident_models = [m for m in models if m.highest_predicted_prob == highest_confidence]
            final_pred_class = most_confident_models[0].predicted_class  # if there's a tie, just pick the first one

    else:
        # if some models agree and some don't, use the leader of the majority class as the final predicted class
        majority_class = mode([m.predicted_class for m in models])  # if there's a tie, mode() will pick the first one
        leader = leader_models[majority_class]
        final_pred_class = leader.predict(xi)[0]

    return final_pred_class


def LCCDE(X_test, y_test, models: list[LCCDE_Model], leader_models, verbose=False) -> tuple[list, list]:
    """Uses the Leader Class and Confidence Decision Ensemble (LCCDE) to
    classify records in a feature matrix. Casts predicted labels to ints.
    Returns a tuple containing ground truth labels and predicted labels.
    :param X_test: feature matrix for testing (pandas DataFrame)
    :param y_test: ground truth Labels corresponding to X_test
    :param models: a list of the LCCDE_Model objects
    :param leader_models: a dictionary with Labels as keys, the value of each key should be a model in base_learners
    :param verbose: if True, prints a progress update after every 1000 predictions
    """
    y_actual = []  # list of actual y-values (I think it ends up being the same as the y_test parameter)
    y_predicted = []  # the values predicted by the ensemble for each xi in X_test

    count = 0
    # predict each label based on the features
    for xi, yi in stream.iter_pandas(X_test, y_test):
        xi = np.array(list(xi.values())).reshape(1, -1)

        # for each model, predict class based on feature values xi
        for m in models:
            m.predicted_class = int(m.model.predict(xi)[0])  # predicted class for this data point xi
            predicted_probs = m.model.predict_proba(xi)  # prediction probability confidence list
            m.highest_predicted_prob = np.max(predicted_probs)  # max of prediction probability confidence list

        # use the ensemble to predict the class of xi
        final_pred_class = int(LCCDE_predict_class(xi, models, leader_models))

        # save the actual and predicted y-values
        y_actual.append(yi)
        y_predicted.append(final_pred_class)

        count += 1
        if verbose and count % 1000 == 0:
            print("Progress update: LCCDE has predicted {n} values".format(n=count))

    return y_actual, y_predicted
