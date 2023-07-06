import numpy as np
import cv2
from math import inf
import argparse, os, time

from algs import Dijkstra, AStar

alg_choices = ['dijkstra', 'astar']
algs = [Dijkstra, AStar]

def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument('--alg', type=str, default=alg_choices[0], choices=alg_choices)
    args.add_argument('--mod', type=int, default=0, help='Modification param for individual algorithms.')

    args.add_argument('--bench', action='store_true', help='Run timing benchmark (disables animation).')
    args.add_argument('--reps', type=int, default=int(1e2), help='Timing bench repetition count.')

    args.add_argument('--no_anim', action='store_true', help='Disabled animations.')
    args.add_argument('-s', '--step', type=int, default=10, help='Animation step (render every Nth frame) - defines animation speed.')
    args.add_argument('-l', '--layout', type=str, default=None, help='Path to a layout file')

    args.add_argument('-e', '--early_out', action='store_true', help="Don't compute for all the tiles, only work until the destination is reached.")

    args = args.parse_args()

    args.no_anim = args.no_anim or args.bench
    args.animated = not args.no_anim

    return args


def default_layout():
    h,w = 64,64
    arr = np.zeros((h,w), dtype=np.uint8)
    arr[15:35,35:40] = 1
    arr[30:35,20:40] = 1
    src = 5,5
    dst = 55,55
    return arr,src,dst

def main(args):
    if args.layout is not None:
        if not os.path.exists(args.layout):
            print("Invalid layout file provided, using deafult")
            arr,src,dst = default_layout()
        else:
            arr = np.load(args.layout)
            src = tuple([x[0] for x in np.where(arr == 2)])
            dst = tuple([x[0] for x in np.where(arr == 3)])
            arr[arr > 1] = 0
            print(f"Using layout from '{args.layout}'")
    else:
        print("Using default layout.")
        arr,src,dst = default_layout()
    
    Alg = algs[alg_choices.index(args.alg)]
    d = Alg(arr, src, dst, args.early_out, args.mod)

    if not args.bench:
        cv2.namedWindow('img', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('img', (512,512))

    if args.animated:
        running = True
        i = 0
        n = 0
        while running and d.step():
            i += 1
            if i % args.step != 0:
                continue
            img = d.draw()
            n += 1

            cv2.imshow('img', img)
            # cv2.imwrite(f'out/astar_{n}.jpg', cv2.resize(img, (256, 256), interpolation=cv2.INTER_NEAREST))
            key = cv2.waitKey(1)
            if key == ord('q'):
                running = False
            elif key == ord(' '):
                cv2.waitKey(0)
    elif args.bench:
        start = time.time()
        for i in range(args.reps):
            d = Alg(arr, src, dst, args.early_out, args.mod)
            while d.step():
                pass
        end = time.time()
        print(f"Time elapsed: {(end-start):.3f}s ({1e3*((end-start)/args.reps):.3f}ms on avg, {args.reps} reps)")
    else:
        while d.step():
            pass

    n += 1
    if not args.bench:
        if not (args.animated and not running):
            print("Iterations:", d.it)
            print("Mean list length:", d.mean_len / d.it)
            print("Path cost:", d.path_cost())

            img = d.draw_final()
            cv2.imshow('img', img)
            # cv2.imwrite(f'out/astar_{n}.jpg', cv2.resize(img, (256, 256), interpolation=cv2.INTER_NEAREST))
            cv2.waitKey(0)
        else:
            print("Canceled.")

if __name__ == "__main__":
    main(parse_args())
