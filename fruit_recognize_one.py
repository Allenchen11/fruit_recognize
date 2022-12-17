# USAGE
# cd D:\python_workspace\fruit_recognize (the dir path of this file) 
# C:\Users\chen\anaconda3\python.exe .\fruit_recognize_one.py --training fruit_image
#  or    
# python fruit_recognize_one.py --training fruit_image
import cv2 #pip install opencv-contrib-python
import datetime
import argparse
import imutils
from cv2 import (VideoCapture, namedWindow, imshow, waitKey, destroyWindow, imwrite)
from sklearn.neighbors import KNeighborsClassifier #pip3 install -U scikit-learn scipy matplotlib
from skimage import exposure #pip install scikit-image
from skimage import feature
from imutils import paths
import cvzone #pip install cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation #pip install mediapipe


startTime = datetime.datetime.now()
print ("[INFO]proccess start at : "+startTime.strftime("%Y-%m-%d %H:%M:%S"))


# construct the argument parse and parse command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--training", required=True, help="Path to the logos training dataset")
args = vars(ap.parse_args())

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

# loop over the image paths in the training set
for imagePath in paths.list_images(args["training"]):
	# extract the make of the car
	make = imagePath.split("\\")[-2]

	# load the image, convert it to grayscale, and detect edges
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	edged = imutils.auto_canny(gray)

	# find contours in the edge map, keeping only the largest one which
	# is presmumed to be the car logo
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	c = max(cnts, key=cv2.contourArea)

	# extract the logo of the car and resize it to a canonical width
	# and height
	(x, y, w, h) = cv2.boundingRect(c)
	logo = gray[y:y + h, x:x + w]
	logo = cv2.resize(logo, (200, 100))

	# extract Histogram of Oriented Gradients from the logo
	H = feature.hog(logo,orientations=9,pixels_per_cell=(10,10),cells_per_block=(2,2),transform_sqrt=True,block_norm="L1")

	# update the data and labels
	data.append(H)
	labels.append(make)

# "train" the nearest neighbors classifier
print("[INFO] training classifier...")
model = KNeighborsClassifier(n_neighbors=1)
model.fit(data, labels)

print("[INFO] start use cam catch image...")
cam_port = 0
cam = VideoCapture(cam_port)

while(cam.isOpened()):
    result, image = cam.read()

    #remove background
    segmentor = SelfiSegmentation()
    image = segmentor.removeBG(image, (255,255,255), threshold=0.99)
    cv2.imshow('frame', image)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
# show result
if result:
    # saving image in local storage
    imwrite("./test_image/test.png", image)
else:
    print("No image detected. Please! try again")



imagePath = 'test_image/test.png'
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
logo = cv2.resize(gray, (200, 100))

(H, hogImage) = feature.hog(logo,orientations=9,pixels_per_cell=(10,10),cells_per_block=(2,2),transform_sqrt=True,block_norm="L1",visualize=True)
pred = model.predict(H.reshape(1, -1))[0]

hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
hogImage = hogImage.astype("uint8")
cv2.imshow("Test Image", hogImage)

cv2.putText(image, pred.title(), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
		(0, 255, 0), 3)
cv2.imshow("Test Image", image)
cv2.waitKey(0)


endTime = datetime.datetime.now()
print ("[INFO]proccess end at : "+endTime.strftime("%Y-%m-%d %H:%M:%S"))