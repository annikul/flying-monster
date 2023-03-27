import pygame


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600)) # pelin näyttö, koon pitää olla kahtien sulkujen sisällä
    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((230, 230, 225))
        pygame.display.flip()

        clock.tick(60) # Odota niin kauan , että ruudun päivitysnopeus on 60 fps

    pygame.quit()


if __name__ == '__main__':
    main()