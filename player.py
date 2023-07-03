import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, data, animation_steps):
        super().__init__()
        self.size_x = data[0]
        self.size_y = data[1]
        self.image_scale = data[2]
        self.offset = data[3]
        self.flip = False
        self.animation_list = self.load_images(data[4], animation_steps)
        self.action = 0  # 0: idle   # 1: run    # 2: jump   # 3: crouch    # 4: attack    # 5: hurt     # 6: death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 145))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.crouch = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attacking_fx = data[5]
        self.death_fx = data[6]
        self.health = 15
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

    def move(self, screen_width, screen_height, target, round_over):
        GRAVITY = 1.5
        SPEED = 6
        dx = dy = 0
        self.running = False
        self.crouch = False

        # get key presses
        mouse_clicked = pygame.mouse.get_pressed()[0]
        key = pygame.key.get_pressed()

        # check if player is alive and can only perform other actions if no currently attacking
        if self.alive and not self.attacking and not round_over:
            # movement
            if key[pygame.K_a]:
                dx = -SPEED
                self.flip = True
                self.running = True
            if key[pygame.K_d]:
                dx = SPEED
                self.flip = False
                self.running = True
            if key[pygame.K_s]:
                self.crouch = True
                dx = 0

            # jump
            if key[pygame.K_w] and not self.jump:
                self.vel_y = -30
                self.jump = True

            # attack
            if mouse_clicked:
                self.attack(target)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy > screen_height - 125:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 125 - self.rect.bottom

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    def update(self, surface):
        # draw health bar
        self.health_bar(surface)

        # check what action the player is performing
        # if dead
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)

        # if hit
        elif self.hit:
            self.update_action(5)

        # if attacking
        elif self.attacking:
            self.update_action(4)

        # if crouching
        elif self.crouch:
            self.update_action(3)

        # if jumping
        elif self.jump:
            self.update_action(2)

        # if running
        elif self.running:
            self.update_action(1)

        # idle
        else:
            self.update_action(0)

        animation_cooldown = 100
        # update image
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if not self.alive:
            death_cooldown = 100
            self.death_fx.play()

            # get the last frame
            self.frame_index = len(self.animation_list[self.action]) - 1

            if pygame.time.get_ticks() - self.update_time >= death_cooldown:

                self.death_fx.stop()
                # remove player from screen
                self.kill()
        else:
            # check if the animation has finished
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

                # check if an attack was executed
                if self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 15

                # check if damage was taken
                if self.action == 5:
                    self.hit = False
                    self.health -= 0.2
                    self.attacking = False
                    self.attack_cooldown = 10

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            self.attacking_fx.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                         2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.hit = True

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def health_bar(self, surface):
        for life in range(16):
            if int(self.health) == life:
                img = pygame.image.load(f'assets/image/background/props/health/{life}.png').convert_alpha()
                # img = pygame.image.load(f'assets/image/background/props/health/{life}.png').convert_alpha()
                img = pygame.transform.scale(img, (150, 50))
                img_rect = img.get_rect()
                img_rect.midtop = [90, 30]
                surface.blit(img, img_rect)

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
