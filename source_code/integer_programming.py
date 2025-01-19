from ortools.linear_solver import pywraplp

def Input():
    [T, N, M] = [int(e) for e in input().split()]

    class_subjects = {}
    for cl in range(1, N + 1):
        class_subjects[cl] = [int(e) for e in input().split()][:-1] # remove the 0 at the end of list
    
    teacher_subjects = {}
    for teacher in range(1, T + 1):
        teacher_subjects[teacher] = [int(e) for e in input().split()][:-1] # remove the 0 at the end of list

    subject_teachers = {}
    for subject in range(1, M + 1):
        subject_teachers[subject] = []
        for teacher in teacher_subjects:
            if subject in teacher_subjects[teacher]:
                subject_teachers[subject].append(teacher)

    subject_periods = [int(e) for e in input().split()]
    subject_periods.insert(0, 0) # add a 0 (dummy) at the beginning of the list to optimize the index

    return [T, M, N, subject_teachers, class_subjects, subject_periods]


def Solve(T, M, N, subject_teachers, class_subjects, subject_periods):
    solver = pywraplp.Solver.CreateSolver("SAT")

    # Parameters
    DAYS = 5
    SESSIONS_PER_DAY = 2
    PERIODS_PER_SESSION = 6
    TOTAL_PERIODS = DAYS * SESSIONS_PER_DAY * PERIODS_PER_SESSION

    # Variables
    # X[c, m, h] = True if class c, subject m at period h
    X = {}
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            for h in range(0, TOTAL_PERIODS + 1):
                X[(c, m, h)] = solver.BoolVar(f'X[{c},{m},{h}]')
                # X[(c, m, 0)] is dummy

    # Y[c, m, t] = True if class c, subject m is assigned to teacher t
    Y = {}
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            for t in subject_teachers[m]:
                Y[(c, m, t)] = solver.BoolVar(f'Y[{c},{m},{t}]')


    # Objective: Maximize the total number of class-subjects assigned
    solver.Maximize(sum(Y[(c, m, t)]
                       for c in range(1, N + 1)
                       for m in class_subjects[c]
                       for t in subject_teachers[m]
                       ))


    for c in range(1, N + 1):
        for m in class_subjects[c]:
            solver.Add(X[(c, m, 0)] == False) # dummy :D


    # Constraints

    # 1st: Each class-subject must be assigned to exactly one teacher
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            solver.Add(sum(Y[(c, m, t)] for t in subject_teachers[m]) <= 1)


    # 2nd: Each class-subject must be scheduled exactly the required number of periods, and those periods should be taught by the assigned teacher
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            solver.Add(sum(X[(c, m, h)] for h in range(TOTAL_PERIODS))
                      ==
                      sum(Y[(c, m, t)] for t in subject_teachers[m]) * subject_periods[m])

    # 3rd: A class can only study one subject at a time
    for c in range(1, N + 1):
        for h in range(1, TOTAL_PERIODS + 1):
            solver.Add(sum(X[(c, m, h)]
                            for m in class_subjects[c]) <= 1)

    # 4th: A teacher cannot teach multiple subjects or classes at a time
    for t in range(1, T + 1):
        for h in range(1, TOTAL_PERIODS + 1):
            tmparr = []
            for c in range(1, N + 1):
                for m in class_subjects[c]:
                    if t in subject_teachers[m]:
                        # tmp = x[c, m, h] * y[c, m, t]
                        tmp = solver.BoolVar(f"tmp_{t}_{h}_{c}_{m}")
                        solver.Add(tmp <= X[(c, m, h)])
                        solver.Add(tmp <= Y[(c, m, t)])
                        solver.Add(X[(c, m, h)] + Y[(c, m, t)] <= tmp + 1)
                        
                        tmparr.append(tmp)
            solver.Add(sum(tmparr) <= 1)

    # 5th: Enforce continuous periods for each subject in each class
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            subject_duration = subject_periods[m]
            for start_period in range(1, TOTAL_PERIODS + 1 - subject_duration):
                consecutive_periods = [X[(c, m, h)] for h in range(start_period, start_period + subject_duration)]
                
                tmp1 = solver.IntVar(-1, 1, f"tmp1_{c}_{m}_{start_period}")
                solver.Add(tmp1 == (X[(c, m, start_period)] - X[(c, m, start_period - 1)]))
                tmp2 = solver.IntVar(0, subject_duration, f"tmp2_{c}_{m}_{start_period}")
                solver.Add(tmp2 == sum(consecutive_periods))

                solver.Add(tmp1 + tmp2 <= subject_duration + 1)
                solver.Add(-tmp1 + tmp2 + (subject_duration) * (1 - tmp1) >= subject_duration - 1)

    status = solver.Solve()

    # Output results
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        cnt = 0
        cnt2 = 0
        output = []
        output_data = []
        for c in range(1, N + 1):
            for m in class_subjects[c]:
                for t in subject_teachers[m]:
                    if Y[(c, m, t)].solution_value() == 1:
                        cnt += 1
                        for h in range(TOTAL_PERIODS):
                            if X[(c, m, h)].solution_value() == 1:
                                cnt2 += 1
                                output.append(f"{c} {m} {h - 1} {t}")
                                output_data.append((c, m, h - 1, t))
                                break
        
        print(cnt)
        print("\n".join(output))
    else:
        print("No solution found.")

def Main():
    [T, M, N, teacher_subjects, class_subjects, subject_periods] = Input()
    Solve(T, M, N, teacher_subjects, class_subjects, subject_periods)

Main()