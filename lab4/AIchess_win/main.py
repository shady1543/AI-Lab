import sys
import argparse

from Game import *
from Dot import *
from ChessBoard import *
from MyAI import *
from ChessAI import *


def parse_arguments():
    parser = argparse.ArgumentParser(description='Game mode settings')
    parser.add_argument('--red', choices=['MyAI', 'Human', 'SuperAI'], default='MyAI',
                        help='选择红色方（先手方）')
    parser.add_argument('--black', choices=['MyAI', 'Human', 'SuperAI'], default='SuperAI',
                        help='选择黑色方（后手方）')
    return parser.parse_args()


def game_initialize():
    pygame.init()
    screen = pygame.display.set_mode((750, 667))
    background_img = pygame.image.load("images/bg.jpg")
    chessboard = ChessBoard(screen)
    clock = pygame.time.Clock()
    game = Game(screen, chessboard)
    game.back_button.add_history(chessboard.get_chessboard_str_map())
    return screen, background_img, chessboard, clock, game


def update_display(screen, background_img, chessboard, game):
    # 判断是否退出
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # 显示棋盘
    screen.blit(background_img, (0, 0))
    screen.blit(background_img, (0, 270))
    screen.blit(background_img, (0, 540))
    chessboard.show_chessboard_and_chess()
    ClickBox.show()
    Dot.show_all()
    game.show()
    pygame.display.update()


def ai_move(ai, game, chessboard, screen):
    cur_row, cur_col, nxt_row, nxt_col = ai.get_next_step(chessboard)
    ClickBox(screen, cur_row, cur_col)
    chessboard.move_chess(nxt_row, nxt_col)
    ClickBox.clean()
    # 产生将军局面
    if chessboard.judge_attack_general(game.get_player()):
        print('--- 黑方被将军 ---\n') if game.get_player() == 'r' else print('--- 红方被将军 ---\n')
        if chessboard.judge_win(game.get_player()):
            print('--- 红方获胜 ---\n') if game.get_player() == 'r' else print('--- 黑方获胜 ---\n')
            game.set_win(game.get_player())
            return
        else:
            game.set_attack(True)
    # 产生必胜局面
    else:
        if chessboard.judge_win(game.get_player()):
            print('--- 红方获胜 ---\n') if game.get_player() == 'r' else print('--- 黑方获胜 ---\n')
            game.set_win(game.get_player())
            return
        game.set_attack(False)
    # 产生和棋局面
    if chessboard.judge_draw():
        print('--- 和棋 ---\n')
        game.set_draw()

    game.back_button.add_history(chessboard.get_chessboard_str_map())
    game.exchange()
    return


def human_move(game, chessboard, screen):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        else:
            # 如果游戏没有获胜方，则游戏继续，否则一直显示"获胜"
            if not game.show_win and not game.show_draw:
                # 检测是否点击了"可落子"对象
                clicked_dot = Dot.click()
                if clicked_dot:
                    chessboard.move_chess(clicked_dot.row, clicked_dot.col)
                    # 清理「点击对象」、「可落子位置对象」
                    Dot.clean_last_position()
                    ClickBox.clean()
                    # 检测落子后，是否产生了"将军"功能
                    if chessboard.judge_attack_general(game.get_player()):
                        print('--- 黑方被将军 ---\n') if game.get_player() == 'r' else print('--- 红方被将军 ---\n')
                        # 检测对方是否可以挽救棋局，如果能挽救，就显示"将军"，否则显示"胜利"
                        if chessboard.judge_win(game.get_player()):
                            print('--- 红方获胜 ---\n') if game.get_player() == 'r' else print('--- 黑方获胜 ---\n')
                            game.set_win(game.get_player())
                            return
                        else:
                            # 如果攻击到对方，则标记显示"将军"效果
                            game.set_attack(True)
                    else:
                        if chessboard.judge_win(game.get_player()):
                            print('--- 红方获胜 ---\n') if game.get_player() == 'r' else print('--- 黑方获胜 ---\n')
                            game.set_win(game.get_player())
                            return
                        game.set_attack(False)

                    if chessboard.judge_draw():
                        print('--- 和棋 ---\n')
                        game.set_draw()
                        return

                    game.back_button.add_history(chessboard.get_chessboard_str_map())
                    # 落子之后，交换走棋方
                    game.exchange()
                    return

                # 检查是否点击了棋子
                clicked_chess = Chess.get_clicked_chess(game.get_player(), chessboard)
                if clicked_chess:
                    # 创建选中棋子对象
                    ClickBox(screen, clicked_chess.row, clicked_chess.col)
                    # 清除之前的所有的可以落子对象
                    Dot.clean_last_position()
                    # 计算当前被点击的棋子可以落子的位置
                    put_down_chess_pos = chessboard.get_put_down_position(clicked_chess)
                    # 根据当前被点击的棋子创建可以落子的对象
                    Dot.create_nums_dot(screen, put_down_chess_pos)

                if game.back_button.clicked_back(chessboard, event):
                    return


def main():
    args = parse_arguments()

    print(f'红色方（先手）：{args.red}\n'
          f'黑色方（后手）：{args.black}\n')

    # 游戏初始化
    screen, background_img, chessboard, clock, game = game_initialize()

    # 双人对战
    if args.red == 'Human' and args.black == 'Human':
        while not game.show_win and not game.show_draw:
            human_move(game, chessboard, screen)
            update_display(game.screen, background_img, game.chessboard, game)
            clock.tick(120)

    # 人机对战
    elif 'Human' in [args.red, args.black]:
        if args.red == 'Human' and args.black == 'MyAI':
            ai = MyAI(game.black)
        elif args.red == 'MyAI' and args.black == 'Human':
            ai = MyAI(game.red)
        elif args.red == 'Human' and args.black == 'SuperAI':
            ai = ChessAI(game.black)
        elif args.red == 'SuperAI' and args.black == 'Human':
            ai = ChessAI(game.red)

        while not game.show_win and not game.show_draw:
            if game.get_player() == ai.team:
                ai_move(ai, game, chessboard, screen)
            else:
                human_move(game, chessboard, screen)

            update_display(game.screen, background_img, game.chessboard, game)
            clock.tick(120)

    # AI对战
    else:
        if args.red == 'SuperAI' and args.black == 'MyAI':
            player1 = ChessAI(game.red)
            player2 = MyAI(game.black)

        elif args.red == 'MyAI' and args.black == 'SuperAI':
            player1 = MyAI(game.red)
            player2 = ChessAI(game.black)

        elif args.red == 'MyAI' and args.black == 'MyAI':
            player1 = MyAI(game.red)
            player2 = MyAI(game.black)

        elif args.red == 'SuperAI' and args.black == 'SuperAI':
            player1 = ChessAI(game.red)
            player2 = ChessAI(game.black)

        counter = 0

        while not game.show_win and not game.show_draw:
            currentAI = player1 if counter % 2 == 0 else player2
            counter += 1

            ai_move(currentAI, game, chessboard, screen)

            update_display(game.screen, background_img, game.chessboard, game)
            clock.tick(120)


if __name__ == '__main__':
    main()
