import cPickle as pickle
import src.feature_extractor as fe


# Predict animal
def predict(image, model = 'data/current_model'):

    X = fe.extract_features([image])

    with open(model, 'rb') as fh:
        model = pickle.load(fh)

    prediction = model.predict(X)

    try:
        probs = model.predict_proba(X)
        print 'prediction prepared'
        return prediction, probs
    except AttributeError:
        pass

    print 'prediction prepared'
    return prediction
