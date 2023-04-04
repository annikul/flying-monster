import random

import pygame

DEFAULT_SCREEN_SIZE = (800, 450)
FPS_TEXT_COLOR = (128, 0, 128)  # dark purple
TEXT_COLOR = (128, 0, 0) # dark red

def main():
    game = Game()
    game.run()

# Kaikki missä on self voi käyttää missä vain funktiossa. Se muuttuja menee selfiin
class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False
        self.show_fps = True
        self.screen = pygame.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.screen_w = self.screen.get_width()
        self.screen_h = self.screen.get_height()
        self.running = False
        self.font16 = pygame.font.Font('fonts/SyneMono-Regular.ttf', 16)
        self.init_graphics()
        self.init_objects()

    def init_graphics(self):
        big_font_size = int(96 * self.screen_h / 450)
        self.font_big = pygame.font.Font('fonts/SyneMono-Regular.ttf', big_font_size)
        original_monster_images = [
            pygame.image.load(f'images/monster/flying/frame-{i}.png')
            for i in [1, 2, 3, 4]
        ]
        self.monster_imgs = [
            pygame.transform.rotozoom(x, 0, self.screen_h / 9600).convert_alpha
            for x in original_monster_images
        ]
        original_monster_dead_images = [
            pygame.image.load(f'images/monster/got_hit/frame-{i}.png')
            for i in [1, 2]
        ]
        self.monster_dead_imgs = [
            pygame.transform.rotozoom(img, 0, self.screen_h / 9600).convert_alpha()
            for img in original_monster_dead_images
        ]
        original_bg_images = [
            pygame.image.load(f'images/background/layer_{1}.png')
            for i in [1, 2, 3]
        ]
        self.bg_imgs = [
            pygame.transform.rotozoom(
                img, 0, self.screen_h / img.get_height()
            ).convert_alpha()
            for img in original_bg_images
        ]
        self.bg_widths = [img.get_width() for img in self.bg_imgs]
        self.bg_pos = [0, 0, 0]  # Tausta kuva ei ala alusta kun peli alkaa alusta, tausta ei välky

    def init_objects(self):
        self.monster_alive = True
        self.monster_y_speed = 0
        self.monster_pos = (self.screen_w / 3, self.screen_h / 4)   # Kohta/korkeus mistä monsteri aloittaa
        self.mosnter_angle = 0
        self.monster_frame = 0
        self.monster_lift = False
        self.obstacles = [Obstacle.make_random(self.screen_w, self.screen_h)]
        
    def scale_positions(self, scale_x, scale_y):
        self.monster_pos = (self.monster_pos[0] * scale_x, self.monster_pos[1] * scale_y)
        for i in range(len(self.bg_pos)):
            self.bg_pos[i] = self.bg_pos[i] * scale_x

    def run(self):  # Aina kun lisätään funktioon luokkia pitää olla (self): #Tämä on funktio alla luokat
        self.running = True
    
        while self.running:
            self.handle_events()
            self.handle_game_logic()
            self.update_screen()
            # Odota niin kauan , että ruudun päivitysnopeus on 60fps  # Pitää ruudun päivityksen vakituisena
            self.clock.tick(60)  # monsterin nopeus
                           
        pygame.quit()

    def handle_events(self):
         for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.monster_lift = True  # Monsteri nousee ylöspäin
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.monster_lift = False
                    elif event.key in (pygame.K_f, pygame.K_F11):
                        self.toggle_fullscreen()
                    elif event.key in (pygame.K_r, pygame.K_RETURN):  
                        self.init_objects()  # r tai enterillä saa pelin käynnistymään uudestaan

    def toggle_fullscreen(self):
        old_w = self.screen_w
        old_h = self.screen_h
        if self.is_fullscreen:
            pygame.display.set_mode(DEFAULT_SCREEN_SIZE)
            self.is_fullscreen = False
        else:
             pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
             self.is_fullscreen = True
        screen = pygame.display.get_surface()
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()
        self.init_graphics()
        self.scale_positions(
            scale_x=(self.screen_w / old_w),
            scale_y=(self.screen_h / old_h),
        )

    def handle_game_logic(self):
        if self.monster_alive:
            self.bg_pos[0] -= 0.5
            self.bg_pos[1] -= 1
            self.bg_pos[2] -= 3

        monster_y = self.monster_pos[1]
        
        if self.monster_alive and self.monster_lift:
            # Lintua nostetaan (0.5 px nostavauhtia/ frame)
            self.monster_y_speed -= 0.5
        else:    
            # Painovoima (lisää putoamisnopeutta joka kuvassa)
            self.monster_y_speed += 0.2
       
        if self.monster_lift or not self.monster_alive:
            self.monster_frame += 1

        # Liikuta monsteria sen nopeuden verran
        monster_y += self.monster_y_speed

        if self.monster_alive: # Jos monsteri elossa
            # laske monsterin asento
            self.monster_angle = -90 * 0.04 *self.monster_y_speed
            self.monster_angle = max(min(self.monster_angle, 60), -60)
        
        # Tarkista onko monsteri pudonnut maahan
        if monster_y > self.screen_h * 0.78:
            monster_y = self.screen_h * 0.78
            self.monster_speed = 0
            self.mosnter_alive = False

        # Aseta  monsterin x-y-koordinaatit self.monster_pos-muuttujaan
        self.monster_pos = (self.monster_pos[0], monster_y)

        for obstacle in self.obstacles:
            obstacle.move(self.screen_w * 0.005)

    def update_screen(self):
        # Täytä tausta violetilla värillä
        #self.screen.fill('purple')

        # Piirrä taustakerrokset (3 kpl)
        for i in range(len(self.bg_imgs)):
            # Ensin piirrä vasen tausta
            self.screen.blit(self.bg_imgs[i], (self.bg_pos[1], 0))
            # Jos vasen tausta ei riitä peittämään koko ruutua, niin...
            if self.bg_pos[i] + self.bg_widths[i] < self.screen_w:
                # ...piirrä sama tausta vielä oikealle puolelle
                self.screen.blit(
                    self.bg_imgs[i],
                    (self.bg_pos[i] + self.bg_widths[i], 0)
                )
            # Jos taustaa on jo siirretty sen leveyden verran...
            if self.bg_pos[i] < -self.bg_widths[i]:
                # ...niin aloita alusta
                self.bg_pos[i] += self.bg_widths[i]

        for obstacle in self.obstacles:
            obstacle.render(self.screen)

        # Piirrä lintu
        if self.monster_alive:
            monster_img_i = self.monster_imgs[(self.monster_frame // 3) % 4]
        else:
            monster_img_i = self.monster_dead_imgs[(self.monster_frame // 10) % 2]
        monster_img = pygame.transform.rotozoom(monster_img_i, self.monster_angle, 1)
        self.screen.blit(monster_img, self.monster_pos)

        if not self.monster_alive:
            game_over_img = self.font_big.render('GAME OVER', True, TEXT_COLOR)
            x = self.screen_w / 2 - game_over_img.get_width() / 2
            y = self.screen_h / 2 - game_over_img.get_height() / 2
            self.screen.blit(game_over_img, (x, y))

        # Piirrä FPS luku
        if self.show_fps:
            fps_text = f'{self.clock.get_fps():.1f} fps'
            fps_img = self.font16.render(fps_text, True, FPS_TEXT_COLOR)
            self.screen.blit(fps_img, (0, 0))

        pygame.display.flip()


class Obstacle:
    def __init__(self, position, upper_height, lower_height, width=100):
        self.position = position # vasemman reunan sijainti
        self.upper_height = upper_height
        self.lower_height =lower_height
        self.width = width
        self.color = (0, 128, 0) # dark green

    @classmethod
    def make_random(cls, screen_w, screen_h):
        h1 = random.randint(int(screen_h * 0.05), int(screen_h * 0.75))
        h2 = random.randint(int((screen_h - h1) * 0.05),
                             int((screen_h - h1) * 0.75))
        return cls(upper_height=h1, lower_height=h2, position=screen_w)
        
    def move(self, speed):
        self.position -= speed

    def is_visible(self):
        return self.position + self.width >=0
        
    def render(self, screen):
        x = self.position
        uy = 0
        uh = self.upper_height
        pygame.draw.rect(screen, self.color, (x, uy, self.width, uh))
        ly = screen.get_height() - self.lower_height
        lh = self.lower_height
        pygame.draw.rect(screen, self.color, (x, ly, self.width, lh))


if __name__ == '__main__':
    main()