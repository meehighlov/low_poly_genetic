import random
from random import randint as rnd
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import matplotlib.path as mp
from scipy.spatial import Delaunay
from scipy import ndimage, misc
from collections import defaultdict
import cv2
import time
import genetic.coloring
from smoothing.smooth import Smooth


def color(polygon, pixels):
    # tri = mp.Path(np.array(polygon))
    x = [int(polygon[point][0]) for point in range(len(polygon))]
    y = [int(polygon[point][1]) for point in range(len(polygon))]
    xmax = max(x)
    xmin = min(x)
    ymax = max(y)
    ymin = min(y)
    color_count = defaultdict(int)
    for i in range(xmin, xmax, 1):
        for j in range(ymin, ymax, 1):
            # if tri.contains_point((i, j)):
            color_count[pixels[i, j]] += 1
    max_color = max(color_count.values() or [0])
    # fill_color = None if max_color > 0 else pixels[xmax - 1, ymax - 1]
    fill_color = None
    for key in color_count:
        fill_color = key
        if color_count[key] == max_color:
            return key
    return fill_color


def fitness(original, selected):
    fit = 0
    for i in range(len(original)):
        r = original[i][0] - selected[i][0]
        g = original[i][1] - selected[i][1]
        b = original[i][2] - selected[i][2]
        fit += r*r + g*g + b*b
    return fit


def fitness_(original, selected, points):
    fit = 0
    for i in range(len(points)):
        r = original[points[i][0]][points[i][1]][0] - selected[points[i][0]][points[i][1]][0]
        g = original[points[i][0]][points[i][1]][1] - selected[points[i][0]][points[i][1]][1]
        b = original[points[i][0]][points[i][1]][2] - selected[points[i][0]][points[i][1]][2]
        fit += r*r + b*b + g*g
    return fit


def edges_points(edges):
    xy = []
    left = []
    h, w = edges.shape
    print(h, w)
    for i in range(h):
        for j in range(w):
            if edges[i, j] > 0:
                xy.append((j, i))
            else:
                left.append((j, i))
    return xy, left


def draw_triangles(inp, image, saved, points_amount=0):
    width, height = image.size
    pixels = saved.load()
    layer = Image.new('RGBA', (width, height))
    layer_draw = ImageDraw.Draw(layer)
    key_points = [(0, 0), (0, height), (width, 0), (width, height)]
    # points = key_points + [(rnd(0, width), rnd(0, height)) for _ in range(points_amount)]
    points = inp
    tri = Delaunay(points)
    for i in tri.simplices:
        a = tuple(points[i[0]])
        b = tuple(points[i[1]])
        c = tuple(points[i[2]])
        fill = color([a, b, c], pixels)
        layer_draw.polygon([a, b, c], fill=fill)
    image.paste(layer, mask=layer)
    # image = image.filter(ImageFilter.DETAIL)
    image.show()
    # saved.show()


imp = 'images/me.jpg'
image = Image.open(imp)
image.show()
# edges = image.filter(ImageFilter.BLUR)
# edges = edges.filter(ImageFilter.EDGE_ENHANCE)
# image.filter(ImageFilter.DETAIL).show()
# edgesC = cv2.Canny(cv2.imread(imp), 100, 200)
# Image.fromarray(edgesC).show()
edges = image.filter(ImageFilter.GaussianBlur(radius=5)).filter(ImageFilter.FIND_EDGES).convert('1')
edges.show(title='abcd')
r = edges.load()
# r = edgesC
h, w = image.size
l = []
for i in range(h):
    tmp = []
    for j in range(w):
        tmp.append(r[i, j])
    l.append(tmp)
saved = Image.open(imp)
l = np.array(l)
# draw_triangles(random.sample(l, len(l)//5), image, saved)


s = Smooth(l, 500, (0.2, 0.8), fit=0.5, kernel_size=11)
s.start(100)
r = s.get_binary()

n = []
for i in range(h):
    for j in range(w):
        if r[i, j] > 0:
            n.append((i, j))

draw_triangles(n, image, saved)

