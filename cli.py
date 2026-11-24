"""loopmem CLI: карточки, реплей вечером, статус."""
import json, os, sys, time
from .model import Lock, Scheduler

DB = os.path.expanduser("~/.loopmem.json")

def _load():
    if os.path.exists(DB):
        with open(DB) as f:
            return [Lock(**d) for d in json.load(f)]
    return []

def _save(locks):
    with open(DB, "w") as f:
        json.dump([{"content": l.content, "c": l.c, "t_last": l.t_last, "t0": l.t0} for l in locks], f)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    locks = _load()
    day = int(time.time() // 86400)
    sched = Scheduler()
    if cmd == "add":
        for text in sys.argv[2:]:
            locks.append(Lock(text))
        _save(locks); print(f"Добавлено. Всего замков: {len(locks)}")
    elif cmd == "review":
        batch = sched.evening_review(locks, day)
        _save(locks)
        print(f"Реплей вечером: {len(batch)} замков защищены на ночь.")
        for l in batch: print("  -", l.content)
    elif cmd == "tmr":
        k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        sched.night_tmr(locks, k, day); _save(locks)
        print(f"TMR: {k} проходов всем {len(locks)} замкам.")
    else:
        due = [l for l in locks if sched.due(l, day)]
        print(f"Всего замков: {len(locks)} | ждут реплея: {len(due)}")
        for l in sorted(due, key=lambda x: x.recall(day))[:10]:
            print(f"  recall={l.recall(day):.2f}  c={l.c}  {l.content}")

if __name__ == "__main__":
    main()
