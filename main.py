from ortools.sat.python import cp_model
from tkinter import *
from itertools import cycle

num_nurses = 5
num_shifts = 2
num_days = 7

def calculate_shifts(shift_requests):
    # This program tries to find an optimal assignment of nurses to shifts
    # (2 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # shift_requests = [[[0, 1], [0, 0], [0, 0], [0, 0], [0, 1],
    #                    [0, 1, 0], [0, 1]],
    #                   [[0, 0], [0, 0], [0, 0], [0, 0], [1, 0],
    #                    [0, 0], [0, 1]],
    #                   [[0, 0], [0, 0], [0, 0], [1, 0], [0, 0],
    #                    [0, 0], [0, 0]],
    #                   [[0, 1], [0, 0], [1, 0], [0, 0], [0, 0],
    #                    [1, 0], [0, 0]],
    #                   [[0, 0], [0, 1], [0, 0], [0, 0], [1, 0],
    #                    [0, 1], [0, 0]]]
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Each shift is assigned to exactly one nurse in .
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    # pylint: disable=g-complex-comprehension
    model.Minimize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_nurses
            for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_nurses:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] == 1:
                        print('Nurse', n, 'works shift', s, '(requested).')
                    else:
                        print('Nurse', n, 'works shift', s, '(not requested).')
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_nurses * min_shifts_per_nurse, ')')
    print('  - wall time       : %f s' % solver.WallTime())

class Checkbar(Frame):
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

   def print_worker_pref(self):
       print("worker pref: ", end='')
       for idx, x in enumerate(self.state()):
           if(x == 1):
               print(self.name_shifts[idx])
       print('')

from itertools import islice
def chunk(it, size):
    it = iter(it)
    return iter(lambda: list(islice(it, size)), [])

def view():
    root = Tk()
    myLabel = Label(root, text="בחר משמרות שאתה לא מעוניין לעבוד בהם")
    myLabel.pack()
    lng = Checkbar(root, ['ראשון בוקר', 'ראשון ערב', 'שני בוקר', 'שני ערב', 'שלישי בוקר', 'שלישי ערב', 'רביעי בוקר', 'רביעי ערב', 'חמישי בוקר', 'חמישי ערב', 'שישי בוקר', 'שישי ערב', 'שבת בוקר','שבת ערב' ])
    lng.pack(side=TOP, fill=X)
    lng.config(relief=GROOVE, bd=2)
    Button(root, text='סיום', command=root.quit).pack(side=BOTTOM)
    root.mainloop()

    result = []
    for var in lng.vars:
        result.append(var.get())
    result = list(chunk(result, num_shifts))

    lng.print_worker_pref()

    root.destroy()
    return result

if __name__ == '__main__':
    result = []
    for i in range(num_nurses):
        worker_pref = view()
        result.append(worker_pref)

    calculate_shifts(result)