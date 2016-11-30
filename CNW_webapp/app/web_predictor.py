import os
import re
import tensorflow as tf
import tensorflow.python.platform
from tensorflow.python.platform import gfile
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt


'''
Usage: run setup() globaly
then run primary() for each img individually
'''

def create_graph():
    model_dir = '../imagenet'

    with gfile.FastGFile(os.path.join(
        model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def setup():
    create_graph()

    with tf.Session() as sess:

        next_to_last_tensor = sess.graph.get_tensor_by_name('pool_3:0')

        s = sess
        t = next_to_last_tensor

        return s,t


# def extract_features(list_images):
#     '''take list of image file paths
#     return pandas series of features
#     '''
#
#     nb_features = 2048
#     features = np.empty((len(list_images),nb_features))
#
#     create_graph()
#
#     with tf.Session() as sess:
#
#         next_to_last_tensor = sess.graph.get_tensor_by_name('pool_3:0')
#
#         for ind, image in enumerate(list_images):
#
#             if not gfile.Exists(image):
#                 tf.logging.fatal('File does not exist %s', image)
#
#             image_data = gfile.FastGFile(image, 'rb').read()
#
#             predictions = sess.run(next_to_last_tensor,
#                                 {'DecodeJpeg/contents:0': image_data})
#             features[ind,:] = np.squeeze(predictions)
#
#     return features


def get_features(image, sess, next_to_last_tensor):
    if not gfile.Exists(image):
        tf.logging.fatal('File does not exist %s', image)

    image_data = gfile.FastGFile(image, 'rb').read()

    predictions = sess.run(next_to_last_tensor,
                        {'DecodeJpeg/contents:0': image_data})
    features = np.squeeze(predictions)
    return features.reshape(1,-1)


# Predict animal
def predict(feat, model = 'current_model'):

    # make predition from single feature vector

    with open(model, 'rb') as fh:
        model = pickle.load(fh)

    prediction = model.predict(feat)

    try:
        probs = model.predict_proba(feat)
        print 'prediction prepared'
        return prediction, probs
    except AttributeError:
        pass

    print 'prediction prepared'
    return prediction


def result_array(prediction):

    # create ordered DataFrame of categories and probabilities
    groups = ['Canine', 'Feline', 'Other', 'Small', 'Ungulate']
    result = pd.DataFrame(groups, columns = ['groups'])
    result['pred_strength'] = prediction[1][0]
    result.sort_values('pred_strength', axis=0,
                        ascending=True, inplace=True,
                        kind='mergesort')
    return result


def plot_pred(prediction, to_plot, save_as = None):
    # take predicted category and ordered prediction strengths
    # plot and save to file

    fig, ax = plt.subplots(figsize=(7,3))
    plt.title('Model Prediction: '+prediction[0][0])
    plt.ylabel('Species Group')
    plt.xlabel('Prediction Strength')
    ax.set_yticklabels(to_plot['groups'], rotation=50, ha='right')
    plt.barh(range(0,5), to_plot['pred_strength'], color='#6982A0', alpha=0.8)

    if save_as:
        plt.savefig('{}.png'.format(save_as), bbox_inches='tight')

    # plt.show()


def primary(image, session, tensor, plt_name):
    x = get_features(image, session, tensor)
    pred = predict(x)
    result = result_array(pred)
    plot_pred(pred, result, save_as = plt_name)
    return result


if __name__ == '__main__':
    pass