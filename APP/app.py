import os
import pygame
import win32api, win32con, win32gui


os.chdir('C:/Users/aralm/YandexDisk/Code_Python/NeuroGPT')
os.system('cls')

pygame.init()
size = [250, 250]
screen = pygame.display.set_mode(size) # For borderless, use pygame.NOFRAME
clock = pygame.time.Clock()
FPS = 30

fuchsia = (255, 0, 128)  # Transparency color
dark_red = (139, 0, 0)

# hwnd = pygame.display.get_wm_info()["window"]
# pygame.display.set_caption("Avatar")
# win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
#                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

img = pygame.image.load('model/apple.png')
img_rect = img.get_rect(center=(100, 100))
screen.blit(img, img_rect)

pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # screen.fill(fuchsia)  # Transparent background    

    # pygame.draw.rect(screen, dark_red, pygame.Rect(30, 30, 30, 60))
   
    # pygame.display.flip()
    # pygame.display.flip()
    clock.tick(FPS)
pygame.quit()

"""# -.- coding: utf8 -.-
import pygame


# уменьшил до размера (100, 100)
scaled_image = pygame.transform.scale(my_image, (30, 30))

angle = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pass
                # пишем свой код
    # обновляем значения
    angle += 1
    # рисуем
    screen.fill((200, 100, 0))
    screen.blit(my_image, (0,0))
    screen.blit(scaled_image, (600, 0))

    # исходное изображение поворачивается на значение переменной angle
    # и записывается в перменную rotated_image
    rotated_image = pygame.transform.rotate(my_image, angle)
    screen.blit(rotated_image, (400, 200))

    pygame.display.flip()
    clock.tick(10)
pygame.quit()
"""