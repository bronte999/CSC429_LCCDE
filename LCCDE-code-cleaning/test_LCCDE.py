from LCCDE import all_equal, all_unique, LCCDE_Model, LCCDE_predict_class, LCCDE
import pandas as pd
import unittest


class FraudModel:
    """A dummy class that implements predict() and predict_proba()."""
    def __init__(self, prediction=None):
        self.prediction = prediction
    def predict(self, xi):
        return [xi] if self.prediction is None else [self.prediction]
    def predict_proba(self, xi):
        return [0]


class TestAllEqual(unittest.TestCase):
    def test_empty(self):
        self.assertTrue(all_equal([]))
    def test_one(self):
        self.assertTrue(all_equal([0]))
    def test_equal(self):
        self.assertTrue(all_equal([0, 0]))
    def test_not_equal_1(self):
        self.assertFalse(all_equal([0, 1]))
    def test_not_equal_2(self):
        self.assertFalse(all_equal([0, 1, 0]))


class TestAllUnique(unittest.TestCase):
    def test_empty(self):
        self.assertTrue(all_unique([]))
    def test_one(self):
        self.assertTrue(all_unique([0]))
    def test_unique(self):
        self.assertTrue(all_unique([0, 1]))
    def test_not_unique_1(self):
        self.assertFalse(all_unique([0, 0]))
    def test_not_unique_2(self):
        self.assertFalse(all_unique([0, 1, 0]))


class TestLCCDE_predict_class(unittest.TestCase):
    def test_all_equal_path_with_all_matching_models(self):
        xi = pd.Series(["a", "b"])
        models = [LCCDE_Model(FraudModel(), "m1"), LCCDE_Model(FraudModel(), "m2")]
        # both models agree on predicted class
        expected_predicted_class = "Benign"
        models[0].predicted_class = expected_predicted_class
        models[1].predicted_class = expected_predicted_class
        # should return expected class
        self.assertEqual(expected_predicted_class,
                         LCCDE_predict_class(xi, models, dict()))
    def test_all_unique_path_with_one_matching_model(self):
        xi = pd.Series(["a", "b"])
        model1 = LCCDE_Model(FraudModel(), "m1")
        model2 = LCCDE_Model(FraudModel(), "m2")
        # models disagree on predicted class
        expected_predicted_class = "Benign"
        different_predicted_class = "Masquerade"
        model1.predicted_class = expected_predicted_class
        model2.predicted_class = different_predicted_class
        # only model1 is the leader for its predicted class
        leader_models = {expected_predicted_class: model1.model,
                         different_predicted_class: model1.model}
        # should return expected class because model1 is leader
        self.assertEqual(expected_predicted_class,
                         LCCDE_predict_class(xi, [model1, model2], leader_models))
    def test_all_unique_path_with_zero_matching_models(self):
        xi = pd.Series(["a", "b"])
        model1 = LCCDE_Model(FraudModel(), "m1")
        model2 = LCCDE_Model(FraudModel(), "m2")
        # set model1 to higher confidence
        model1.highest_predicted_prob = 1
        model2.highest_predicted_prob = 0.5
        # models disagree on predicted class
        expected_predicted_class = "Benign"
        different_predicted_class = "Masquerade"
        model1.predicted_class = expected_predicted_class
        model2.predicted_class = different_predicted_class
        # both models predicted a class that they are not the leader for
        leader_models = {expected_predicted_class: model2.model, different_predicted_class: model1.model}
        # should return expected class because model1 has higher confidence
        self.assertEqual(expected_predicted_class,
                         LCCDE_predict_class(xi, [model1, model2], leader_models))
    def test_else_path_with_some_matching_models(self):
        xi = pd.Series(["a", "b"])
        expected_predict_result = 69  # we want model1.predict() to be called and return this
        model1 = LCCDE_Model(FraudModel(prediction=expected_predict_result), "m1")
        model2 = LCCDE_Model(FraudModel(), "m2")
        model3 = LCCDE_Model(FraudModel(), "m3")
        # models disagree on predicted class, but majority is expected_predicted_class
        predicted_class = "Benign"
        different_predicted_class = "Masquerade"
        model1.predicted_class = predicted_class
        model2.predicted_class = different_predicted_class
        model3.predicted_class = predicted_class
        # make model1 leader for expected_predicted_class
        leader_models = {predicted_class: model1.model}
        self.assertEqual(expected_predict_result,
                         LCCDE_predict_class(xi, [model1, model2, model3], leader_models))


class TestLCCDE(unittest.TestCase):
    # most of the work is done in LCCDE_predict_class(), this just tests LCCDE() from start to finish
    def test_1(self):
        correct_pred = 69
        wrong_pred = 0
        # one record in X_test with correct_pred as its label in y_test
        X_test = pd.DataFrame([["a", "b", "c"]])
        y_test = pd.Series([correct_pred])
        # base_learner1.predict() returns correct_pred
        model1 = LCCDE_Model(FraudModel(prediction=correct_pred), "m1")
        model2 = LCCDE_Model(FraudModel(prediction=wrong_pred), "m2")
        # base_learner1 is leader for correct_pred class
        leader_models = {correct_pred: model1.model, wrong_pred: model2.model}
        # should return y_test labels as a list, and a list of predicted values
        self.assertEqual((list(y_test), [correct_pred]),
                         LCCDE(X_test, y_test, [model1, model2], leader_models))


if __name__ == '__main__':
    unittest.main()
