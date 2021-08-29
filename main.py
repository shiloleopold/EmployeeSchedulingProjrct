from ortools.sat.python import cp_model
from tkinter import *
from itertools import islice

num_workers = 8
num_shifts = 2
num_days = 7
min_shifts_per_weak = 2


def calculate_shifts(workers):
    shift_requests = []
    for worker in workers:
        shift_requests.append(worker.get_shifts_array())

    # This program tries to find an assignment of workers to shifts
    # (2 shifts per day, for 7 days), subject to some constraints.
    # Each worker can request to be assigned to specific shifts.
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: worker 'n' works shift 's' on day 'd'.
    shifts = {}
    for idx, n in enumerate(workers):
        for d in all_days:
            for s in all_shifts:
                shifts[(idx, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (idx, d, s))

    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(idx, d, s)] for idx, n in enumerate(workers)) == 4)

    for idx, worker in enumerate(workers):
        model.Add(sum(shifts[(idx, d, s)] for d in all_days for s in all_shifts) >= min_shifts_per_weak)
    model.Minimize(
        sum(shift_requests[idx][d][s] * shifts[(idx, d, s)] for idx, n in enumerate(workers)
            for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # print
    if status != 3:
        for d in all_days:
            print('Day', d + 1)
            for idx, w in enumerate(workers):
                for s in all_shifts:
                    if solver.Value(shifts[(idx, d, s)]) == 1:
                        if shift_requests[idx][d][s] == 1:
                            print(w.name, 'works shift', s, '(not want to work).')
                        else:
                            print(w.name, 'works shift', s)
    else:
        print("there is no solution!")
    print()
    print('Statistics')
    print('  - Number of shift that worker not want but get = %i' % solver.ObjectiveValue(),
          '(out of', num_shifts * num_days * 4, ')')


class CheckBar(Frame):
    def __init__(self, parent=None, picks=[], side=TOP, anchor=W):
        Frame.__init__(self, parent)
        self.vars = []
        self.name_shifts = picks
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)

    def state(self):
        return map((lambda var: var.get()), self.vars)


class Worker:
    def __init__(self, cb, name=""):
        self.name = name
        self.check_bar = cb

    def get_shifts_array(self):
        result = []
        for var in self.check_bar.vars:
            result.append(var.get())
        return list(chunk(result, num_shifts))

    def get_chosen_shifts(self):
        pref = []
        for idx, x in enumerate(self.check_bar.state()):
            if x == 1:
                pref.append(self.check_bar.name_shifts[idx])
        return pref

    def print_worker_pref(self):
        print(self.name, end=': ')
        print(self.get_chosen_shifts())


def chunk(it, size):
    it = iter(it)
    return iter(lambda: list(islice(it, size)), [])


def view():
    root = Tk()
    t = Text(root, height=1, width=30)
    my_label = Label(root, text="בחר משמרות שאתה לא מעוניין לעבוד בהם")
    my_label.pack()
    lng = CheckBar(root, ['ראשון בוקר', 'ראשון ערב', 'שני בוקר', 'שני ערב',
                          'שלישי בוקר', 'שלישי ערב', 'רביעי בוקר', 'רביעי ערב', 'חמישי בוקר', 'חמישי ערב', 'שישי בוקר',
                          'שישי ערב', 'שבת בוקר', 'שבת ערב'])
    t.pack()
    lng.pack(side=TOP, fill=X)
    lng.config(relief=GROOVE, bd=2)

    worker = Worker(lng)

    def quit_window():
        worker_name = t.get("1.0", "end-1c")
        worker.name = worker_name
        root.quit()

    Button(root, text='סיום', command=quit_window).pack(side=BOTTOM)
    root.mainloop()

    root.destroy()
    return worker


if __name__ == '__main__':
    workers = []
    for i in range(num_workers):
        worker = view()
        workers.append(worker)
        worker.print_worker_pref()

    calculate_shifts(workers)
