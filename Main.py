import random
import math
import arcade
import os

'''
TO DO: 
- Change / more flashy texts ( Score, asteroids)
- Sounds
- Better health bar
'''


"""
0. VARIABLES: 
- 1. Starting asteroid count
- 2. Scale factor
- 3. Limit of screen space
- 4. Screen width, height
- 5. Title
- 6. Limits
- 7. Margin when you hit screen margins (from left to right from top to bottom)
- 8. These numbers represent "states" that the game can be in
- 9. Asteroid velocity
"""

# 1.
STARTING_ASTEROID_COUNT = 10

# 2.
SCALE = 0.5

# 3.
OFFSCREEN_SPACE = 300

# 4.
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# 5.
SCREEN_TITLE = "Just a random space game"

# 6.
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE

# 7.
VIEWPORT_MARGIN = 20

# 8.
INSTRUCTIONS_PAGE_0 = 0
INSTRUCTIONS_PAGE_1 = 1
GAME_RUNNING = 2
GAME_OVER = 3

# 9.
ASTEROID_SPEED = 7

class TurningSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """

    """
    0. Called each frame
    - 1. Super class 
    - 2. Angle update
    """
    def update(self):

        # 1.
        super().update()

        # 2.
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.
    Derives from arcade.Sprite.
    """

    """ 
    0. Set up the space ship.
    - 1. Call the parent Sprite constructor
    - 2. Player info, angle from parent class
    - 3. Respawn player
    """
    def __init__(self, filename, scale):

        # 1.
        super().__init__(filename, scale)

        # 2.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.05
        self.respawning = 0

        # 3.
        self.respawn()

    """
    0. Respawn function
    - 1. Respawning indicates we are in the middle of respawning (non zero = in the middle of)
    - 2. Center x and y to middle screen
    - 3. Reset player angle
    """
    def respawn(self):

        # 1.
        self.respawning = 1

        # 2.
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2

        # 3.
        self.angle = 0

    """
    0. Update called each game cycle
    - 1. If we are in the middle of respawning (!!!TODO!!!)
    - 2. Speed is incrementally faster with thrust
    - 3. Change x and change y updated with angles
    - 4. We change player position based on change x and change y
    - 5. Call super class
    """
    def update(self):

        # 1.
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 25:
                self.respawning = 0
                self.alpha = 255
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        # 2.
        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # 3.
        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        # 4.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # 5.
        super().update()


class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """
    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0

    def update(self):
        """ Move the asteroid around. """
        super().update()
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT


class BulletSprite(TurningSprite):
    """
    Class that represents a bullet.

    Derives from arcade.TurningSprite which is just a Sprite
    that aligns to its direction.
    """

    """
    0. Update ticks every delta time
    - 1. If bullet is out of bounds kill
    """
    def update(self):
        super().update()

        # 1.
        if self.center_x < -100 or self.center_x > 1500 or \
                self.center_y > 1100 or self.center_y < -100:
            self.kill()


class MyGame(arcade.Window):
    """ Main application class. """

    """
    0. Init
    - 1. Set the working directory (where we expect to find files) to the same directory this .py file is in
    - 2. Spite lists 
    - 3. Player setup
    - 4. Variables to check if bounds are hit
    - 5. Sounds (!!!TODO!!!)
    - 6. Start state when game is loaded for the fist time
    - 7. Load and fill instructions array (Game over + Start screen) 
    """
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # 1.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0

        self.game_over = False

        # 2.
        self.all_sprites_list = None
        self.asteroid_list = None
        self.bullet_list = None
        self.ship_life_list = None
        self.background = None

        # 3.
        self.score = 0
        self.player_sprite = None
        self.lives = 3

        # 4.
        self.view_bottom = 0
        self.view_left = 0

        # 5.
        self.laser_sound = arcade.load_sound("assets/sounds/laser.wav")
        self.background_sound = arcade.load_sound("assets/sounds/spy_background_pixel_3.mp3")
        self.is_background_music_on = False

        # 6.
        self.current_state = INSTRUCTIONS_PAGE_0

        # 7.
        self.instructions = []
        texture_start_screen = arcade.load_texture("assets/UI/start_text.png")
        self.instructions.append(texture_start_screen)
        texture_game_over = arcade.load_texture("assets/UI/game_over_text.png")
        self.instructions.append(texture_game_over)
        texture_restart = arcade.load_texture("assets/UI/restart_text.png")
        self.instructions.append(texture_restart)

    """
    0. Draw start page when game is loaded
    - 1. Draw game as a background
    - 2. Draw texture at 0 on the screen (press space to start text)
    """
    def draw_start_page(self):

        # 1.
        self.draw_game()

        # 2.
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5,
                                      self.instructions[0].width,
                                      self.instructions[0].height, self.instructions[0], 0)

    """
    0. Draw game over screen
    - 1. Game is already drawn, we draw on top of it "Game over" and "try again"
    """
    def draw_game_over(self):

        # 1.
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5,
                                      self.instructions[1].width,
                                      self.instructions[1].height, self.instructions[1], 0)

        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.25,
                                      self.instructions[2].width,
                                      self.instructions[2].height, self.instructions[2], 0)
    """
    0. Setup to start new game
    - 1. General vars (frame count + game over bool)
    - 2. Load background image
    - 3. Initialize the sprite lists
    - 4. Setup the player
    - 5. Setup player HP
    - 6. Loads the asteroids
    """
    def start_new_game(self):

        if self.current_state == GAME_RUNNING and self.is_background_music_on:
            arcade.play_sound(self.background_sound)
            self.is_background_music_on = True

        # 1.
        self.frame_count = 0
        self.game_over = False

        # 2.
        self.background = arcade.load_texture("assets/UI/bg.png")

        # 3.
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # 4.
        self.score = 0
        self.player_sprite = ShipSprite("assets/player/ship.png", SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = 3

        # 6.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite("assets/UI/horizontal_bar_red.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.all_sprites_list.append(life)
            self.ship_life_list.append(life)

        # 7.
        image_list = ("assets/enemy/asteroid_grey.png",
                      "assets/enemy/asteroid_grey_tiny.png",
                      "assets/enemy/pixel_asteroid.png",
                      "assets/enemy/asteroid_tiny.png")
        for i in range(STARTING_ASTEROID_COUNT):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * ASTEROID_SPEED - 1
            enemy_sprite.change_y = random.random() * ASTEROID_SPEED - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.all_sprites_list.append(enemy_sprite)
            self.asteroid_list.append(enemy_sprite)

    """
    0. On draw general (not game specific) - render the screen
    - 1. This command has to happen before we start drawing
    - 2. Start page
    - 3. Game running
    - 4. Game over
    """
    def on_draw(self):

        # 1.
        arcade.start_render()

        # 2.
        if self.current_state == INSTRUCTIONS_PAGE_0:
            self.draw_start_page()

        # 3.
        elif self.current_state == GAME_RUNNING:
            self.draw_game()

        # 4.
        else:
            self.draw_game()
            self.draw_game_over()

    """
    0. Draw game on screen - render the game screen
    - 1. Draw the background image
    - 2. Draw all sprites
    - 3. Score and Asteroid count string output
    """
    def draw_game(self):

        # 1.
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,
                                      SCREEN_HEIGHT, self.background)

        # 2.
        self.all_sprites_list.draw()

        # 3.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

    """
    0. What happens on key pressed
    - 1. If key is SPACE and we are in the fist page, start game
    - 2. If key is SPACE and we are in game over, restart game
    - 3. If key is SPACE and er are not in respawn, shoot
    - 4. Movement keys
    """
    def on_key_press(self, symbol, modifiers):

        # 1..
        if self.current_state == INSTRUCTIONS_PAGE_0 and symbol == arcade.key.SPACE:
            self.current_state = GAME_RUNNING
            self.start_new_game()

        # 2.
        if self.current_state == GAME_OVER and symbol == arcade.key.SPACE:
            self.current_state = GAME_RUNNING
            self.start_new_game()

        # 3.
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            bullet_sprite = BulletSprite("assets/player/laser.png", SCALE)
            bullet_sprite.guid = "Bullet"

            bullet_speed = 13
            bullet_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
            bullet_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * bullet_speed

            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()

            self.all_sprites_list.append(bullet_sprite)
            self.bullet_list.append(bullet_sprite)

            arcade.play_sound(self.laser_sound)

        # 4.
        if symbol == arcade.key.A:
            self.player_sprite.change_angle = 2
        elif symbol == arcade.key.D:
            self.player_sprite.change_angle = -2.5
        elif symbol == arcade.key.W:
            self.player_sprite.thrust = 0.15
        elif symbol == arcade.key.S:
            self.player_sprite.thrust = -.2

    """
    0. What happens when we release the key
    - 1. Movements keys stop the moving
    """
    def on_key_release(self, symbol, modifiers):

        # 1.
        if symbol == arcade.key.A:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.D:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.W:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.S:
            self.player_sprite.thrust = 0

    """
    0. Split asteroids when are hit
    - 1. Generals 
    - 2. Big asteroid
    - 3. Tiny asteroid (medium)
    - 4. Tiny asteroid
    """
    def split_asteroid(self, asteroid: AsteroidSprite):

        # 1.
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        # 2.
        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["assets/enemy/asteroid_grey_tiny.png",
                              "assets/enemy/asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.25
                enemy_sprite.change_y = random.random() * 3 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

        # 3.
        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["assets/enemy/asteroid_grey_tiny.png",
                              "assets/enemy/asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.5
                enemy_sprite.change_y = random.random() * 3.5 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

        # 4.
        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["assets/enemy/asteroid_grey_tiny.png",
                              "assets/enemy/asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 4 - 1.75
                enemy_sprite.change_y = random.random() * 4 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

    """
    0. Update each tick
    - 1. If game is not running return out
    - 2. Update frame count
    - 3. Update if is not game over 
    - 4. Check collision for bullets
    - 5. For each asteroid hit we destroy it
    - 6. If we are not respawning check for collision
    - 7. Check if we hit outside bounds (a - right, b - left, c - top, d - bottom)
    - 8. Move the player if bounds are hit
    """
    def update(self, x):

        # 1.
        if self.current_state != GAME_RUNNING:
            return

        # 2.
        self.frame_count += 1

        # 3.
        if not self.game_over:
            self.all_sprites_list.update()

            # 4.
            for bullet in self.bullet_list:
                asteroids_plain = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                asteroids_spatial = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                if len(asteroids_plain) != len(asteroids_spatial):
                    print("Error: Update for bullets")

                # 5.
                asteroids = asteroids_spatial
                for asteroid in asteroids:
                    self.split_asteroid(asteroid)
                    asteroid.kill()
                    bullet.kill()

            # 6.
            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_asteroid(asteroids[0])
                        asteroids[0].kill()
                        self.ship_life_list.pop().kill()
                    else:
                        self.game_over = True
                        self.current_state = GAME_OVER

        # 7.
        changed_right = False
        changed_left = False
        changed_top = False
        changed_bottom = False

        # 7.a
        left = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left:
            self.view_left -= left - self.player_sprite.left
            changed_left = True

        # 7.b
        right = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right:
            self.view_left += self.player_sprite.right - right
            changed_right = True

        # 7.c
        top = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top:
            self.view_bottom += self.player_sprite.top - top
            changed_top = True

        # 7.d
        bot = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bot:
            self.view_bottom -= bot - self.player_sprite.bottom
            changed_bottom = True

        # 8.
        if changed_right:
            self.player_sprite.center_x = 75

        if changed_left:
            self.player_sprite.center_x = SCREEN_WIDTH - 75

        if changed_bottom:
            self.player_sprite.center_y = SCREEN_HEIGHT - 75

        if changed_top:
            self.player_sprite.center_y = 75


def main():
    """
    0. Main function
    """
    window = MyGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()
