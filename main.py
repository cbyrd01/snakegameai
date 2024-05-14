import asyncio
import pygame
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
AI_BLUE = (0, 255, 255)
AI_GREEN = (0, 255, 128)
AI_BACKGROUND = (0, 0, 64)
AI_RED = (255, 0, 0)
WALL_COLOR = (100, 100, 100)

# Set display dimensions
DIS_WIDTH = 800
DIS_HEIGHT = 600
SCORE_DISPLAY_HEIGHT = 40

# Set snake block size
SNAKE_BLOCK = 10

# Create display
dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
pygame.display.set_caption('AI Themed Snake Game by ChatGPT')

# Create clock object
clock = pygame.time.Clock()

# Define font styles
font_style = pygame.font.SysFont("bahnschrift", 20)
score_font = pygame.font.SysFont("comicsansms", 20)

# Default menu options
difficulty = 3
goal_score = 25
player1_type = "Human"
player2_type = "AI"
num_walls = 10

def draw_snake(snake_block, snake_list, color):
    for block in snake_list:
        pygame.draw.rect(dis, color, [block[0], block[1], snake_block, snake_block])

def display_message(msg, color, y_displace=0):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [DIS_WIDTH / 6, DIS_HEIGHT / 3 + y_displace])

def display_score(score, player, player_type):
    player_text = f"{player_type} {player}: {score}"
    value = score_font.render(player_text, True, AI_GREEN)
    if player == 1:
        dis.blit(value, [10, 10])
    else:
        dis.blit(value, [DIS_WIDTH - 200, 10])

def relocate_snake(snake_list, walls, other_snake):
    while True:
        new_x = round(random.randrange(SNAKE_BLOCK, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
        new_y = round(random.randrange(SCORE_DISPLAY_HEIGHT + SNAKE_BLOCK, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
        if [new_x, new_y] not in walls and [new_x, new_y] not in other_snake:
            break
    snake_list.clear()
    snake_list.append([new_x, new_y])
    return new_x, new_y

def create_boundary_walls():
    walls = []
    for x in range(0, DIS_WIDTH, SNAKE_BLOCK):
        walls.append([x, SCORE_DISPLAY_HEIGHT])
        walls.append([x, DIS_HEIGHT - SNAKE_BLOCK])
    for y in range(SCORE_DISPLAY_HEIGHT, DIS_HEIGHT, SNAKE_BLOCK):
        walls.append([0, y])
        walls.append([DIS_WIDTH - SNAKE_BLOCK, y])
    return walls

def create_random_walls(num_walls, existing_walls):
    walls = []
    while len(walls) < num_walls:
        wall_length = random.randint(2, 5)
        orientation = random.choice(['horizontal', 'vertical'])
        if orientation == 'horizontal':
            start_x = round(random.randrange(SNAKE_BLOCK, DIS_WIDTH - SNAKE_BLOCK * (wall_length + 1)) / 10.0) * 10.0
            start_y = round(random.randrange(SCORE_DISPLAY_HEIGHT + SNAKE_BLOCK, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
            new_wall = [[start_x + SNAKE_BLOCK * i, start_y] for i in range(wall_length)]
        else:
            start_x = round(random.randrange(SNAKE_BLOCK, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
            start_y = round(random.randrange(SCORE_DISPLAY_HEIGHT + SNAKE_BLOCK, DIS_HEIGHT - SNAKE_BLOCK * (wall_length + 1)) / 10.0) * 10.0
            new_wall = [[start_x, start_y + SNAKE_BLOCK * i] for i in range(wall_length)]

        # Add random direction change for walls longer than 2 blocks
        if wall_length > 2:
            if random.choice([True, False]):  # Randomly decide if the wall should turn
                turn_index = random.randint(1, wall_length - 2)
                if orientation == 'horizontal':
                    if start_y + SNAKE_BLOCK < DIS_HEIGHT - SNAKE_BLOCK:
                        new_wall = new_wall[:turn_index + 1] + [[new_wall[turn_index][0], new_wall[turn_index][1] + SNAKE_BLOCK * (i + 1)] for i in range(wall_length - turn_index - 1)]
                    else:
                        new_wall = new_wall[:turn_index + 1] + [[new_wall[turn_index][0], new_wall[turn_index][1] - SNAKE_BLOCK * (i + 1)] for i in range(wall_length - turn_index - 1)]
                else:
                    if start_x + SNAKE_BLOCK < DIS_WIDTH - SNAKE_BLOCK:
                        new_wall = new_wall[:turn_index + 1] + [[new_wall[turn_index][0] + SNAKE_BLOCK * (i + 1), new_wall[turn_index][1]] for i in range(wall_length - turn_index - 1)]
                    else:
                        new_wall = new_wall[:turn_index + 1] + [[new_wall[turn_index][0] - SNAKE_BLOCK * (i + 1), new_wall[turn_index][1]] for i in range(wall_length - turn_index - 1)]

        if all(block not in existing_walls and block not in walls for block in new_wall):
            walls.append(new_wall)  # Add the new wall as a distinct wall
    return [block for wall in walls for block in wall]  # Flatten the list of walls

def generate_food(snake1, snake2, walls):
    while True:
        food_x = round(random.randrange(SNAKE_BLOCK, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
        food_y = round(random.randrange(SCORE_DISPLAY_HEIGHT + SNAKE_BLOCK, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
        if [food_x, food_y] not in snake1 and [food_x, food_y] not in snake2 and [food_x, food_y] not in walls:
            break
    return food_x, food_y

def move_ai_snake(x, y, food_x, food_y, x_change, y_change, snake_list, walls, other_snake, recent_positions):
    directions = [[SNAKE_BLOCK, 0], [-SNAKE_BLOCK, 0], [0, SNAKE_BLOCK], [0, -SNAKE_BLOCK]]
    random.shuffle(directions)
    best_direction = [x_change, y_change]
    min_distance = float('inf')

    for direction in directions:
        new_x = x + direction[0]
        new_y = y + direction[1]
        if [new_x, new_y] not in walls and [new_x, new_y] not in snake_list and [new_x, new_y] not in other_snake and (new_x, new_y) not in recent_positions:
            distance = ((food_x - new_x) ** 2 + (food_y - new_y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                best_direction = direction

    x_change, y_change = best_direction
    x += x_change
    y += y_change

    return x, y, x_change, y_change

async def start_menu():
    global difficulty, goal_score, player1_type, player2_type, num_walls

    menu_options = [
        f"Difficulty: {difficulty}",
        f"Goal Score: {goal_score}",
        f"Player 1: {player1_type}",
        f"Player 2: {player2_type}",
        f"Number of Walls: {num_walls}",
        "Start Game"
    ]
    menu_index = 0

    while True:
        dis.fill(BLACK)
        for i, option in enumerate(menu_options):
            color = YELLOW if i == menu_index else WHITE
            display_message(option, color, y_displace=(i * 30 - 50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_options)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if menu_index == 0:  # Difficulty
                        difficulty = (difficulty + (1 if event.key == pygame.K_RIGHT else -1)) % 6
                        if difficulty == 0:
                            difficulty = 1
                        menu_options[0] = f"Difficulty: {difficulty}"
                    elif menu_index == 1:  # Goal Score
                        if event.key == pygame.K_RIGHT:
                            goal_score = min(goal_score + 25, 100)
                        else:
                            goal_score = max(goal_score - 25, 25)
                        menu_options[1] = f"Goal Score: {goal_score}"
                    elif menu_index == 2:  # Player 1 Type
                        player1_type = "AI" if player1_type == "Human" else "Human"
                        menu_options[2] = f"Player 1: {player1_type}"
                    elif menu_index == 3:  # Player 2 Type
                        player2_type = "AI" if player2_type == "Human" else "Human"
                        menu_options[3] = f"Player 2: {player2_type}"
                    elif menu_index == 4:  # Number of Walls
                        if event.key == pygame.K_RIGHT:
                            num_walls = min(num_walls + 1, 50)
                        else:
                            num_walls = max(num_walls - 1, 0)
                        menu_options[4] = f"Number of Walls: {num_walls}"
                elif event.key == pygame.K_RETURN and menu_index == 5:
                    await game_loop()
                    return
        await asyncio.sleep(0)

async def game_loop():
    global difficulty, goal_score, player1_type, player2_type, num_walls

    x1 = DIS_WIDTH / 4
    y1 = DIS_HEIGHT / 2
    x1_change = 0
    y1_change = 0

    x2 = 3 * DIS_WIDTH / 4
    y2 = DIS_HEIGHT / 2
    x2_change = 0
    y2_change = 0

    snake1 = [[x1, y1]]
    snake2 = [[x2, y2]]
    snake1_length = 1
    snake2_length = 1

    boundary_walls = create_boundary_walls()
    random_walls = create_random_walls(num_walls, boundary_walls)
    walls = boundary_walls + random_walls

    food_x, food_y = generate_food(snake1, snake2, walls)

    game_close = False

    # Adjust intervals based on difficulty
    if difficulty == 1:
        move_interval = 75  # Player much faster
        ai_update_interval = 150
    elif difficulty == 2:
        move_interval = 90  # Player a little faster
        ai_update_interval = 125
    elif difficulty == 3:
        move_interval = 100  # Both same speed
        ai_update_interval = 100
    elif difficulty == 4:
        move_interval = 110  # AI a tiny bit faster
        ai_update_interval = 90
    elif difficulty == 5:
        move_interval = 125  # AI a little faster
        ai_update_interval = 75

    last_move_time = pygame.time.get_ticks()
    ai_update_time1 = pygame.time.get_ticks()
    ai_update_time2 = pygame.time.get_ticks()
    recent_positions1 = deque(maxlen=10)
    recent_positions2 = deque(maxlen=10)

    while not game_close:
        delta_time = clock.tick(60) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if player1_type == "Human":
                    if event.key == pygame.K_LEFT and x1_change == 0:
                        x1_change = -SNAKE_BLOCK
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT and x1_change == 0:
                        x1_change = SNAKE_BLOCK
                        y1_change = 0
                    elif event.key == pygame.K_UP and y1_change == 0:
                        x1_change = 0
                        y1_change = -SNAKE_BLOCK
                    elif event.key == pygame.K_DOWN and y1_change == 0:
                        x1_change = 0
                        y1_change = SNAKE_BLOCK

        # Update human player position
        if player1_type == "Human" and pygame.time.get_ticks() - last_move_time >= move_interval:
            x1 += x1_change
            y1 += y1_change
            snake1.append([x1, y1])
            if len(snake1) > snake1_length:
                del snake1[0]

            if [x1, y1] in snake1[:-1] or [x1, y1] in snake2 or [x1, y1] in walls:
                x1, y1 = relocate_snake(snake1, walls, snake2)
                snake1_length = max(1, snake1_length - 1)
            last_move_time = pygame.time.get_ticks()

        # Update AI players
        if player1_type == "AI" and pygame.time.get_ticks() - ai_update_time1 >= ai_update_interval:
            ai_update_time1 = pygame.time.get_ticks()
            x1, y1, x1_change, y1_change = move_ai_snake(x1, y1, food_x, food_y, x1_change, y1_change, snake1, walls, snake2, recent_positions1)
            recent_positions1.append((x1, y1))

            snake1.append([x1, y1])
            if len(snake1) > snake1_length:
                del snake1[0]

            if [x1, y1] in snake1[:-1] or [x1, y1] in snake2 or [x1, y1] in walls:
                x1, y1 = relocate_snake(snake1, walls, snake2)
                snake1_length = max(1, snake1_length - 1)

        if player2_type == "AI" and pygame.time.get_ticks() - ai_update_time2 >= ai_update_interval:
            ai_update_time2 = pygame.time.get_ticks()
            x2, y2, x2_change, y2_change = move_ai_snake(x2, y2, food_x, food_y, x2_change, y2_change, snake2, walls, snake1, recent_positions2)
            recent_positions2.append((x2, y2))

            snake2.append([x2, y2])
            if len(snake2) > snake2_length:
                del snake2[0]

            if [x2, y2] in snake2[:-1] or [x2, y2] in snake1 or [x2, y2] in walls:
                x2, y2 = relocate_snake(snake2, walls, snake1)
                snake2_length = max(1, snake2_length - 1)

        dis.fill(AI_BACKGROUND)

        pygame.draw.rect(dis, GREEN, [food_x, food_y, SNAKE_BLOCK, SNAKE_BLOCK])
        for wall in walls:
            pygame.draw.rect(dis, WALL_COLOR, [wall[0], wall[1], SNAKE_BLOCK, SNAKE_BLOCK])

        draw_snake(SNAKE_BLOCK, snake1, AI_BLUE)
        draw_snake(SNAKE_BLOCK, snake2, AI_RED)
        display_score(snake1_length - 1, 1, player1_type)
        display_score(snake2_length - 1, 2, player2_type)

        pygame.display.update()

        if x1 == food_x and y1 == food_y:
            snake1_length += 1
            food_x, food_y = generate_food(snake1, snake2, walls)
        if x2 == food_x and y2 == food_y:
            snake2_length += 1
            food_x, food_y = generate_food(snake1, snake2, walls)

        if snake1_length - 1 >= goal_score or snake2_length - 1 >= goal_score:
            game_close = True

        await asyncio.sleep(0)  # Important for the async loop

    await end_game()

async def end_game():
    dis.fill(BLACK)
    display_message("Game Over! Press any key to return to the menu", RED)
    pygame.display.update()
    await wait_for_key_press()
    await start_menu()

async def wait_for_key_press():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                return
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(start_menu())
