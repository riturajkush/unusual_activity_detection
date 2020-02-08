import os
from .c3d import *
from .classifier import *
from  .utils.visualization_util import *
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model

graph = tf.get_default_graph()

feature_extractor = c3d_feature_extractor()
classifier_model = build_classifier_model()

def run_demo():
    video_name = os.path.basename(cfg.sample_video_path).split('.')[0]
    video = cv2.VideoCapture(cfg.sample_video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    # read video
    video_clips, num_frames = get_video_clips(cfg.sample_video_path)

    print("Number of clips in the video : ", len(video_clips))

    # build models

    print("Models initialized")

    # extract features
    rgb_features = []
    for i, clip in enumerate(video_clips):
        clip = np.array(clip)
        if len(clip) < params.frame_count:
            continue

        clip = preprocess_input(clip)
        global sess


        global graph
        with graph.as_default():
            # set_session(sess)
            rgb_feature = feature_extractor.predict(clip)[0]
            rgb_features.append(rgb_feature)

        print("Processed clip : ", i)

    rgb_features = np.array(rgb_features)

    # bag features
    rgb_feature_bag = interpolate(rgb_features, params.features_per_bag)
    print("Interpolation Done")
    
    # classify using the trained classifier model
    predictions = classifier_model.predict(rgb_feature_bag)
    print("Classification Done")
    predictions = np.array(predictions).squeeze()
    print("Predictions Squeezed")
    predictions = extrapolate(predictions, num_frames)
    print("Predictions Extrapolated")
    start, end = 0, 0
    for p in range(len(predictions)):
        if(predictions[p] >= 0.1):
            start = p
            break
    for p in range(len(predictions)-1, -1, -1):
        if(predictions[p] >= 0.1):
            end = p
            break
    start = int(start/fps )
    end = int(end/fps) 
    print(start,end)
    # print(predictions)
    save_path = os.path.join(cfg.output_folder, video_name + '.gif')
    # np.savetxt('data.csv',predictions,delimiter=',')
    # visualize predictions
    # visualize_predictions(cfg.sample_video_path, predictions, save_path)
    print("GIF saved")

