import pygame


def main():
    game = Game()
    game.run()

# Kaikki missä on self voi käyttää missä vain funktiossa. Se muuttuja menee selfiin
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600)) # pelin näyttö, koon pitää olla kahtien sulkujen sisällä
        self.running = False
        self.init_graphics()
        self.init_objects()

    def init_graphics(self):
        self.monster_frame = 0
        monster_imgs = [
            pygame.image.load(f'images/monster/flying/frame-{i}.png')
            for i in [1, 2, 3, 4]
        ]
        self.monster_imgs = [
            pygame.transform.rotozoom(x, 0, 1/16)
            for x in monster_imgs
        ]
        bg_imgs = [
            pygame.image.load(f'images/background/layer_{i}.png')
            for i in [1, 2, 3]
        ]
        self.bg_imgs = [
            pygame.transform.rotozoom(x, 0, 600 / x.get_height()).convert_alpha()
            for x in bg_imgs
        ]

    def init_objects(self):
        self.monster_y_speed = 0
        self.monster_pos = (200,000)
        self.monster_lift = False
        self.bg0_pos = 0
        self.bg1_pos = 0
        self.bg2_pos = 0

    def run(self):  # Aina kun lisätään funktioon luokkia pitää olla (self): #Tämä on funktio alla luokat
        clock = pygame.time.Clock()

        self.running = True
    
        while self.running:
            self.handle_events()
            self.handle_game_logic()
            self.update_screen()
            # Odota niin kauan , että ruudun päivitysnopeus on 60fps  # Pitää ruudun päivityksen vakituisena
            clock.tick(60)  # monsterin nopeus
                           
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
    
    def handle_game_logic(self):
        self.bg0_pos -= 0.25
        self.bg1_pos -= 0.5
        self.bg2_pos -= 2

        monster_y = self.monster_pos[1]
        
        if self.monster_lift:
            # Lintua nostetaan (0.5 px nostavauhtia/ frame)
            self.monster_y_speed -= 0.5
            self.monster_frame += 1
        else:    
            # Painovoima (lisää putoamisnopeutta joka kuvassa)
            self.monster_y_speed += 0.2
       
        # Liikuta monsteria sen nopeuden verran
        monster_y += self.monster_y_speed

        self.monster_pos = (self.monster_pos[0], monster_y)

    def update_screen(self):
        # Täytä tausta violetilla värillä
        #self.screen.fill('purple')

        self.screen.blit(self.bg_imgs[0], (self.bg0_pos, 0))
        self.screen.blit(self.bg_imgs[1], (self.bg1_pos, 0))
        self.screen.blit(self.bg_imgs[2], (self.bg2_pos, 0))

        # Piirrä lintu
        angle = -90 * 0.04 * self.monster_y_speed
        angle = max(min(angle, 60), -60) # Monsteri ei mene yli 60, -60 kulman. Ei lähe pyörimään 
        
        monster_img_i = self.monster_imgs[(self.monster_frame // 3) % 4] # Siipien räpyttely

        monster_img = pygame.transform.rotozoom(monster_img_i, angle, 1)
        self.screen.blit(monster_img, self.monster_pos)

        pygame.display.flip()


if __name__ == '__main__':
    main()