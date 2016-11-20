import os
import re
import tensorflow as tf
import tensorflow.python.platform
from tensorflow.python.platform import gfile
import numpy as np
import pandas as pd

"""Credit: KERNIX blog - Image classification with a pre-trained deep neural network"""

def create_graph():
    model_dir = 'imagenet'
    with gfile.FastGFile(os.path.join(
        model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def extract_features(in_item, save_loc = None):
    '''take list of image file paths or pandas df with file_path column
    return numpy array of features
    (optional save as .npy file to save_loc)'''

        # TODO: improve saving
        # check if features.npy exists
        # if exists (and is the same photo set) pickup from end

    # add functionality for list of photos
    if type(in_item) == list:
        list_images = in_item

    if type(in_item) == pd.core.frame.DataFrame:
        list_images = in_item.file_path

    nb_features = 2048
    features = np.empty((len(list_images),nb_features))

    create_graph()

    with tf.Session() as sess:

        next_to_last_tensor = sess.graph.get_tensor_by_name('pool_3:0')

        for ind, image in enumerate(list_images):
            if (ind%100 == 0):
                print('Processing %s...' % (image))
                # Save periodically
                if save_loc:
                    np.save(save_loc, features)
            if not gfile.Exists(image):
                tf.logging.fatal('File does not exist %s', image)

            image_data = gfile.FastGFile(image, 'rb').read()

            predictions = sess.run(next_to_last_tensor,
                                {'DecodeJpeg/contents:0': image_data})
            features[ind,:] = np.squeeze(predictions)

    if save_loc: np.save('data/FSM2_iter1/features', features)
    return features