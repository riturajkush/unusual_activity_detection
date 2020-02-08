from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.conf import settings
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import event_detection.settings as settings
from django.contrib.auth import authenticate, login, logout
from detector.c3d import *
from detector.classifier import *
from detector.utils.visualization_util import *
import numpy as np
import tensorflow as tf
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

# Create your views here.
# demo.run_demo()
@csrf_exempt
def index(request):
    if request.method == "POST":
        try:
            # print(request.url)
            myfile = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            
            uploaded_file_url = os.path.join(settings.BASE_DIR, 'media', filename)

            start,end=0,0
            start, end = run_demo(uploaded_file_url)
            if start==0 and end==0:
                message = {
                    'status':False,
                    'message':"No activity detected",
                    'start':start,
                    'end':end 
                }
            else:
                 message = {
                    'url': fs.url(filename),
                    'status':True,
                    'message':"Unusual Activity Detected",
                    'start':start,
                    'end':end
                }
            return JsonResponse(message)
        except:
            message = {
                'status':False,
                'message':"Processing Error",
            }
            return JsonResponse(message)

    return render(request,'home/upload_video.html',context={})

def run_demo(video_path):
    video_name = os.path.basename(video_path).split('.')[0]
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    # read video
    video_clips, num_frames = get_video_clips(video_path)

    print("Number of clips in the video : ", len(video_clips))

    # build models

    print("Models initialized")
    feature_extractor = c3d_feature_extractor()
    classifier_model = build_classifier_model()
    # extract features
    rgb_features = []
    for i, clip in enumerate(video_clips):
            clip = np.array(clip)
            if len(clip) < params.frame_count:
                continue
            clip = preprocess_input(clip)
            
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
        if(predictions[p] >= 0.05):
            start = p
            break
    for p in range(len(predictions)-1, -1, -1):
        if(predictions[p] >= 0.05):
            end = p
            break
    start = int(start/fps)
    end = int(end/fps)
    print(start, end)
    # print(predictions)
    save_path = os.path.join(cfg.output_folder, video_name + '.gif')
    # np.savetxt('data.csv',predictions,delimiter=',')
    # visualize predictions
    # visualize_predictions(cfg.sample_video_path, predictions, save_path)
    print("GIF saved")
    return start,end

def logins(request):
    # logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home:index'))
        
        return  HttpResponseRedirect(reverse('home:index'))

def logouts(request):
    logout(request)
    return  HttpResponseRedirect(reverse('home:index'))



