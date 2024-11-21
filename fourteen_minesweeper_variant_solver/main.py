from pywinauto import Application
import win32gui
import cv2
from cv2.typing import MatLike
import numpy as np
import os
from pathlib import Path
from fourteen_minesweeper_variant_solver.data import Cell, Game
from fourteen_minesweeper_variant_solver.rule import *
from fourteen_minesweeper_variant_solver.solver import solve

def no_double_click_time():
    return 0

win32gui.GetDoubleClickTime = no_double_click_time

app = Application().connect(title_re='Minesweeper Variants 2')
mv2 = app.window(title_re='Minesweeper Variants 2')
mv2.set_focus()
mv2.capture_as_image().save('screenshot.png')

image = cv2.imread('screenshot.png')
original_size = image.shape[:2]
image = cv2.resize(image, (1600, 900))
# Preprocess the image for better OCR
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)

def find_board(image: np.ndarray):
    # Find the game board
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    board_contour = None
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # Check if the contour has 4 sides and is nearly square
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.9 <= aspect_ratio <= 1.1:  # Check if nearly square
                board_contour = contour
                break
            break
    if board_contour is None:
        print('Board not detected')
        grid_image = binary.copy()
        grid_image = cv2.cvtColor(grid_image, cv2.COLOR_GRAY2BGR)
        grid_image = cv2.drawContours(grid_image, contours, -1, (0, 255, 0), 2)
        cv2.imshow('grid_image', grid_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        exit()
    return board_contour

board_contour = find_board(binary)
x, y, w, h = cv2.boundingRect(board_contour)
board = binary[y - 10:y + h + 10, x - 10:x + w + 10]

def find_cells(board: MatLike):
    # Identify the number of cells per row and column
    cell_contours, _ = cv2.findContours(board, cv2.RETR_LIST , cv2.CHAIN_APPROX_SIMPLE)
    cell_contours = [c for c in cell_contours if cv2.contourArea(c) > 3500 and cv2.contourArea(c) < 4500]
    cell_contours = sorted(cell_contours, key=lambda c: tuple(reversed(cv2.boundingRect(c)[:2])))
    grid_size = int(np.sqrt(len(cell_contours)))
    if grid_size * grid_size != len(cell_contours):
        print(f'Grid size not detected correctly, {len(cell_contours)} cells detected')
        grid_image = board.copy()
        grid_image = cv2.cvtColor(grid_image, cv2.COLOR_GRAY2BGR)
        grid_image = cv2.drawContours(grid_image, cell_contours, -1, (0, 255, 0), 2)
        cv2.imshow('grid_image', grid_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        exit()
    return cell_contours

cell_contours = find_cells(board)
grid_size = int(np.sqrt(len(cell_contours)))

# Recognize content in each cell
templates = {}
for template_path in Path('templates').glob('*.png'):
    label = template_path.stem
    template_image = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    template_image = cv2.bitwise_not(template_image)
    template_image = cv2.morphologyEx(template_image, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    templates[label] = template_image

def recognize_text(board: np.ndarray, cell_contours: MatLike) -> list[list[Cell]]:
    recognized_grid: list[Cell] = []
    print(list(cv2.boundingRect(c) for c in cell_contours))
    result_image = board.copy()
    result_image = cv2.cvtColor(result_image, cv2.COLOR_GRAY2BGR)
    for cell_contour in cell_contours:
        # Extract cell region
        x, y, w, h = cv2.boundingRect(cell_contour)
        cell = board[y+2:y + h-2, x+2:x + w-2]
        cell = cv2.morphologyEx(cell, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        cell = cv2.resize(cell, (64, 64))
        
        best_match = None
        best_score = float('inf')
        for label, template in templates.items():
            # Resize template to match the cell's size
            resized_template = cv2.resize(template, (64, 64))
            # Perform template matching
            result = cv2.matchTemplate(cell, resized_template, cv2.TM_SQDIFF)
            min_val, _, _, _ = cv2.minMaxLoc(result)
            if min_val < best_score:
                best_score = min_val
                best_match = label.split('_')[0]
        
        print(f"Best match: {best_match} {best_score}")
        if best_score > 9e6:
            unmatched_cell_path = os.path.join('unknown', f"cell_{len(recognized_grid)}.png")
            cell = cv2.morphologyEx(cell, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            cell = cv2.morphologyEx(cell, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            cell = cv2.bitwise_not(cell)
            cv2.imwrite(unmatched_cell_path, cell)
            unmatched_cell_path = os.path.join('unknown', f"original_{len(recognized_grid)}.png")
            cell = board[y+2:y + h-2, x+2:x + w-2]
            cell = cv2.bitwise_not(cell)
            cv2.imwrite(unmatched_cell_path, cell)
            print(f"Low-confidence match saved: {best_match} {best_score} {unmatched_cell_path}")
            recognized_grid.append(Cell.UNKNOWN)
        else:
            assert best_match is not None
            if best_match == 'flag':
                cell_content = Cell.MINE
            elif best_match == 'hidden':
                cell_content = Cell.HIDDEN
            elif best_match == 'blank':
                cell_content = Cell.UNKNOWN
            else:
                cell_content = Cell.basic(int(best_match))
            recognized_grid.append(cell_content)
            result_image = cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            result_image = cv2.putText(result_image, best_match.strip(), (x, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    grid_array = [[recognized_grid[i + j * grid_size] for i in range(grid_size)] for j in range(grid_size)]
    # print(grid_array)
    # cv2.imshow('result_image', result_image)
    # cv2.waitKey(0)
    return grid_array

board_x, board_y, _, _ = cv2.boundingRect(board_contour)
board_x -= 10
board_y -= 10
solved = False
while not solved:
    mv2.capture_as_image().save('screenshot.png')
    image = cv2.imread('screenshot.png')
    image = cv2.resize(image, (1600, 900))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
    x, y, w, h = cv2.boundingRect(board_contour)
    board = binary[y - 10:y + h + 10, x - 10:x + w + 10]

    grid_array = recognize_text(board, cell_contours)
    print(grid_array)
    res = solve(Game(
        board=grid_array,
        # total_mines=[10, 14, 20, 26][grid_size - 5],
        total_mines=[8, 12, 16, 24][grid_size - 5],
        rules=[
            # HorizontalRule(),
            # ConnectedRule(),
            # SegmentRule(),
            GroupRule(),
        ],
    ))
    print(res)
    solved = res.solved
    if len(res.known_facts) == 0:
        print('No more moves to make')
        break
    # break

    for move in res.known_facts:
        x, y, w, h = cv2.boundingRect(cell_contours[move.row * grid_size + move.column])
        click_x = board_x + x + w // 2
        click_y = board_y + y + h // 2
        click_x = click_x * original_size[1] // 1600
        click_y = click_y * original_size[0] // 900
        if move.is_mine:
            mv2.click_input(coords=(click_x, click_y), button='right')
        else:
            mv2.click_input(coords=(click_x, click_y), button='left')


# mv2.capture_as_image().save('screenshot.png')
# image = cv2.imread('screenshot.png')
# image = cv2.resize(image, (1600, 900))
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# _, binary = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
# next_level_template = cv2.imread('templates/nextlevel.jpg', cv2.IMREAD_GRAYSCALE)
# cv2.imshow('binary', binary)
# results = cv2.matchTemplate(binary, next_level_template, cv2.TM_SQDIFF)
# min_val, _, min_pos, _ = cv2.minMaxLoc(results)
# click_x = min_pos[0] + next_level_template.shape[1] // 2
# click_y = min_pos[1] + next_level_template.shape[0] // 2
# click_x = click_x * original_size[1] // 1600
# click_y = click_y * original_size[0] // 900
# mv2.click_input(coords=(click_x, click_y), button='left')