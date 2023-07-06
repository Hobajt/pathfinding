import numpy as np
from math import inf
import heapq

class AStar:
    def __init__(self, arr, src, dst, early_out = False, mod = 0) -> None:
        self.src = src
        self.dst = dst
        self.h, self.w = arr.shape[:2]
        self.early_out = early_out

        heuristics = [self.H_octile, self.H_manhattan, self.H_euclidean]
        self.H = heuristics[mod]

        self.vis = np.zeros((self.h, self.w), dtype=np.uint8)

        self.arr = np.full((self.h, self.w), np.inf, dtype=np.float32)
        self.arr[arr == 1] = -1

        self.arr[src[0],src[1]] = 0

        self.open = [(self.H(src), 0,*src)]

        self.img = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.img[src[0],src[1]] = [0,0,255]
        self.img[dst[0],dst[1]] = [0,255,0]
        self.img[arr == 1] = [100,100,100]

        self.it = 0
        self.mean_len = 0
    
    def H_euclidean(self, pos):
        return np.sqrt((pos[0]-self.dst[0])**2 + (pos[1]-self.dst[1])**2)

    def H_manhattan(self, pos):
        return np.abs((pos[0]-self.dst[0]) + (pos[1]-self.dst[1]))
    
    def H_octile(self, pos):
        dx = np.abs(pos[0]-self.dst[0])
        dy = np.abs(pos[1]-self.dst[1])
        return 1*(dx+dy) + (1.141421 - 2) * min(dx,dy)
    
    def step(self):
        if len(self.open) < 1:
            return False
        self.it += 1
        self.mean_len += len(self.open)

        h,d,y,x = heapq.heappop(self.open)

        if self.vis[y,x] != 0 or self.arr[y,x] < 0:
            return True

        if np.float32(d) > self.arr[y,x]:
            print("O KURWA", np.float32(d), self.arr[y,x])
            exit(1)
        self.arr[y,x] = d
        self.vis[y,x] = 1

        if self.early_out and (y,x) == self.dst:
            self.open = []
            return

        d1,d2 = d + 1, d + np.sqrt(2)
        neighbors = [
            (d2,y-1,x-1),
            (d1,y-1,x+0),
            (d2,y-1,x+1),
            (d1,y+0,x-1),
            (d1,y+0,x+1),
            (d2,y+1,x-1),
            (d1,y+1,x+0),
            (d2,y+1,x+1),
        ]
        for entry in neighbors:
            d,y,x = entry
            if y < 0 or x < 0 or y >= self.h or x >= self.w:
                continue
            if self.arr[y,x] < 0 or (self.vis[y,x] != 0 and d >= self.arr[y,x]) or (d > self.arr[y,x] and self.arr[y,x] < np.inf):
                continue
            h = self.H((y,x,))
            self.arr[y,x] = d
            heapq.heappush(self.open, (h+d,d,y,x,))
        return True

    def get_path(self):
        pos = self.dst
        path = []
        while pos != self.src:
            path.append(pos)
            y,x = pos
            patch = np.array(self.arr[y-1:y+2,x-1:x+2])
            patch[patch < 0] = np.inf
            idx = np.unravel_index(np.argmin(patch), patch.shape)
            idx = [x-1 for x in idx]
            pos = y+idx[0],x+idx[1]
            # print(pos, idx)
            # print(patch)
        return path

    def path_cost(self):
        path = self.get_path()
        d = 0
        for y,x in path:
            d += self.arr[y,x]
        return d

    def draw(self):
        img = np.array(self.img)

        d_pos = (self.arr != np.inf) * (self.arr > 0)
        d_max = max(self.arr[d_pos])
        d_max = d_max if d_max > 10 else 10

        val = self.arr[d_pos]/d_max
        val = np.clip(val**(2.2), 0.0, 1.0) #gamma to highlight distance differences
        img[d_pos,2] = val * 255

        return img

    def draw_final(self):
        img = self.draw()

        path = self.get_path()

        for y,x in path:
            img[y,x] = [0, 215, 255]
        
        img[self.src[0],self.src[1]] = [255,0,0]
        img[self.dst[0],self.dst[1]] = [0,255,0]

        return img
