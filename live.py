# from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
from landmark import detect_landmarks, normalize_landmarks, plot_landmarks
from mediapipe.python.solutions.face_detection import FaceDetection
import numpy as np
from streamlit_webrtc import AudioProcessorBase,RTCConfiguration,VideoProcessorBase,WebRtcMode,webrtc_streamer
from aiortc.contrib.media import MediaPlayer
from PIL import ImageColor
import streamlit as st



# left_blush = [423,280,352,346,347,348,329,355,429] # 
# right_blush = [423,427,411,352,330,280,345,346,347,348,352,329,355,429] # 

left_blush = [423,280,352,346,347,348,329,355,429] # 
right_blush = [203,50,123,117,118,119,100,126,209,198] #119



color = []

option = st.selectbox(
     'How would you like to be contacted?',
     ('color_1', 'color_2', 'color_3', 'color_4', 'color_5'))

if option =='color_1':
    color = [63, 64, 108] 
    co = [206,157,151]
    m = '#BBA6BD'
elif option == 'color_2':
    color = [10, 5, 120]
    m = '#945E9C'
elif option == 'color_3':
    color = [60,60,60]
    m = '#d0b49f'
elif option == 'color_4':
    color = [107, 182, 203]
    m = '#9DB6CC' 
elif option == 'color_5':
    color = [105, 71, 59]
    m = '#a47551'
else :
    color = [45, 15, 5]


colors = st.color_picker('Pick A Color', m)

class VideoProcessor:
    	def recv(self, frame):
         try:
            frm = frame.to_ndarray(format="rgb24")
            ret_landmarks = detect_landmarks(frm, True)
            height, width, _ = frm.shape
            feature_landmarks = None
            feature_landmarks_right = normalize_landmarks(ret_landmarks, height, width, right_blush)
            mask_right = blush_mask(frm, feature_landmarks_right, [0, 0, 100],75)#
            feature_landmarks_left = normalize_landmarks(ret_landmarks, height, width, left_blush)
            mask_left = blush_mask(frm, feature_landmarks_left, [0, 0, 100],75)
            mask = mask_left+mask_right
            output = cv2.addWeighted(frm, 1.0, mask, 0.2, 0.0)
            print('here 1')
            output = cv2.flip(output,1)
            return av.VideoFrame.from_ndarray(output, format='rgb24')
         except:
             VideoProcessor


def blush_mask(src: np.ndarray, points: np.ndarray, color: list, radius: int):
    """
    Given a src image, points of the cheeks, desired color and radius
    Returns a colored mask that can be added to the src
    """

    mask = np.zeros_like(src)  # Create a mask
    mask = cv2.fillPoly(mask, [points], color)  # Mask for the required facial feature
    # Blurring the region, so it looks natural
    # TODO: Get glossy finishes for lip colors, instead of blending in replace the region
    mask = cv2.GaussianBlur(mask, (7, 7), 5)
    return mask


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun4.l.google.com:19302"]}]}
)

webrtc_ctx = webrtc_streamer(
    key="object-detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)
