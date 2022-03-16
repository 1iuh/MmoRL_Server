from actions.actions import Action


class Move(Action):
    direction:str
    cast = 100

    def __init__(self, direction):
        self.direction = direction

    def excute(self, target, obj_store):
        if target.hp <= 0:
            return

        target.action = None
        position = target.position.copy()
        if self.direction == 'UP':
            position.y = position.y + 1
        elif self.direction == 'DOWN':
            position.y = position.y - 1
        elif self.direction == 'LEFT':
            position.x = position.x - 1
        elif self.direction == 'RIGHT':
            position.x = position.x + 1

        # 如果是墙
        if obj_store.has_wall(position):
            return
        # 如果有门就开门
        if obj_store.has_door(position):
            door = obj_store.get_door_position(position)
            door.open()
            return

        # 如果有敌人
        other = obj_store.get_by_position(position)
        # 如果有其他对象, 就攻击
        if other is not None and other.hp >0:
            target.attack(other)
            return
        obj_store.move(target, position)
