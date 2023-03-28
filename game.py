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
        img_monster1 = pygame.image.load('images/monster/flying/frame-1.png')
        self.img_monster1 = pygame.transform.rotozoom(img_monster1, 0, 1/16)

    def init_objects(self):
        self.monster_y_speed = 0
        self.monster_pos = (200,300)
        self.monster_lift = False

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
        monster_y = self.monster_pos[1]
        
        if self.monster_lift:
            # Lintua nostetaan (8px / frame)
            self.monster_y_speed = 8
        else:    
            # Painovoima (lisää putoamisnopeutta joka kuvassa)
            self.monster_y_speed += 0.2
 
       
        # Liikuta monsteria sen nopeuden verran
        monster_y += self.monster_y_speed


        self.monster_pos = (self.monster_pos[0], monster_y)


    def update_screen(self):
        # Täytä tausta violetilla värillä
        self.screen.fill('purple')

        # Piirrä lintu
        self.screen.blit(self.img_monster1, self.monster_pos)

        pygame.display.flip()


if __name__ == '__main__':
    main()