import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 #爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]): #x,yに300,200が代入される
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv) #実際に移動
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"): #1回だけ呼び出されるメソッド
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery #こうかとんの中心縦座標
        self.rct.left = bird.rct.right #こうかとんの右座標
        self.vx, self.vy = +5, 0 #ビームの速度

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True): #画面の中に入っていたら表示
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)   


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコア表示に関するクラス
    """
    def __init__(self):
        """
        
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30) #フォント
        self.color = (0, 0, 255) #文字色の設定
        self.kazu = 0 #スコアの初期値
        self.img = self.fonto.render(f"スコア：{self.kazu}", 0, self.color) #文字列Surface
        self.ix, self.iy = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        """
        スコアの更新を行い表示する
        引数 screen：画面Surface
        """
        self.img = self.fonto.render(f"スコア：{self.kazu}", 0, self.color)
        screen.blit(self.img, (self.ix, self.iy))


class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, x: int, y: int):
        """
        爆発の設定
        引数1：爆弾の中心x座標
        引数2：爆弾の中心y座標
        """
        bg_img = pg.image.load("fig/explosion.gif") 
        self.bakuhatu = [bg_img, pg.transform.flip(bg_img, True, True)]
        self.rct = self.bakuhatu[0].get_rect()
        self.rct.center = (x, y)
        self.life = 20

    def update(self, screen: pg.Surface):
        """
        爆発Surfaceを切り替えて爆発を演出
        引数 screen：画面Surface
        """
        self.life -= 1
        if (self.life >= 0):
            for i in range(len(self.bakuhatu)):
                screen.blit(self.bakuhatu[i], self.rct)


class Lief:
    """
    ライフに関するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)  # フォント
        self.color = (0, 0, 255)  # 文字色の設定
        self.kokaton_life = 100  # こうかとんのライフを100に設定
        #当たり続けているとライフが減るのを防ぐ
        self.ix, self.iy = 100, HEIGHT - 50  # スコアの表示位置

    def check(self, screen: pg.Surface):
        """
        ライフを1減らし、ライフが0になったらゲームオーバーを表示する
        引数 screen：画面Surface
        """
        self.kokaton_life -= 1

        if self.kokaton_life <= 0:
            fonto = pg.font.Font(None, 80)  # フォントを80サイズに設定
            txt = fonto.render("Game Over", True, (255, 0, 0))  # ゲームオーバーのテキスト
            screen.blit(txt, [WIDTH // 2 - 150, HEIGHT // 2])  # 画面中央に表示
            pg.display.update()  # 画面を更新
            time.sleep(1)  # 1秒間表示
            return True  # ゲームオーバー
        return False  # ライフが残っている場合

    def draw_score(self, screen: pg.Surface):
        """
        ライフを画面に表示する
        引数 screen：画面Surface
        """
        life_img = self.fonto.render(f"ライフ：{self.kokaton_life}", 0, self.color)
        screen.blit(life_img, (self.ix, self.iy - 100))  


def main():
    beam_list = [] #Beamクラスのインスタンスを複数扱うための空のリスト
    explosion_list = []
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200)) #引数がタプル
    bomb = Bomb((255, 0, 0), 10) #ボムクラスのインスタンス
    score = Score()
    #スペースが押されるまではNone
    beam = None #__init__のselfを無視した引数を書く #ビームインスタンス生成(ビームが一つ完成)
    #bomb2 = Bomb((0, 0, 255), 20) #これだけでボムが増やせる
    bombs = [Bomb((255, 0, 0), 10) for i in range(NUM_OF_BOMBS)] #ボムのリストが5個並ぶ
    clock = pg.time.Clock()
    lief = Lief() #lifeクラスのインスタンス
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: #✕ボタン押されたらmainメソッドから出る
                return
            #スペースキーが押されたらビームを出す
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beam = Beam(bird)
                beam_list.append(beam) #リストに追加         
        screen.blit(bg_img, [0, 0])
        
        #衝突判定
        for bomb in bombs: #1つでもぶつかっsたらゲームオーバー
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                lief.check(screen)  # ライフを減らす
                bird.change_img(8, screen)
                
                if lief.check(screen):  # ライフが0ならゲームオーバー
                    return
        
        #ビームで撃ち落とされると一部がNoneになったリストになる
        for i, bomb in enumerate(bombs): #何番目のボムかを番号付きで取得
            for j, beam in enumerate(beam_list): ##何番目のビームかを番号付きで取得
                if beam_list[j] is not None: #beamのj番目がNoneじゃなかったら
                    if beam.rct.colliderect(bomb.rct): #ビームが爆弾を撃ち落としたら
                        # if explosion.life > 0:
                        explosion = Explosion(bomb.rct.centerx, bomb.rct.centery)
                        explosion_list.append(explosion)
                        bombs[i] = None #i番目をNoneにする
                        beam_list[j] = None #ビームのj番目をNone
                        bird.change_img(6, screen) #ビームが当たるとこうかとんが喜ぶ
                        score.kazu += 1 #スコアを1増やす
                        #explosion.update(screen)
                        pg.display.update()
                    
                    if check_bound(beam.rct) != (True, True):
                        del beam_list[j]
                    print(beam_list)

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        #beam.update(screen)
        bombs = [bomb for bomb in bombs if bomb is not None] #Noneでないものリスト
        beam_list = [beam for beam in beam_list if beam is not None] 
        for bomb in bombs: #リストにNoneが入っている可能性がある
            bomb.update(screen) #ボムの更新
        for beam in beam_list:
            beam.update(screen) #beamの更新
        #もしbeamがNoneじゃなかったらupdateする
        # if beam is not None:
        # beam.update(screen) #ここがNoneの時でもupdateされてるからエラー
        #bomb2.update(screen) #こっちで更新が必要
        for explosion in explosion_list:
            explosion.update(screen)
        score.update(screen)
        lief.draw_score(screen)  #ライフを表示
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()