from __future__ import annotations

from abc import ABCMeta
from utils import Vector2, MyMatrix
from uuid import uuid4
from random import randint
import logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("GameManager")


class Actor(metaclass=ABCMeta):
    uid: int
    hp:int
    max_hp:int
    min_attack:int
    max_attack:int
    position: Vector2
    name: str
    action = None
    tile_code: int
    vision: MyMatrix
    vision_range = 5
    hit_bonus = 0
    is_player = False
    damage_bonus = 0
    dodge_bonus = 0
    def_bonus = 0
    nvwa: 'Nvwa'
    messages: list[str]
    hurt: list

    is_player = False

    def __init__(self):
        self.uid = uuid4().int & (1<<64)-1
        self.hp = self.max_hp
        self.messages = []
        self.hurt = []

    def excuteAction(self):

        if self.action is None:
            self.think()
        if self.action is None:
            return
        self.action.excute(self, self.nvwa)

    def destroy(self):
        self.nvwa.destroy(self)

    def think(self):
        return

    def damaged(self, damage:int):
        self.hp -= damage
        self.hurt.append(str(damage))
        if self.hp < 0:
            self.destroy()

    def attack(self, target):
        # 投一个命中骰子
        hit_dice = self.roll_hit_dice()
        hit_bonus = self.hit_bonus

        # 投一个闪避骰子
        dodge_dice = target.roll_dodge_dice()
        dodge_bonus = target.dodge_bonus

        if hit_dice + hit_bonus <= dodge_dice + dodge_bonus:
            message = f'你攻击{target.name} miss. ({hit_dice} + {hit_bonus} vs {dodge_dice} + {dodge_bonus})'
            self.add_message(message)
            message = f'{self.name}攻击你 miss. ({hit_dice} + {hit_bonus} vs {dodge_dice} + {dodge_bonus})'
            target.add_message(message)
            target.hurt.append('miss')
            return

        message = f'你击中{target.name}. ({hit_dice} + {hit_bonus} vs {dodge_dice} + {dodge_bonus})'
        self.add_message(message)
        message = f'{self.name}击中你. ({hit_dice} + {hit_bonus} vs {dodge_dice} + {dodge_bonus})'
        target.add_message(message)

        # 投一个伤害骰子
        damage_dice = self.roll_damage_dice()
        damage_bonus = self.damage_bonus
        # 投一个减伤骰子
        def_dice = self.roll_def_dice()
        def_bonus = target.def_bonus
        damage = max(0, damage_dice + damage_bonus - def_dice - def_bonus)

        target.damaged(damage)
        message = f'{target.name} 受到 {damage} 点伤害. ({damage_dice} + {damage_bonus} - {def_dice} - {def_bonus})'
        self.add_message(message)
        message = f'你受到 {damage} 点伤害. ({hit_dice} + {hit_bonus} vs {dodge_dice} + {dodge_bonus})'
        target.add_message(message)



    def roll_hit_dice(self):
        return randint(0, 20)

    def roll_dodge_dice(self):
        return randint(0, 20)

    def roll_damage_dice(self):
        return randint(1, 3)
    
    def roll_def_dice(self):
        return randint(1, 3)

    def add_message(self, message):
        pass

