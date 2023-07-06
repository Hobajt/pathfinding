import numpy as np
import cv2
import argparse
import pickle

def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument('--width', type=int, default=64)
    args.add_argument('--height', type=int, default=64)

    args.add_argument('--outpath', type=str, default='layout.npy')

    return args.parse_args()

def main(args):
    arr = np.zeros((args.height, args.width), dtype=np.uint8)

    clr_wall = [100,100,100]
    clr_src = [0,0,255]
    clr_dst = [0,255,0]

    ctx = argparse.Namespace(
        running = True,
        brush_size = 1
    )

    def terminate():
        ctx.running = not ctx.running
    
    def display():
        img = np.zeros((args.height, args.width, 3), dtype=np.uint8)
        img[arr == 1] = clr_wall
        img[arr == 2] = clr_src
        img[arr == 3] = clr_dst

        cv2.imshow('img', img)
    
    def write():
        np.save(args.outpath, arr)
        print(f"Layout written to '{args.outpath}'")
    
    def brush_plus():
        ctx.brush_size += 1
    
    def brush_minus():
        ctx.brush_size = (ctx.brush_size-1) if ctx.brush_size > 1 else 1

    def mouse_callback(evt, x, y, flags, params):
        y,x = min(y,args.height),min(x,args.width)
        ctrl, shift = bool(flags & cv2.EVENT_FLAG_CTRLKEY), bool(flags & cv2.EVENT_FLAG_SHIFTKEY)

        bl = ctx.brush_size // 2
        br = ctx.brush_size - bl

        if bool(flags & cv2.EVENT_FLAG_LBUTTON):
            value = min(1 + ctrl + 2*shift, 3)
            if value != 1:
                arr[arr == value] = 0
                bl,br = 0,1
            arr[y-bl:y+br,x-bl:x+br] = value
        elif bool(flags & cv2.EVENT_FLAG_RBUTTON):
            arr[y-bl:y+br,x-bl:x+br] = 0
        display()

    handlers = {
        ord('q'): terminate,
        ord('w'): write,
        ord('e'): brush_minus,
        ord('r'): brush_plus,
    }


    ratio = 1 if (args.width >= 512) else (512/args.width)
    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('img', (int(args.width * ratio), int(args.height * ratio)))
    cv2.setMouseCallback('img', mouse_callback)

    while ctx.running:
        display()

        key = cv2.waitKey(0)
        if key in handlers:
            handlers[key]()

if __name__ == "__main__":
    main(parse_args())
