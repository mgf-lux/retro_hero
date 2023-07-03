import pygame
from random import randint


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, data, animation_steps):
        super().__init__()
        self.size_x = data[0]
        self.size_y = data[1]
        self.image_scale = data[2]
        self.offset = data[3]
        self.flip = False
        self.animation_list = self.load_images(data[randint(4, 5)], animation_steps)
        self.action = 0  # 0: rise   # 1: walk    # 2: death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 145))
        self.vel_y = 0
        self.speed = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attacking_cooldown = 0
        self.attacking_fx = data[6]
        self.death_fx = data[7]
        self.health = 1.5
        self.health_upgrade = False
        self.alive = True
        self.hit = False

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size_x, y * self.size_y, self.size_x, self.size_y)
                temp_img_list.append(
                    pygame.transform.scale(temp_img, (self.size_x * self.image_scale, self.size_y * self.image_scale)))
            animation_list.append(temp_img_list)

        return animation_list

    def move(self, target, round_over):
        self.speed = 1.5
        dx = 0

        self.running = False

        # check if enemy and player is alive
        if self.alive and not self.attacking and not round_over:
            # can only peform other actions if no currently attacking

            # ensure enemy track player position
            if self.rect.left >= target.rect.right:
                self.flip = False
                self.running = True
                self.speed = 1.6
                dx = -self.speed

            elif self.rect.right <= target.rect.left:
                self.flip = True
                self.running = True
                dx = +self.speed

            # attack when collide with player
            if self.rect.colliderect(target.rect):
                self.attack(target)
                self.attacking = False

            # update player position
            self.rect.x += dx

    def update(self):
        if self.hit:
            self.hit = False
            self.health -= 0.5

        elif self.health <= 0:
            self.health = 0
            self.update_action(2)
            self.alive = False


        animation_cooldown = 100
        # update image
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # check what action the player is performing

        # check if skeleton is rising
        if self.action == 0:
            if self.frame_index >= len(self.animation_list[self.action]) - 1:
                self.update_action(1)

        # check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

        if not self.alive:
            self.death_fx.play()

            # get the last frame
            self.frame_index = len(self.animation_list[self.action]) - 1
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.death_fx.stop()
                # remove enemy from screen
                self.kill()

    def attack(self, target):
        # execute attack
        self.attacking = True
        self.attacking_fx.play()
        self.speed = 0
        # direction = [self.rect.left, self.rect.right]
        attacking_rect = pygame.Rect(self.rect.left, self.rect.y, 2 * self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.hit = True

        # stop attacking sound when the player die
        if not target.alive:
            self.attacking_fx.stop()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
