"""loopmem — планировщик повторений на счётчиковой модели памяти.

Модель: элемент памяти = "замок" со счётчиком прохождений c.
Прочность T(c) = T0 * (1+c)^beta ночей до распада 1/e.
Каждая ночь без повторения срезает прочность на 15% (даунскейлинг сна).
Реплей вечером до сна защищает замок на текущую ночь.
Подсказка во сне (TMR): k проходов = k+1 к счётчику.
"""
import math

T0_DEFAULT = 4.0        # ночей жизни замка после первого прохождения
BETA = math.log(2.5) / math.log(2.0)   # калибровка: первый множитель интервала = 2.5
THETA = 0.9             # целевой recall перед реплеем
NIGHT_DECAY = 0.85      # 15% срез прочности за ночь без реплея


def strength(c: int, t0: float = T0_DEFAULT, beta: float = BETA) -> float:
    return t0 * (1.0 + c) ** beta


def interval(c: int, t0: float = T0_DEFAULT, theta: float = THETA, beta: float = BETA) -> int:
    """Дней до следующего реплея, чтобы recall упал до theta."""
    return max(1, round(strength(c, t0, beta) * math.log(1.0 / theta)))


class Lock:
    """Элемент памяти."""
    __slots__ = ("content", "c", "t_last", "t0")

    def __init__(self, content: str, c: int = 1, t_last: int = 0, t0: float = T0_DEFAULT):
        self.content, self.c, self.t_last, self.t0 = content, c, t_last, t0

    def recall(self, day: int) -> float:
        return math.exp(-(day - self.t_last) / strength(self.c, self.t0))

    def passes(self, k: int = 1, day: int = 0):
        """k прохождений петли (реплей или TMR-подсказка)."""
        self.c += k
        self.t_last = day


class Scheduler:
    """Сон-осведомлённый планировщик.

    Каждый вечер решает, какие замки реплеить сегодня:
      - планово (recall упал до THETA), или
      - аварийно (замок не переживёт ночь: прочность < 1 ночи).
    """

    def __init__(self, theta: float = THETA, night_decay: float = NIGHT_DECAY):
        self.theta, self.nd = theta, night_decay

    def due(self, lock: Lock, day: int) -> bool:
        return (day - lock.t_last) >= interval(lock.c, lock.t0, self.theta)

    def dying(self, lock: Lock, day: int) -> bool:
        return lock.recall(day) < 0.5 and strength(lock.c, lock.t0) < 1.0

    def evening_review(self, locks: list, day: int, budget: int = 200):
        planned = [l for l in locks if self.due(l, day)]
        rescue  = [l for l in locks if self.dying(l, day) and l not in planned]
        batch = (planned + rescue)[:budget]
        for l in batch:
            l.passes(1, day)
        return batch

    def night_tmr(self, locks: list, k: int = 3, day: int = 0):
        """TMR: k пассивных проходов замка во сне."""
        for l in locks:
            l.passes(k, day)
