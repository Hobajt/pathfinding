import cv2
import numpy as np
import os


i = 1
over = 10
end = -1

a = cv2.imread(f'astar_{i}.jpg')
b = cv2.imread(f'dijkstra_{i}.jpg')

a_out,b_out = False, False

while True:
    if os.path.exists(f'astar_{i}.jpg'):
        a = cv2.imread(f'astar_{i}.jpg')
        # a = cv2.resize(a, (256,256), interpolation=cv2.INTER_NEAREST)
    else:
        a_out = True

    if os.path.exists(f'dijkstra_{i}.jpg'):
        b = cv2.imread(f'dijkstra_{i}.jpg')
        # b = cv2.resize(b, (256,256), interpolation=cv2.INTER_NEAREST)
    else:
        b_out = True

    if a_out and b_out:
        if end < 0:
            end = i
        if i-end > over:
            break

    img = np.hstack((a, b))
    cv2.imwrite(f'out_{i}.jpg', img)
    cv2.imshow('img', img)
    cv2.waitKey(1)

    i += 1
print("Done.")
