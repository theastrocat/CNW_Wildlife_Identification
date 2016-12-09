from sys import argv
from os.path import isdir
from os import makedirs

import metadata_handler as mdh
import clean_db as cdb
import feature_extractor as fe


''' takes directory of images (and optional dataset name)
to use from command prompt:
    python data_pipeline.py <directory of photos> (optional: dataset_name)'''


#TODO: separate mdh and cdb steps?
#  paths can then be specified only in process photos
#  get_raw_metadata and create_dataframe can then take paths
#  instead of taking dataset_name and re-creating path names

def get_raw_metadata():
    pass


def create_dataframe(photo_dir, dataset_name = 'Wildlife_ID_Data'):

    '''Takes a directory of photos. Returns a dataframe of photo metadata.
    Stores data in raw json and csv form.
    Usage:
    df = dpl.create_dataframe(photo_dir, dataset_name = <desired_dataset_name>)
    df can then be customized according to the needs of the individual dataset
    '''

    path_to = path_dict(dataset_name, photo_dir)
    data_path = path_to['dataset']

    with open(data_path + 'info.txt','w') as outf:
        outf.write(photo_dir+'\n'+data_path)

    jsonfile = path_to['json']
    csvfile = path_to['csv']
    mdh.build_json_database(photo_dir, jsonfile)
    print '\ndata pipeline processing: {}\ncreated: {}\ncreated: {}\n'\
            .format(photo_dir, jsonfile, csvfile)

    df = cdb.create_csv(jsonfile, csvfile)
    return df


def path_dict(dataset_name, photo_dir = None):
    'returns dict of paths for structure of data folder'
    def _make_path(target):
        return "data/{}/{}".format(dataset_name, target)
    dd = {}
    dd['photos'] = photo_dir
    dd['dataset'] = _make_path('')
    dd['json'] = _make_path('raw_metadata.json')
    dd['csv'] = _make_path('metadata.csv')
    dd['features'] = _make_path('features.npy')

    return dd

def confirm_overwrite(path):
    response = raw_input('This data set already exists. Overwrite? [yes/no] ')
    if response.lower() == 'no':
        return False
    elif response.lower() == 'yes':
        return True
    else:
        print 'please type "yes" or "no"'
        return confirm_overwrite(path)


def process_photos(photo_dir, dataset_name = 'Wildlife_ID_Data'):

    if isdir('data/'+dataset_name):
        if confirm_overwrite('data/'+dataset_name) == False:
            print "aborting process_photos"
            return
        else: pass

    else:
        print 'Creating Directory: data/'+dataset_name
        makedirs('data/'+dataset_name)

    path_to = path_dict(dataset_name, photo_dir)

    print "\ndata pipeline: fetching  photo metadata, creating pandas database and csv . . .\n"
    df = create_dataframe(photo_dir, dataset_name = dataset_name)
    print "\ndata pipeline: extracting features . . .\n"

    #FIXME: ? is it better to import pandas here and just pass
    #  df.file_path to fe ?

    features = fe.extract_features(df,
                            save_loc = path_to['features'][:-4])
    print "\ndata pipeline: photo processing complete!\n"

    df = fe.feature_df(df, features)

    # return df


# loads a dataframe with only features and
def load_df(dataset_name):
    path_to = path_dict(dataset_name)
    df = fe.feature_df(path_to['csv'], path_to['features'])
    return df


#TODO:  convert dpl to class
class ImageProcessor(object):
    """ImageProcessor takes a directory of photos and/or a data set name
    IP.process_photos() creates json file, csv and inception-v3 features"""

    def __init__(self, photo_dir = None, dataset_name = 'Wildlife_ID_Data'):
        self.photos = photo_dir
        self.data_name = dataset_name
        self.data_path = self._make_path('')
        self.json = self._make_path('raw_metadata.json')
        self.csv = self._make_path('metadata.csv')
        self.features = self._make_path('features')
        self.info = self._make_path('info.txt')


    def _make_path(self, target):
        return "data/{}/{}".format(self.data_name, target)


    def record_info(self):
        #TODO: add date created
        info = 'Data Set Name: '+self.data_name\
                +'\n\tdataset loc: '+self.data_path\
                +'\n\tsource photos: '+self.photos\
                +'\n\tjson data: '+self.json\
                +'\n\tdataframe csv: '+self.csv\

        with open(self.info,'w') as outf:
            outf.write(info)


#TODO: now that I've pulled out these three functions they look kinda silly
#  Why wrap a function I built elsewhere + one line of text
    def create_json(self):
        mdh.build_json_database(self.photos, self.json)
        print '\ndata pipeline created: {}\n'\
                .format(self.json)


    def create_dataframe(self):
        df = cdb.create_csv(self.json, self.csv)
        print '\ndata pipeline created: {}\n'\
                .format(self.csv)
        return df


    def feature_df(dataset_name):
        '''Returns a dataframe of filenames and tensorflow features
        '''
        df = fe.feature_df(self.csv, self.features)
        return df


    def process_photos(self):

        if isdir(self.data_path):
            if confirm_overwrite(self.data_path) == False:
                print "aborting process_photos"
                return
            else: pass

        else:
            print 'Creating Directory: '+self.data_path
            makedirs(self.data_path)

        print "\ndata pipeline: fetching  photo metadata, creating pandas database and csv . . .\n"

        self.record_info()

        self.create_json()

        df =  self.create_dataframe()

        print "\ndata pipeline: extracting features . . .\n"
        features = fe.extract_features(df,
                                save_loc = self.features)

        print "\ndata pipeline: photo processing complete!\n"
        df = fe.feature_df(df, features)

        return df


if __name__ == '__main__':

    if len(argv)==3:
        ImageProcessor(photo_dir = argv[1], dataset_name = argv[2]).process_photos()

    else:
        ImageProcessor(photo_dir = argv[1]).process_photos()
