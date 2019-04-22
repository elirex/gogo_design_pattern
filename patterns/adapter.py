#!/usr/bin/env python3

class Player:
    def __init__(self, name):
        self.name = name

    def attack(self):
        print(f'{self.name} attack')

    def defense(self):
        print(f'{self.name} defense')

# TODO: impolement PlayerTranslator
class PlayerTranslator(Player):

    def __init__(self, player):
        self._player = player

    def attack(self):
        self._player.gong_ji()

    def defense(self):
        self._player.fang_shou()

class ChinsesPlayer:
    def __init__(self, name):
        self.name = name

    def gong_ji(self):
        print(f'{self.name} 攻擊')

    def fang_shou(self):
        print(f'{self.name} 防守')


if __name__ == '__main__':
    Jeff = Player('Jeff')
    CJ = Player('CJ')
    shiang = PlayerTranslator(ChinsesPlayer('香香'))

    Jeff.attack()
    CJ.attack()
    shiang.attack()
    # TODO: call shiang to attack


    Jeff.defense()
    CJ.defense()
    shiang.defense()
    # TODO: call shiang to defense

