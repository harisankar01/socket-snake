import socket
import pygame
import random
from pygame.locals import * # import all variables needed

width = 800
height = 600
gridfactor = 16
part_graphics_list = ['graphics/part1.png', 'graphics/part2.png', 'graphics/part3.png', 'graphics/part4.png']

class Snake_Printer(): # Snake_Printer class
    def __init__(self):
        self.part_image = pygame.image.load('graphics/part1.png').convert() # universal part image for this snake   
        self.food_image = pygame.image.load('graphics/food.png').convert() # universal food image for this snake   
        self.ms = gridfactor # movespeed

    def blit_body(self, new_body_str, wind):
        new_body = []
        for pair in new_body_str.split('|'):
            new_body.append([int(coord) for coord in pair.split(',')])
        #e.g. new_body = [['30', '40'], ['20', '10'], ['30', '90']]
        # rect = rectangular coordinates = ((x,y),(width,height))
        head_rect = self.part_image.get_rect()               
        # gets the rect object from the surface
        head_rect.x = new_body[0][0]            
        head_rect.y = new_body[0][1]
            
        wind.blit(self.part_image, head_rect)
        # blitting parts
        for i in range(1, len(new_body)):
            part_rect = self.part_image.get_rect()
            part_rect.x = new_body[i][0]
            part_rect.y = new_body[i][1]
            wind.blit(self.part_image, part_rect)
            # to blit the snake itself onto the window provided

    def blit_foodlist_str(self, foodlist_str, wind):
        foodlist = []
        for pair in foodlist_str.split('|'):
            foodlist.append(pair.split(','))

        for food in foodlist:
            food_rect = self.food_image.get_rect()
            food_rect.x = int(food[0])
            food_rect.y = int(food[1])
            wind.blit(self.food_image, food_rect)

    def edit_graphics(self, new_part_img): # setter to edit images for the sprites for head and part any time
        self.part_image = pygame.image.load(new_part_img).convert()



def main():
    server_ip = "127.0.0.1"  # host server's ip
    server_port = 5004  # server's port

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Attempting to connect to %s on port %i." % (server_ip, server_port))
    client_sock.connect((server_ip, server_port))  # TCP - from the client side, we CONNECT to the given host and port
    # our client's port is decided arbitrarily by our computer e.g. 5192

    pygame.init()
    #pygame.font.SysFont(name, size, bold=False, italic=False)
    font1 = pygame.font.SysFont('calibri', 18, True) # font object created

    win_dimensions = (width, height) # tuple width pixels x height pixels (width, height)
    window = pygame.display.set_mode(win_dimensions) # surface created for main window
    
    pygame.display.set_caption("snake") # set main display's caption to "snake1"

    bg = pygame.image.load('graphics/bg.png')
    overlay = pygame.image.load('graphics/bg_overlay.png')
    # render/blit background image on window
    window.blit(bg, (0, 0)) # block information transfer, render surface onto another surface
    
    # initially the direction is recieved from the server
    direction = int(client_sock.recv(4).decode('utf-8')) # bytestring from client buffer decoded to utf-8 string then to int

    snake = Snake_Printer() #object of snake_printer() class
  
    running = True
    while running:
        pygame.time.delay(70) # delay in miliseconds

        # pygame.event.get(), returns a list of all current I/O events occuring
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
            # every event has a type, and also event.key == pygame.K_ESCAPE so event has key pressed if I/O event
            # event checking if the red button X is pressed/clicked 
                running = False # loop breaks
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys_dict = pygame.key.get_pressed()  # gets current dictonary of keyboard presses where each key e.g. pygame.K_LEFT has a value of 1 or 0 (pressed/not pressed)

        # reverse direction is not allowed, if the snake1 is going east (3), then direction cannot be changed to west (4)    
        if keys_dict[pygame.K_LEFT] == True and direction != 3:
            direction = 4
        elif keys_dict[pygame.K_UP] == True and direction != 2:
            direction = 1      
        elif keys_dict[pygame.K_DOWN] == True and direction != 1:
            direction = 2  
        elif keys_dict[pygame.K_RIGHT] == True and direction != 4:
            direction = 3

        client_sock.send(str(direction).encode('utf-8')) # direction sent

        window.blit(bg, (0, 0))
        
        packet = client_sock.recv(1024).decode('utf-8')  # client's socket recieves data from the server script running on the server it connected to
        # print("RECIEVED PACKET ",packet)
        packet_segments = packet.split('%')
        updated_body_lists = packet_segments[1].split('-') #"1,2|3,3|4,3-"

        if packet_segments[0] != "":
            snake.blit_foodlist_str(packet_segments[0], window)

        for i in range(len(updated_body_lists)):
            if updated_body_lists[i] != "":
                snake.edit_graphics(part_graphics_list[i]) # different color every time
                snake.blit_body(updated_body_lists[i], window)

        window.blit(overlay, (0, 0))
        packet_score = packet_segments[2]
        # font.render(text, antialias, color, background=None) -> Surface
        text_surface = font1.render('Score: ' + packet_score, True, (255,255,255))
        window.blit(text_surface, (8, 8))

        pygame.display.update()  # update screen

    print("Disconnecting.")
    client_sock.close()  # close connection if user quitted
    pygame.quit()

if __name__ == '__main__':
    main()
