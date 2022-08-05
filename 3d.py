import numpy as np
import json
from tkinter import *


class Text:
    def __init__(self, canvas, position, string=""):
        self.canvas = canvas
        self.text = canvas.create_text(
            position[0], canvas.winfo_reqheight() - position[1]
        )
        self.string = string
        if callable(string):
            self.update()
        else:
            self.canvas.itemconfig(self.text, text=string)

    def update(self):
        self.canvas.itemconfig(self.text, text=self.string())
        canvas.after(10, self.update)


class Polygon:
    def __init__(self, canvas, points, fill="red"):
        self.canvas = canvas
        self.points = [np.array(x) for x in points]
        self.polygon = canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=fill)


class Camera:
    def __init__(self, canvas, position, direction):
        self.canvas = canvas
        self.position = np.array(position)
        self.direction = np.array(direction)
        self.direction = self.direction / np.linalg.norm(self.direction)
        self.norm = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def rotate(self, matrix):
        self.direction = np.matmul(matrix, self.direction)
        self.direction = self.direction / np.linalg.norm(self.direction)

        self.norm = np.matmul(matrix, self.norm)


def onKeyPress(event):
    speed = 0.5 + 0.001 * (np.random.random() - 0.5)
    if event.char == "w":
        throttle = speed * np.array(
            [
                [np.cos(0), -np.sin(0), 0],
                [np.sin(0), np.cos(0), 0],
                [0, 0, 1],
            ]
        )
        cam.position = cam.position + np.matmul(throttle, cam.direction).T
    elif event.char == "a":
        throttle = speed * np.array(
            [
                [np.cos(-np.pi / 2), -np.sin(-np.pi / 2), 0],
                [np.sin(-np.pi / 2), np.cos(-np.pi / 2), 0],
                [0, 0, 1],
            ]
        )
        cam.position = cam.position + np.matmul(throttle, cam.direction).T
    elif event.char == "s":

        throttle = speed * np.array(
            [
                [np.cos(np.pi), -np.sin(np.pi), 0],
                [np.sin(np.pi), np.cos(np.pi), 0],
                [0, 0, -1],
            ]
        )
        cam.position = cam.position + np.matmul(throttle, cam.direction).T
    elif event.char == "d":
        throttle = speed * np.array(
            [
                [np.cos(np.pi / 2), -np.sin(np.pi / 2), 0],
                [np.sin(np.pi / 2), np.cos(np.pi / 2), 0],
                [0, 0, 1],
            ]
        )
        cam.position = cam.position + np.matmul(throttle, cam.direction).T
    elif event.char == "q":
        cam.position = cam.position + speed * np.array([0, 0, 1])
    elif event.char == "e":
        cam.position = cam.position + speed * np.array([0, 0, -1])


def leftKey(event):
    theta = -np.pi / 36
    matrix = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )

    cam.rotate(matrix)


def rightKey(event):
    theta = np.pi / 36
    matrix = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )

    cam.rotate(matrix)


def downKey(event):
    theta = np.pi / 36
    matrix = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    cam.rotate(matrix)


def upKey(event):
    theta = -np.pi / 36
    matrix = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    cam.rotate(matrix)


polygon_num = 0


def debug():
    string = (
        "polygon: {0}\n".format(polygon_num)
        + "cam dir: {0}\n".format([round(x, 2) for x in cam.direction])
        + "cam pos: {0}\n".format([round(x, 2) for x in cam.position])
        + "cam norm: {0}\n".format([[round(y, 2) for y in x] for x in cam.norm])
    )

    return string


root = Tk()
root.title("")
root.resizable(False, False)

root.bind("<KeyPress>", onKeyPress)
root.bind("<Left>", leftKey)
root.bind("<Right>", rightKey)
root.bind("<Up>", upKey)
root.bind("<Down>", downKey)

canvas = Canvas(root, width=750, height=750)
canvas.pack()

# map load
map_name = input("input map name: ")
f = open(map_name)
map_data = json.load(f)
polygons = []

for polygon in map_data["polygons"]:
    polygons.append(Polygon(canvas, polygon["points"], polygon["fill"]))

cam = Camera(canvas=canvas, position=[0.1, 0.1, 0.1], direction=[1, 0, 0])
debug_text = Text(canvas=canvas, position=[300, 100], string=debug)


def update(cam=cam, polygons=polygons, top=debug_text):
    global polygon_num

    cam_polygons = []
    width = canvas.winfo_reqwidth()
    height = canvas.winfo_reqheight()
    f = 30
    angle = 60 * np.pi / 180

    dx = -cam.position[0]
    dy = -cam.position[1]
    dz = -cam.position[2]

    movement_matrix = np.array(
        [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]]
    )
    inv = np.pad(
        np.linalg.inv(cam.norm), ((0, 1), (0, 1)), "constant", constant_values=0
    )
    inv[3][3] = 1
    rotate_matrix = np.matmul(
        np.array([[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]), inv
    )
    project_matrix = np.array(
        [
            [1 / (f * np.tan(angle)), 0, 0, 0],
            [0, 1 / (f * np.tan(angle)), 0, 0],
            [0, 0, 1 / f, 0],
            [0, 0, 1, 0],
        ]
    )

    total_matrix = np.matmul(project_matrix, np.matmul(rotate_matrix, movement_matrix))

    for element in polygons:

        points = [
            np.matmul(total_matrix, np.append(point, 1)) for point in element.points
        ]

        if all(
            [
                (-1 < point[0] / point[2] < 1)
                and (-1 < point[1] / point[2] < 1)
                and (0 < point[2] < 1)
                for point in points
            ]
        ):
            canvas.itemconfigure(element.polygon, state="normal")
            cam_polygons.append({"points": points, "polygon": element.polygon})
        else:
            canvas.itemconfigure(element.polygon, state="hidden")

    polygon_num = len(cam_polygons)
    cam_polygons.sort(
        key=lambda x: min([point[2] for point in x["points"]]), reverse=True
    )

    for element in cam_polygons:
        points = [point * width / (2 * point[2]) for point in element["points"]]

        # order =====

        canvas.tag_raise(element["polygon"])
        canvas.coords(
            element["polygon"],
            points[0][1] + width / 2,
            height / 2 + points[0][0],
            points[1][1] + width / 2,
            height / 2 + points[1][0],
            points[2][1] + width / 2,
            height / 2 + points[2][0],
        )

    canvas.tag_raise(top)
    canvas.after(10, update)


update()
root.mainloop()
