import cv2
import screeninfo
import glob
import time

screen_1 = screeninfo.get_monitors()[0]
screen_2 = screeninfo.get_monitors()[1]

image_dir = "projector_img/750"
files = glob.glob(image_dir + '/*.png')
files.sort()

windowname1 = "1"
cv2.namedWindow(windowname1, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow(windowname1, screen_1.x, screen_1.y)
cv2.setWindowProperty(windowname1, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

windowname2 = "2"
cv2.namedWindow(windowname2, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow(windowname2, screen_2.x, screen_2.y)
cv2.setWindowProperty(windowname2, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

b_img = cv2.imread(files[0])

flag = 0
for i in files:
    img = cv2.imread(i)
    cv2.imshow(windowname1, img)
    print(i)
    if flag == 0:
        cv2.imshow(windowname2, b_img)
        cv2.waitKey(2000)
        #time.sleep(3)
        flag = 1
    else:
        cv2.waitKey(500)
flag = 0
for i in files:
    img = cv2.imread(i)
    cv2.imshow(windowname2, img)
    print(i)
    if flag == 0:
        cv2.imshow(windowname1, b_img)
        cv2.waitKey(2000)
        #time.sleep(3)
        flag = 1
    else:
        cv2.waitKey(500)



cv2.imshow(windowname1, b_img)
cv2.imshow(windowname2, b_img)
cv2.waitKey(0)

z_img = cv2.imread(files[-1])
cv2.imshow(windowname1, z_img)
cv2.imshow(windowname2, b_img)
cv2.waitKey(0)


cv2.imshow(windowname1, b_img)
cv2.imshow(windowname2, z_img)
cv2.waitKey(0)

cv2.imshow(windowname1, z_img)
cv2.imshow(windowname2, z_img)
cv2.waitKey(0)

cv2.destroyAllWindows()
