import pygame
import random

# Constants for the visual interface
WINDOW_SIZE = 500
BACKGROUND_COLOR = (230, 230, 250)  # Lavender background
TILE_COLOR = (100, 100, 255)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 60
FPS = 60  # Increased FPS for smoother transitions
PADDING = 5
SLIDE_SPEED = 20  # Speed of tile sliding (larger number = faster)
TURN_COUNT_HEIGHT = 75  # Height allocated for the turn count display

# Initialize Pygame
pygame.init()
font = pygame.font.SysFont('Arial', FONT_SIZE)
clock = pygame.time.Clock()

class PuzzleNode:
    def __init__(self, n, state):
        self.n = n
        self.tablesize = n ** 2
        self.state = state

    def draw(self, screen, tile_positions):
        # Draws the puzzle grid in pygame using the positions from the tile_positions list
        tile_size = (WINDOW_SIZE) // self.n
        for i in range(self.n):
            for j in range(self.n):
                val = self.state[i][j]
                if val != 0:
                    x, y = tile_positions[val]  # Get the current position of the tile
                    self.draw_tile(screen, x, y, tile_size, val)

    def draw_tile(self, screen, x, y, tile_size, value):
        # Draw a tile with rounded corners and a shadow effect
        pygame.draw.rect(screen, (50, 50, 150), (x, y, tile_size, tile_size), border_radius=15)
        pygame.draw.rect(screen, TILE_COLOR, (x + PADDING, y + PADDING, tile_size - PADDING * 2, tile_size - PADDING * 2), border_radius=10)
        text = font.render(str(value), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
        screen.blit(text, text_rect)

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
        
        # Ensure that 0 is at the last position
        if puzzle_2d[-1][-1] != 0:
            # Swap the last element with the position of 0
            zero_pos = puzzle.index(0)
            puzzle[zero_pos], puzzle[-1] = puzzle[-1], puzzle[zero_pos]
            puzzle_2d = [puzzle[i:i + n] for i in range(0, len(puzzle), n)]
        
        if is_solvable(puzzle_2d):
            return puzzle_2d

def goalstate(state):
    n = len(state)
    flat_goallist = list(range(1, n ** 2)) + [0]  # Ensure 0 is last
    goal = [flat_goallist[i:i + n] for i in range(0, n ** 2, n)]
    return goal

def moves(inputs, n):
    storage = []
    move = [row[:] for row in inputs]  # Deep copy of the current state
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
            continue  # Ignore the empty tile
        goal_x, goal_y = divmod(element - 1, len(state[0]))  # Adjusted for 0 indexing
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

def update_tile_positions(n, state, prev_state, tile_positions):
    # Updates the positions of the tiles for smooth transitions
    tile_size = (WINDOW_SIZE) // n
    for i in range(n):
        for j in range(n):
            val = state[i][j]
            if val != 0:
                prev_i, prev_j = [(row, col) for row in range(n) for col in range(n) if prev_state[row][col] == val][0]
                target_x, target_y = j * tile_size, i * tile_size
                current_x, current_y = tile_positions[val]

                # Calculate how much the tile should move towards its target
                delta_x = target_x - current_x
                delta_y = target_y - current_y

                # Move the tile towards the target by SLIDE_SPEED pixels per frame
                if abs(delta_x) < SLIDE_SPEED:
                    current_x = target_x
                else:
                    current_x += SLIDE_SPEED if delta_x > 0 else -SLIDE_SPEED

                if abs(delta_y) < SLIDE_SPEED:
                    current_y = target_y
                else:
                    current_y += SLIDE_SPEED if delta_y > 0 else -SLIDE_SPEED

                # Update the position in the tile_positions dictionary
                tile_positions[val] = (current_x, current_y)

def initialize_tile_positions(n, state):
    # Initializes the position of the tiles based on their grid location
    tile_size = (WINDOW_SIZE) // n
    tile_positions = {}
    for i in range(n):
        for j in range(n):
            val = state[i][j]
            if val != 0:
                tile_positions[val] = (j * tile_size, i * tile_size)
    return tile_positions

def main():
    n = 3
    random_puzzle = generate_random_puzzle(n)

    print("Generated random puzzle:")
    for row in random_puzzle:
        print(row)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + TURN_COUNT_HEIGHT))
    pygame.display.set_caption("Puzzle Solver with Swipe Transition")

    steps, frontierSize, solutions = solvePuzzle(n, random_puzzle, Manhattan_heuristic)
    solution_steps = solutions[1:]

    tile_positions = initialize_tile_positions(n, random_puzzle)

    running = True
    step_idx = 0
    animating = False
    turn_count = 0  # Initialize turn count

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Draw the puzzle grid
        if step_idx < len(solution_steps):
            current_state = solution_steps[step_idx]
            if step_idx == 0:
                prev_state = random_puzzle
            else:
                prev_state = solution_steps[step_idx - 1]
        else:
            current_state = goalstate(random_puzzle)

        # Update tile positions for smooth swipe transition
        if animating:
            update_tile_positions(n, current_state, prev_state, tile_positions)

        # Check if animation is done
        if tile_positions == initialize_tile_positions(n, current_state):
            animating = False
            if step_idx < len(solution_steps):
                turn_count += 1  # Increment turn count only when a valid move is made
            step_idx += 1

        puzzle_node = PuzzleNode(n, current_state)
        puzzle_node.draw(screen, tile_positions)

        # Display turn count
        turn_text = font.render(f"Turns: {turn_count}", True, (0, 0, 0))  # Black text
        turn_background = pygame.Surface((WINDOW_SIZE, TURN_COUNT_HEIGHT))  # Background for the turn count
        turn_background.fill((255, 255, 255))  # White background
        screen.blit(turn_background, (0, WINDOW_SIZE))  # Draw background
        screen.blit(turn_text, (10, WINDOW_SIZE + 10))  # Draw turn count text

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Start animating the next state
        if not animating and step_idx < len(solution_steps):
            animating = True

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
