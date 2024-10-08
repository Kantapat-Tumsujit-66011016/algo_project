import pygame
import random

# Constants for the visual interface
WINDOW_SIZE = 500
BACKGROUND_COLOR = (230, 230, 250)  # Lavender background
TILE_COLOR = (100, 100, 255)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 60
BUTTON_FONT_SIZE = 30
FPS = 60  # Increased FPS for smoother transitions
PADDING = 5
TURN_COUNT_HEIGHT = 75  # Height allocated for the turn count display
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# Initialize Pygame
pygame.init()
font = pygame.font.SysFont('Arial', FONT_SIZE)
button_font = pygame.font.SysFont('Arial', BUTTON_FONT_SIZE)
clock = pygame.time.Clock()

class PuzzleNode:
    def __init__(self, n, state):
        self.n = n
        self.tablesize = n ** 2
        self.state = state

    def draw(self, screen, tile_positions):
        tile_size = (WINDOW_SIZE) // self.n
        for i in range(self.n):
            for j in range(self.n):
                val = self.state[i][j]
                if val != 0:
                    x, y = tile_positions[val]
                    self.draw_tile(screen, x, y, tile_size, val)

    def draw_tile(self, screen, x, y, tile_size, value):
        pygame.draw.rect(screen, (50, 50, 150), (x, y, tile_size, tile_size), border_radius=15)
        pygame.draw.rect(screen, TILE_COLOR, (x + PADDING, y + PADDING, tile_size - PADDING * 2, tile_size - PADDING * 2), border_radius=10)
        text = font.render(str(value), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
        screen.blit(text, text_rect)

    def get_empty_position(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] == 0:
                    return (i, j)

def is_solvable(puzzle):
    flat_puzzle = [tile for row in puzzle for tile in row if tile != 0]
    inversions = 0
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j]:
                inversions += 1
    return inversions % 2 == 0

def generate_random_puzzle(n):
    puzzle = list(range(n * n))
    while True:
        random.shuffle(puzzle)
        puzzle_2d = [puzzle[i:i + n] for i in range(0, len(puzzle), n)]
        if puzzle_2d[-1][-1] != 0:
            zero_pos = puzzle.index(0)
            puzzle[zero_pos], puzzle[-1] = puzzle[-1], puzzle[zero_pos]
            puzzle_2d = [puzzle[i:i + n] for i in range(0, len(puzzle), n)]
        if is_solvable(puzzle_2d):
            return puzzle_2d

def goalstate(state):
    n = len(state)
    flat_goallist = list(range(1, n ** 2)) + [0]
    goal = [flat_goallist[i:i + n] for i in range(0, n ** 2, n)]
    return goal

def moves(inputs, n):
    storage = []
    move = [row[:] for row in inputs]
    i = next(index for index, row in enumerate(move) if 0 in row)
    j = move[i].index(0)

    if i > 0:  # Move up
        move[i][j], move[i - 1][j] = move[i - 1][j], move[i][j]
        storage.append([row[:] for row in move])
        move[i][j], move[i - 1][j] = move[i - 1][j], move[i][j]

    if i < n - 1:  # Move down
        move[i][j], move[i + 1][j] = move[i + 1][j], move[i][j]
        storage.append([row[:] for row in move])
        move[i][j], move[i + 1][j] = move[i + 1][j], move[i][j]

    if j > 0:  # Move left
        move[i][j], move[i][j - 1] = move[i][j - 1], move[i][j]
        storage.append([row[:] for row in move])
        move[i][j], move[i][j - 1] = move[i][j - 1], move[i][j]

    if j < n - 1:  # Move right
        move[i][j], move[i][j + 1] = move[i][j + 1], move[i][j]
        storage.append([row[:] for row in move])
        move[i][j], move[i][j + 1] = move[i][j + 1], move[i][j]

    return storage

def Manhattan_heuristic(state):
    flat_statelist = [item for sublist in state for item in sublist]
    mandistance = 0
    for index, element in enumerate(flat_statelist):
        if element == 0:
            continue
        goal_x, goal_y = divmod(element - 1, len(state[0]))
        curr_x, curr_y = divmod(index, len(state[0]))
        mandistance += abs(goal_x - curr_x) + abs(goal_y - curr_y)
    return mandistance

def Astar(start, finish, heuristic):
    n = len(start)
    pathstorage = [[heuristic(start), start]]
    expanded = []
    expanded_nodes = 0

    while pathstorage:
        i = 0
        for j in range(1, len(pathstorage)):
            if pathstorage[i][0] > pathstorage[j][0]:
                i = j
        path = pathstorage.pop(i)
        current_node = path[-1]

        if current_node == finish:
            return expanded_nodes, len(path), path

        if current_node in expanded:
            continue

        expanded.append(current_node)

        for next_move in moves(current_node, n):
            if next_move in expanded:
                continue
            newpath = [path[0] + heuristic(next_move) - heuristic(current_node)] + path[1:] + [next_move]
            pathstorage.append(newpath)

        expanded_nodes += 1

    return expanded_nodes, 0, []

def solvePuzzle(n, state, heuristic):
    goal = goalstate(state)
    steps, frontierSize, solutions = Astar(state, goal, heuristic)
    return steps, frontierSize, solutions

def initialize_tile_positions(n, state):
    tile_size = (WINDOW_SIZE) // n
    tile_positions = {}
    for i in range(n):
        for j in range(n):
            val = state[i][j]
            if val != 0:
                tile_positions[val] = (j * tile_size, i * tile_size)
    return tile_positions

def draw_button(screen, text, x, y, width, height, color, font, text_color=(0, 0, 0)):
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def is_puzzle_solved(puzzle):
    """Check if the puzzle is solved (goal state) with 0 (empty tile) in the last position."""
    n = len(puzzle)
    # Create the solved state
    solved_state = goalstate(puzzle)
    return puzzle == solved_state  # Check if the current puzzle matches the goal state

def display_win_message(screen):
    """Display the 'You Win!' message on the screen."""
    win_font = pygame.font.SysFont('Arial', 80)
    win_text = win_font.render("You Win!", True, (0, 255, 0))  # Green text
    win_rect = win_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(win_text, win_rect)
    pygame.display.flip()
    pygame.time.delay(2000)  # Show the message for 2 seconds

def main():
    n = 3
    random_puzzle = generate_random_puzzle(n)
    solved_puzzle = goalstate(random_puzzle)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + TURN_COUNT_HEIGHT))
    pygame.display.set_caption("Sliding Puzzle Game")

    steps, frontierSize, solutions = solvePuzzle(n, random_puzzle, Manhattan_heuristic)
    solution_steps = solutions[1:]

    tile_positions = initialize_tile_positions(n, random_puzzle)

    running = True
    step_idx = 0
    animating = False
    turn_count = 0
    manual_mode = True
    puzzle_solved = False  # To track whether the puzzle is solved
    tile_size = WINDOW_SIZE // n

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Draw buttons and turn count in a single line
        draw_button(screen, "Reset", 20, WINDOW_SIZE + 10, BUTTON_WIDTH, BUTTON_HEIGHT, (173, 216, 230), button_font)
        turn_count_text = button_font.render(f"Turns: {turn_count}", True, (0, 0, 0))
        screen.blit(turn_count_text, (WINDOW_SIZE // 2 - turn_count_text.get_width() // 2, WINDOW_SIZE + 25))
        draw_button(screen, "Auto Solve", WINDOW_SIZE - 170, WINDOW_SIZE + 10, BUTTON_WIDTH, BUTTON_HEIGHT, (173, 216, 230), button_font)

        # Current state depends on manual or auto-solve mode
        current_state = random_puzzle if manual_mode else solution_steps[step_idx] if step_idx < len(solution_steps) else solved_puzzle

        puzzle_node = PuzzleNode(n, current_state)
        puzzle_node.draw(screen, tile_positions)

        # Check if the puzzle is solved after each move and before displaying "You Win!"
        if is_puzzle_solved(random_puzzle) and not puzzle_solved:
            pygame.display.flip()  # Render the final state of the puzzle
            pygame.time.delay(500)  # Short delay before the "You Win!" message
            display_win_message(screen)  # Display "You Win!" message
            puzzle_solved = True  # Mark puzzle as solved

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if 20 < x < 20 + BUTTON_WIDTH and WINDOW_SIZE + 10 < y < WINDOW_SIZE + 10 + BUTTON_HEIGHT:
                    draw_button(screen, "Reset", 20, WINDOW_SIZE + 10, BUTTON_WIDTH, BUTTON_HEIGHT, (173, 196, 230), button_font)
                    pygame.display.flip()
                    pygame.time.delay(100)

                    random_puzzle = generate_random_puzzle(n)
                    tile_positions = initialize_tile_positions(n, random_puzzle)
                    steps, frontierSize, solutions = solvePuzzle(n, random_puzzle, Manhattan_heuristic)
                    solution_steps = solutions[1:]
                    step_idx = 0
                    turn_count = 0
                    manual_mode = True
                    puzzle_solved = False  # Reset puzzle solved state

                if WINDOW_SIZE - 170 < x < WINDOW_SIZE - 170 + BUTTON_WIDTH and WINDOW_SIZE + 10 < y < WINDOW_SIZE + 10 + BUTTON_HEIGHT:
                    draw_button(screen, "Auto Solve", WINDOW_SIZE - 170, WINDOW_SIZE + 10, BUTTON_WIDTH, BUTTON_HEIGHT, (173, 196, 230), button_font)
                    pygame.display.flip()
                    pygame.time.delay(100)

                    manual_mode = False
                    animating = True
                    step_idx = 0

                if manual_mode and not puzzle_solved:  # Allow clicks only if not solved
                    clicked_tile_x = x // tile_size
                    clicked_tile_y = y // tile_size

                    if clicked_tile_x < n and clicked_tile_y < n:
                        clicked_tile_value = random_puzzle[clicked_tile_y][clicked_tile_x]
                        empty_pos = puzzle_node.get_empty_position()
                        empty_i, empty_j = empty_pos

                        if (clicked_tile_y == empty_i and abs(clicked_tile_x - empty_j) == 1) or (clicked_tile_x == empty_j and abs(clicked_tile_y - empty_i) == 1):
                            # Swap clicked tile with the empty tile
                            random_puzzle[empty_i][empty_j], random_puzzle[clicked_tile_y][clicked_tile_x] = random_puzzle[clicked_tile_y][clicked_tile_x], random_puzzle[empty_i][empty_j]
                            tile_positions = initialize_tile_positions(n, random_puzzle)
                            turn_count += 1
                            pygame.display.flip()  # Ensure the tile swap is rendered

        if not manual_mode and animating and not puzzle_solved:
            if step_idx < len(solution_steps):
                # Update the puzzle state step by step in auto-solve mode
                random_puzzle = solution_steps[step_idx]
                tile_positions = initialize_tile_positions(n, random_puzzle)
                turn_count += 1  # Increment turn count in auto-solve mode
                step_idx += 1
                pygame.display.flip()  # Render each step of the solution
            else:
                animating = False
                manual_mode = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
