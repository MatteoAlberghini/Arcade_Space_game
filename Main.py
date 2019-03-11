import random
import math
import arcade
import os

'''
TO DO: 
- Fix bug when you spawn you dont shoot for a while
- Rename everything
- Comment everything
- Start game screen
- Game over screen
- Change / more flashy texts
'''


"""
0. VARIABLES: 
- 1. Starting asteroid count
- 2. Scale factor
- 3. Limit of screen space
- 4. Screen width, height
- 5. Title
- 6. Limits
- 7. Margin when you hit screen margins (from left to right from top to botton)
"""

# 1.
STARTING_ASTEROID_COUNT = 10

# 2.
SCALE = 0.5

# 3.
OFFSCREEN_SPACE = 300

# 4.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

# 5.
SCREEN_TITLE = "xdxdxddxdx"

# 6.
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE

# 7.
VIEWPORT_MARGIN = 20


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
    - 2. Speed is incrementaly faster with thrust
    - 3. Change x and change y updated with angles
    - 4. We change player position based on change x and change y
    - 5. Call super class
    """
    def update(self):

        # 1.
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
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

    def update(self):
        super().update()
        if self.center_x < -100 or self.center_x > 1500 or \
                self.center_y > 1100 or self.center_y < -100:
            self.kill()


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0

        self.game_over = False

        # Sprite lists
        self.all_sprites_list = None
        self.asteroid_list = None
        self.bullet_list = None
        self.ship_life_list = None
        self.background = None

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.lives = 3

        # Scroll
        self.view_bottom = 0
        self.view_left = 0

        # Sounds
        #self.laser_sound = arcade.load_sound("sounds/laser1.wav")

    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        self.frame_count = 0
        self.game_over = False

        # background image
        self.background = arcade.load_texture("bg.png")

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite("ship.png", SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = 3

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite("horizontal_bar_red.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.all_sprites_list.append(life)
            self.ship_life_list.append(life)

        # Make the asteroids
        image_list = ("asteroid_grey.png",
                      "asteroid_grey_tiny.png",
                      "pixel_asteroid.png",
                      "asteroid_tiny.png")
        for i in range(STARTING_ASTEROID_COUNT):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.all_sprites_list.append(enemy_sprite)
            self.asteroid_list.append(enemy_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw background
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,
                                      SCREEN_HEIGHT, self.background)

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

    def on_key_press(self, symbol, modifiers):
        """ Called whenever a key is pressed. """
        # Shoot if the player hit the space bar and we aren't respawning.
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            bullet_sprite = BulletSprite("laser.png", SCALE)
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

            #arcade.play_sound(self.laser_sound)

        if symbol == arcade.key.A:
            self.player_sprite.change_angle = 2
        elif symbol == arcade.key.D:
            self.player_sprite.change_angle = -2.5
        elif symbol == arcade.key.W:
            self.player_sprite.thrust = 0.15
        elif symbol == arcade.key.S:
            self.player_sprite.thrust = -.2

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a key is released. """
        if symbol == arcade.key.A:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.D:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.W:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.S:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["asteroid_grey_tiny.png",
                              "asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["asteroid_grey_tiny.png",
                              "asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["asteroid_grey_tiny.png",
                              "asteroid_tiny.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

    def update(self, x):
        """ Move everything """

        self.frame_count += 1

        if not self.game_over:
            self.all_sprites_list.update()

            for bullet in self.bullet_list:
                asteroids_plain = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                asteroids_spatial = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                if len(asteroids_plain) != len(asteroids_spatial):
                    print("ERROR")

                asteroids = asteroids_spatial

                for asteroid in asteroids:
                    self.split_asteroid(asteroid)
                    asteroid.kill()
                    bullet.kill()

            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_asteroid(asteroids[0])
                        asteroids[0].kill()
                        self.ship_life_list.pop().kill()
                        print("Crash")
                    else:
                        self.game_over = True
                        print("Game over")

        changed_right = False
        changed_left = False
        changed_top = False
        changed_bottom = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed_left = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed_right = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed_top = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed_bottom = True

        if changed_right:
            self.player_sprite.center_x = 75

        if changed_left:
            self.player_sprite.center_x = SCREEN_WIDTH - 75

        if changed_bottom:
            self.player_sprite.center_y = SCREEN_HEIGHT - 75

        if changed_top:
            self.player_sprite.center_y = 75

def main():
    window = MyGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()
