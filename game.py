import random

import pygame

from highscore import HighscoreRecorder
from menu import Menu
from obstacle import Obstacle

DEFAULT_SCREEN_SIZE = (800, 450)
FPS_TEXT_COLOR = (128, 0, 128)  # dark purple
TEXT_COLOR = (128, 0, 0) # dark red
SCORE_TEXT_COLOR = (0, 64, 160)  

DEBUG  = 0

def main():
    game = Game()
    game.run()

# Kaikki missä on self voi käyttää missä vain funktiossa. Se muuttuja menee selfiin
class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.menu = Menu([
            "New Game",
            "High Scores",
            "About",
            "Quit"
        ])
        self.highscore_recorder = HighscoreRecorder()
        self.is_fullscreen = False
        self.is_in_menu = True
        self.is_in_highscore_record = False
        self.show_fps = True
        self.screen = pygame.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.screen_w = self.screen.get_width()
        self.screen_h = self.screen.get_height()
        self.running = False
        self.font16 = pygame.font.Font('fonts/SyneMono-Regular.ttf', 16)
        self.init_sounds()
        self.init_graphics()
        self.init_objects()
        self.open_menu()

    def init_sounds(self):
        self.flying_sound = pygame.mixer.Sound("sounds/flying.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")

    def init_graphics(self):
        self.menu.set_font_size(int(48 * self.screen_h / 450))
        self.highscore_recorder.set_font_size(int(36 * self.screen_h / 450))
        big_font_size = int(96 * self.screen_h / 450)
        self.font_big = pygame.font.Font('fonts/SyneMono-Regular.ttf', big_font_size)
        original_monster_images = [
            pygame.image.load(f'images/monster/flying/frame-{i}.png')
            for i in [1, 2, 3, 4]
        ]
        self.monster_imgs = [
            pygame.transform.rotozoom(x, 0, self.screen_h / 9600).convert_alpha()
            for x in original_monster_images
        ]
        self.monster_radius = self.monster_imgs[0].get_height() / 2  # Likiarvo
        original_monster_dead_images = [
            pygame.image.load(f'images/monster/got_hit/frame-{i}.png')
            for i in [1, 2]
        ]
        self.monster_dead_imgs = [
            pygame.transform.rotozoom(img, 0, self.screen_h / 9600).convert_alpha()
            for img in original_monster_dead_images
        ]
        original_bg_images = [
            pygame.image.load(f'images/background/layer_{i}.png')
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
        self.score = 0
        self.monster_alive = True
        self.monster_y_speed = 0
        self.monster_pos = (self.screen_w / 3, self.screen_h / 4)   # Kohta/korkeus mistä monsteri aloittaa
        self.mosnter_angle = 0
        self.monster_frame = 0
        self.monster_lift = False
        self.obstacles: list[Obstacle] = []
        self.next_obstacle_at = self.screen_w / 2
        self.add_obstacle()

    def add_obstacle(self):
        obstacle = Obstacle.make_random(self.screen_w, self.screen_h)
        self.obstacles.append(obstacle)

    def remove_oldest_obstacle(self):
        self.obstacles.pop(0)
        
    def scale_positions(self, scale_x, scale_y):
        self.monster_pos = (self.monster_pos[0] * scale_x, self.monster_pos[1] * scale_y)
        for i in range(len(self.bg_pos)):
            self.bg_pos[i] = self.bg_pos[i] * scale_x
        for obstacle in self.obstacles:
            obstacle.width *= scale_x
            obstacle.position *= scale_x
            obstacle.upper_height *= scale_y
            obstacle.hole_size *= scale_y
            obstacle.lower_height *= scale_y

    def run(self):  # Aina kun lisätään funktioon luokkia pitää olla (self): #Tämä on funktio alla luokat
        self.running = True
    
        while self.running:
            # Käsittele tapahtumat (eventit)
            self.handle_events()

            # Pelin logiikka (liikkumiset, painovaimo, yms)
            self.handle_game_logic()

            # Päivitä näyttö, piirtää taustalle kaikki asiat.
            self.update_screen()

            # Päivitä näytölle piirretyt asiat näkyviin
            pygame.display.flip()

            # Odota niin kauan , että ruudun päivitysnopeus on 60fps  # Pitää ruudun päivityksen vakituisena
            self.clock.tick(60)  # monsterin nopeus
                           
        pygame.quit()

    def handle_events(self):
         for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        if not self.is_in_menu:
                            self.monster_lift = True  # Monsteri nousee ylöspäin
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_f, pygame.K_F11):
                        self.toggle_fullscreen()
                    elif self.is_in_menu:
                        if event.key == pygame.K_UP:
                            self.menu.select_previous_item()
                        elif event.key == pygame.K_DOWN:
                            self.menu.select_next_item
                        elif event.key in (pygame.K_RETURN): 
                            item = self.menu.get_selected_item()
                            if item == "New Game":
                                self.start_game()
                            elif item == "High Scores":
                                pass # TODO: Implement High Score view
                            elif item == "About":
                                pass # TODO: Implement About view
                            elif item == "Quit":
                                self.running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.monster_lift = False
                    elif event.key == pygame.K_ESCAPE or not self.monster_alive:
                        if not self.is_in_highscore_record:
                            self.record_highscores()
                        else:
                            self.open_menu()
                    
    def start_game(self):
        self.play_game_music()
        self.is_in_menu = False
        self.is_in_highscore_record = False
        self.init_objects()
        self.flying_sound.play(-1)

    def open_menu(self):
        self.play_menu_music()
        self.is_in_menu = True
        self.flying_sound.stop()

    def kill_monster(self):
        if self.monster_alive:
            self.monster_alive = False
            self.flying_sound.stop()
            self.hit_sound.play()
            pygame.mixer.music.fadeout(500)

    def record_highscores(self):
        self.is_in_highscore_record = True
        print('High score')

    def play_menu_music(self):
        pygame.mixer.music.load('music/menu_chill.ogg')
        pygame.mixer_music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1)
             
    def play_game_music(self):
        pygame.mixer.music.load('music/run_game_2.ogg')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer_music.play(loops=-1)

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
        self.scale_positions_and_sizes(
            scale_x=(self.screen_w / old_w),
            scale_y=(self.screen_h / old_h),
        )

    def handle_game_logic(self):
        if self.is_in_menu:
            return
        
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
            self.monster_angle = -90 * 0.04 * self.monster_y_speed
            self.monster_angle = max(min(self.monster_angle, 60), -60)
        
        # Tarkista onko monsteri pudonnut maahan
        if monster_y > self.screen_h * 0.82:
            monster_y = self.screen_h * 0.82
            self.monster_y_speed = 0
            self.kill_monster

        # Aseta  monsterin x-y-koordinaatit self.monster_pos-muuttujaan
        self.monster_pos = (self.monster_pos[0], monster_y)

        # Lisää uusi este, kun viimeisin este on yli ruudun puolivälin
        if self.obstacles[-1].position < self.next_obstacle_at: # Kun käyttää -1 silloin se tarkoittaa viimeistä listalta eli ensimmäinen oikealta. -2 on toinen oikealta
            self.add_obstacle()
            self.next_obstacle_at = random.randint(
                int(self.screen_w * 0.35),
                int(self.screen_w * 0.65),
            )

        # Poista vasemmanpuoleisin este, kun se menee pois ruudulta
        if not self.obstacles[0].is_visible():
            self.remove_oldest_obstacle()
            self.score += 1

        # Siirrä esteitä sopivalla nopeudella ja tarkista törmäys
        self.monster_collides_with_obstacle = False
        for obstacle in self.obstacles:
            if self.monster_alive:
                obstacle.move(self.screen_w * 0.005)
            if obstacle.collides_with_circle(self.monster_pos, self.monster_radius):
                self.monster_collides_with_obstacle = True

        if self.monster_collides_with_obstacle:
            self.kill_monster()

    def update_screen(self):
        # Täytä tausta violetilla värillä
        # self.screen.fill('purple')

        # Piirrä taustakerrokset (3 kpl)
        for i in range(len(self.bg_imgs)): # i käy läpi luvut 0, 1 ja 2
            # Menussa piirretään vain ensimmäinen taustakerros
            if self.is_in_menu and i == 1:
                break # Kun ollan menussa ja i=1 niin lopetetaan looppi
            # Ensin piirrä vasen tausta
            self.screen.blit(self.bg_imgs[i], (self.bg_pos[i], 0))
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

        if self.is_in_menu:
            self.menu.render(self.screen)
            return
        
        if self.is_in_highscore_record:
            self.highscore_recorder.render(self.screen)
            return
        
        for obstacle in self.obstacles:
            obstacle.render(self.screen)

        # Piirrä monsteri
        if self.monster_alive:
            monster_img_i = self.monster_imgs[(self.monster_frame // 3) % 4]
        else:
            monster_img_i = self.monster_dead_imgs[(self.monster_frame // 10) % 2]
        monster_img = pygame.transform.rotozoom(monster_img_i, self.monster_angle, 1)
        monster_x = self.monster_pos[0] - monster_img.get_width() / 2 * 1.25
        monster_y = self.monster_pos[1] - monster_img.get_height() / 2 
        self.screen.blit(monster_img, (monster_x, monster_y))

        # Piirrä pisteet
        score_text = f'{self.score}'
        score_img = self.font_big.render(score_text, True, SCORE_TEXT_COLOR)
        score_pos = (self.screen_w * 0.95 - score_img.get_width(),
                    self.screen_h - score_img.get_height())
        self.screen.blit(score_img, score_pos)

        # Piirrä GAME OVER -teksti
        if not self.monster_alive:
            game_over_img = self.font_big.render('GAME OVER', True, TEXT_COLOR)
            x = self.screen_w / 2 - game_over_img.get_width() / 2
            y = self.screen_h / 2 - game_over_img.get_height() / 2
            self.screen.blit(game_over_img, (x, y))

        # Piirrä kehittämistä helpottava ympyrä
        if DEBUG:
            color = (0, 0, 0) if not self.monster_collides_with_obstacle else (255, 0, 0)
            pygame.draw.circle(self.screen, color, self.monster_pos, self.monster_radius)

        # Piirrä FPS luku
        if self.show_fps:
            fps_text = f'{self.clock.get_fps():.1f} fps'
            fps_img = self.font16.render(fps_text, True, FPS_TEXT_COLOR)
            self.screen.blit(fps_img, (0, 0))

    
if __name__ == '__main__':
    main()