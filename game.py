import pygame


def main():
    game = Game()
    game.run()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600)) # pelin näyttö, koon pitää olla kahtien sulkujen sisällä
        self.running = False

    def run(self):  # Aina kun lisätään funktioon luokkia pitää olla (self): #Tämä on funktio alla luokat
        clock = pygame.time.Clock()

        self.running = True

        while self.running:
            self.handle_events()
            self.handle_game_logic()
            self.update_screen()
            # Odota niin kauan , että ruudun päivitysnopeus on 60fps  # Pitää ruudun päivityksen vakituisena
            clock.tick(60) 
                           
        pygame.quit()

    def handle_events(self):
         for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    def handle_game_logic(self):
        pass

    def update_screen(self)
        self.screen.fill('purple')
        pygame.display.flip()


if __name__ == '__main__':
    main()