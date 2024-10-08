import pygame
from pygame import mixer
from fighter2 import Fighter, Button, Effect
from stats import stats
from bot import moveAI
try:
    stats_list = stats()

    mixer.init()
    pygame.init()

    # create game window

    screen_width, screen_height = 1000, 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Brawler')

    # set framerate
    clock = pygame.time.Clock()
    FPS = 60

    # define colors
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    blue = (0, 0, 255)

    # define game variables

    intro_count = 5
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]
    round_over = False
    round_over_cooldown = 2000
    plyr1_action = ''
    plyr2_action = ''
    plyr1_potions = 5
    plyr2_potions = 5
    plyr_1_turns = 0
    plyr_2_turns = 0
    attack = 0
    turn = 1
    double_animate = 0
    last_time = 0

    # define fighter variables

    warrior_size = 162
    warrior_scale = 4
    warrior_offset = [72, 56]
    warrior_data = [warrior_size, warrior_scale, warrior_offset]

    wizard_size = 250
    wizard_scale = 3
    wizard_offset = [112, 107]
    wizard_data = [wizard_size, wizard_scale, wizard_offset]


    pygame.mixer.music.load('assets/audio/musicop.mp3')
    pygame.mixer.music.set_volume(0.5)
    # pygame.mixer.music.play(-1, 0.0, 5000)

    sword_fx = pygame.mixer.Sound('assets/audio/sword.wav')
    sword_fx.set_volume(0.5)
    magic_fx = pygame.mixer.Sound('assets/audio/magic.wav')
    magic_fx.set_volume(0.75)
    # load background image

    bg_image = pygame.image.load('assets/images/background/background.jpg').convert_alpha()

    # load spritesheets

    warrior_sheet = pygame.image.load('assets/images/warrior/sprites/warrior.png').convert_alpha()
    wizard_sheet = pygame.image.load('assets/images/wizard/sprites/wizard.png').convert_alpha()


    # Load Damage spritesheets
    explosion_sheet = pygame.image.load('assets/images/damage/explosion.png').convert_alpha()
    explosion_info = {'length': 16, 'size_in_px': 72}

    explosion_list = []
    for x in range(16):
        temp_img = explosion_sheet.subsurface(72*x, 0, 72, 72)
        explosion_list.append(pygame.transform.scale(temp_img, (100, 100)))


    damage_sheet = pygame.image.load('assets/images/damage/damage.png').convert_alpha()
    damage_info = {'length': 7, 'size_in_px': 140}
    damage_list = []
    for x in range(7):
        temp_img = damage_sheet.subsurface(140*x, 0, 140, 50)
        damage_list.append(pygame.transform.scale(temp_img, (200, 200)))


    blood_sheet = pygame.image.load('assets/images/damage/blood.png').convert_alpha()
    blood_info = {'length': 6, 'size_in_px': 32}
    blood_list = []
    for x in range(6):
        temp_img = blood_sheet.subsurface(32*x, 0, 32, 32)
        blood_list.append(pygame.transform.scale(temp_img, (150, 150)))



    # Effects defined

    explosion = Effect(explosion_list, 50)
    explosion_x = 0
    explosion_y = 0

    damage = Effect(damage_list, 50)
    damage_x = 0
    damage_y = 0

    blood = Effect(blood_list, 50)
    blood_x = 0
    blood_y = 0


    # load victory image

    victory_image = pygame.image.load('assets/images/icons/victory.png').convert_alpha()

    # define number of steps in each animation
    warrior_animation_steps = [10, 8, 1, 7, 7, 3, 7]
    wizard_animation_steps = [8, 8, 1, 8, 8, 3, 7]


    # define font
    count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
    turn_font = pygame.font.Font("assets/fonts/turok.ttf", 50)


    action_defend_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, 0, 490, 'defend', 20, yellow, 10, "assets/fonts/turok.ttf")
    #plyr1_action_heal_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr1_potions} left)', 20, yellow, 10, "assets/fonts/turok.ttf")
    #plyr2_action_heal_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr2_potions} left)', 20, yellow, 10, "assets/fonts/turok.ttf")
    action_attack_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, 2*screen_width/3, 490, 'attack', 20, yellow, 10, "assets/fonts/turok.ttf")

    attack1_btn = Button((30, 90, 255), blue, screen_width/2 - 20, 90, 0, 490, 'attack 1', 20, yellow, 10, "assets/fonts/turok.ttf")
    attack2_btn = Button((30, 90, 255), blue, screen_width/2 - 20, 90, screen_width/2, 490, 'attack 2', 20, yellow, 10, "assets/fonts/turok.ttf")

    # define function to draw text

    def draw_text(text, font, text_color, x, y):
        img = font.render(text, True, text_color, 10)
        screen.blit(img, (x, y))


    # draw background function

    def draw_bg():
        scaled_bg = pygame.transform.scale(bg_image, (screen_width, screen_height))
        screen.blit(scaled_bg, (0, 0))

    # function for drawing fighter health bars
    def draw_health_bar(health, max_health, x, y):
        ratio = health/max_health
        pygame.draw.rect(screen, white, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, red, (x, y, 400, 30))
        pygame.draw.rect(screen, yellow, (x, y, 400*ratio, 30))

    def double_animation(animation_1, animation_2, x_1, y_1, x_2, y_2, last_time=pygame.time.get_ticks()):
        if pygame.time.get_ticks() - last_time >= len(animation_1.animation_list)*animation_1.animation_cooldown:
            animation_2.draw(screen, x_2, y_2)
            print('blood')
        else:
            animation_1.draw(screen, x_1, y_1)
            print('damage')
        if animation_2.frame_index >= len(animation_2.animation_list) - 1:
            return 'ended'
        else:
            return None


    # Create two instances of Fighter

    Fighter1 = Fighter(1, 200, 310, False, warrior_data, warrior_sheet, warrior_animation_steps, sword_fx, stats_list[0], stats_list[2], stats_list[4])
    Fighter2 = Fighter(2, 700, 310, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx, stats_list[1], stats_list[3], stats_list[5])

    # game loop
    run = True
    while run:
        clock.tick(FPS)

        # draw background

        draw_bg()

        # show player stats

        draw_health_bar(Fighter1.health, stats_list[6], 20, 20)
        draw_health_bar(Fighter2.health, stats_list[7], 580, 20)
        draw_text('P1: ' + str(score[0]), score_font, red, 20, 60)
        draw_text('P2: ' + str(score[1]), score_font, red, 580, 60)


        # update count
        if intro_count <= 0:

            # move fighters
            # if turn == 1:
            #     if plyr1_action == '':
            #         draw_text("Player 1's Turn. Pick a move!", turn_font, blue, 220, 50)
            #         action_attack_btn.draw(screen)
            #         action_defend_btn.draw(screen)
            #         plyr1_action_heal_btn.draw(screen)
            #         for event in pygame.event.get():
            #             if event.type == pygame.MOUSEBUTTONUP:
            #                 if action_attack_btn.main_body.collidepoint(event.pos):
            #                     plyr1_action = 'attack'
            #                 if action_defend_btn.main_body.collidepoint(event.pos):
            #                     plyr1_action = 'defend'
            #                 if plyr1_action_heal_btn.main_body.collidepoint(event.pos):
            #                     if plyr1_potions > 0:
            #                         Fighter1.health += 10
            #                         plyr1_potions -= 1
            #                         turn = 2
            #                         plyr1_action = ''
                    # if action_defend_btn.clicked:
                    #     plyr1_action = 'defend'
                    # if plyr1_action_heal_btn.clicked:
                    #     plyr1_action = 'heal'
                    # if action_attack_btn.clicked:
                        
                # if plyr1_action == 'defend':
                #     Fighter1.move(screen_width, screen_height, Fighter2)
                #     turn = 2
                #     plyr1_action = ''
                # elif plyr1_action == 'attack':
                #     attack1_btn.draw(screen)
                #     attack2_btn.draw(screen)
                #     for event in pygame.event.get():
                #         if event.type == pygame.MOUSEBUTTONUP:
                #             if attack1_btn.main_body.collidepoint(event.pos):
                #                 Fighter1.move(screen_width, screen_height, Fighter2)
                #                 blood.reset()
                #                 blood.animate = True
                #                 blood_x = Fighter2.rect.x
                #                 blood_y = Fighter2.rect.y

                #                 turn = 2
                #                 plyr1_action = ''
                #             if attack2_btn.main_body.collidepoint(event.pos):
                #                 Fighter1.move(screen_width, screen_height, Fighter2)
                #                 double_animate = 1
                #                 blood.reset()
                #                 damage.reset()
                #                 blood_x = Fighter2.rect.x
                #                 blood_y = Fighter2.rect.y
                #                 damage_x = Fighter2.rect.x
                #                 damage_y = Fighter2.rect.y
                #                 last_time = pygame.time.get_ticks()

                #                 turn = 2
                #                 plyr1_action = ''
                        
            # if turn == 2:
            #     if plyr2_action == '':
            #         draw_text("Player 2's Turn. Pick a move!", turn_font, blue, 220, 50)
            #         action_attack_btn.draw(screen)
            #         action_defend_btn.draw(screen)
            #         plyr2_action_heal_btn.draw(screen)
            #         for event in pygame.event.get():
            #             if event.type == pygame.MOUSEBUTTONUP:
            #                 if action_attack_btn.main_body.collidepoint(event.pos):
            #                     plyr2_action = 'attack'
            #                 if action_defend_btn.main_body.collidepoint(event.pos):
            #                     plyr2_action = 'defend'
            #                 if plyr2_action_heal_btn.main_body.collidepoint(event.pos):
            #                     if plyr2_potions > 0:
            #                         Fighter2.health += 10
            #                         plyr2_potions -= 1
            #                         turn = 1
            #                         plyr2_action = ''
            #                         plyr2_action_heal_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr2_potions} left)', 20, yellow, 10, "assets/fonts/turok.ttf")

                    # if action_defend_btn.clicked:
                        
                    # if plyr2_action_heal_btn.clicked:
                        
                    # if action_attack_btn.clicked:
                        
                # elif plyr2_action == 'defend':
                #     Fighter2.move(screen_width, screen_height, Fighter1)
                #     turn = 1
                #     plyr2_action = ''
                # elif plyr2_action == 'attack':
                #     attack1_btn.draw(screen)
                #     attack2_btn.draw(screen)
                #     for event in pygame.event.get():
                #         if event.type == pygame.MOUSEBUTTONUP:
                #             if attack1_btn.main_body.collidepoint(event.pos):
                #                 blood.reset()
                #                 blood.animate = True
                #                 blood_x = Fighter1.rect.x
                #                 blood_y = Fighter1.rect.y

                #                 turn = 1
                #                 plyr2_action = ''
                #             if attack2_btn.main_body.collidepoint(event.pos):
                #                 double_animate = 1
                #                 blood.reset()
                #                 damage.reset()
                #                 blood_x = Fighter1.rect.x
                #                 blood_y = Fighter1.rect.y
                #                 damage_x = Fighter1.rect.x
                #                 damage_y = Fighter1.rect.y
                #                 last_time = pygame.time.get_ticks()

                #                 turn = 1
                #                 plyr2_action = ''

            Fighter1.move(screen_width, screen_height, Fighter2)
            moveAI(Fighter2, Fighter2.rect.x, Fighter1.rect.x, screen_width, screen_height, Fighter1)
            #Fighter2.move(screen_width, screen_height, Fighter1)
        else:
            # display count timer
            draw_text(str(intro_count), count_font, red, screen_width/2, screen_height/3)
            # update count timer
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # update fighters
        Fighter1.update()
        Fighter2.update()

        # draw fighters

        Fighter1.draw(screen)
        Fighter2.draw(screen)

        if explosion.animate:
            explosion.draw(screen, explosion_x, explosion_y)
        if damage.animate:
            damage.draw(screen, damage_x, damage_y)
        if blood.animate:
            blood.draw(screen, blood_x, blood_y)
        if double_animate == 1:
            doub_anim_proc = double_animation(damage, blood, damage_x, damage_y, blood_x, blood_y, last_time)
            if doub_anim_proc == 'ended':
                double_animate = 0
        if double_animate == 2:
            doub_anim_proc = double_animation(explosion, blood, explosion_x, explosion_y, blood_x, blood_y, last_time)
            if doub_anim_proc == 'ended':
                double_animate = 0


        # check for player defeat
        if round_over == False:
            if Fighter1.alive == False:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif Fighter2.alive == False:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            screen.blit(victory_image, (360, 150))
            if pygame.time.get_ticks() - round_over_time > round_over_cooldown:
                round_over = False
                intro_count = 5
                Fighter1 = Fighter(1, 200, 310, False, warrior_data, warrior_sheet, warrior_animation_steps, sword_fx, stats_list[0], stats_list[2], stats_list[4])
                Fighter2 = Fighter(2, 700, 310, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx, stats_list[1], stats_list[3], stats_list[5])

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #  update display
        pygame.display.update()

    # exit pygame

    pygame.quit()
except Exception as e:
    print(e)