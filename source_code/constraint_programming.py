from ortools.sat.python import cp_model

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


def timetable_optimization(T, M, N, subject_teachers, class_subjects, subject_periods):
    model = cp_model.CpModel()

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
            for h in range(TOTAL_PERIODS):
                X[(c, m, h)] = model.NewBoolVar(f'X[{c},{m},{h}]')

    # Y[c, m, t] = True if class c, subject m is assigned to teacher t
    Y = {}
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            for t in subject_teachers[m]:
                Y[(c, m, t)] = model.NewBoolVar(f'Y[{c},{m},{t}]')


    # Objective: Maximize the total number of class-subjects assigned
    model.Maximize(sum(Y[(c, m, t)]
                       for c in range(1, N + 1)
                       for m in class_subjects[c]
                       for t in subject_teachers[m]
                       ))

    # Constraints

    # 1st: Each class-subject must be assigned to exactly one teacher
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            model.Add(sum(Y[(c, m, t)] for t in subject_teachers[m]) <= 1)


    # 2nd: Each class-subject must be scheduled exactly the required number of periods, and those periods should be taught by the assigned teacher
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            model.Add(sum(X[(c, m, h)] for h in range(TOTAL_PERIODS))
                      ==
                      sum(Y[(c, m, t)] for t in subject_teachers[m]) * subject_periods[m])

    # 3rd: A class can only study one subject at a time
    for c in range(1, N + 1):
        for h in range(TOTAL_PERIODS):
            model.Add(sum(X[(c, m, h)]
                            for m in class_subjects[c]) <= 1)

    # 4th: A teacher cannot teach multiple subjects or classes at a time
    for t in range(1, T + 1):
        for h in range(TOTAL_PERIODS):
            tmparr = []
            for c in range(1, N + 1):
                for m in class_subjects[c]:
                    if t in subject_teachers[m]:
                        tmp = model.NewBoolVar(f"tmp_{t}_{h}_{c}_{m}")
                        model.AddMultiplicationEquality(tmp, [X[(c, m, h)], Y[(c, m, t)]])
                        # tmp = x[c, m, h] * y[c, m, t]
                        tmparr.append(tmp)
            model.Add(sum(tmparr) <= 1)


    # 5th: Enforce continuous periods for each subject in each class
    for c in range(1, N + 1):
        for m in class_subjects[c]:
            subject_duration = subject_periods[m]
            for start_period in range(TOTAL_PERIODS - subject_duration):
                consecutive_periods = [X[(c, m, h)] for h in range(start_period, start_period + subject_duration)]
                
                if(start_period > 0):
                    tmp1 = model.NewBoolVar(f"tmp1_{c}_{m}_{start_period}")
                    model.AddBoolAnd([X[(c, m, start_period)], X[(c, m, start_period - 1)].Not()]).OnlyEnforceIf(tmp1)
                    model.AddBoolOr([X[(c, m, start_period)].Not(), X[(c, m, start_period - 1)]]).OnlyEnforceIf(tmp1.Not())
                    model.AddBoolAnd(consecutive_periods).OnlyEnforceIf(tmp1)
                else:
                    model.Add(sum(consecutive_periods) == subject_duration).OnlyEnforceIf(X[(c, m, start_period)])

    # Solve model
    solver = cp_model.CpSolver()
    # solver.parameters.enumerate_all_solutions = False
    # solver.parameters.optimize_with_core = True
    solver.parameters.max_time_in_seconds = 10 * 60
    # solver.parameters.max_deterministic_time = 15
    # solver.parameters.max_memory_in_mb = 100
    status = solver.Solve(model)

    # Output results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        cnt = 0
        output = []
        output_data = []
        for c in range(1, N + 1):
            for m in class_subjects[c]:
                for t in subject_teachers[m]:
                    if solver.Value(Y[(c, m, t)]) == 1:
                        cnt += 1
                        for h in range(TOTAL_PERIODS):
                            if solver.Value(X[(c, m, h)]) == 1:
                                output.append(f"{c} {m} {h} {t}")
                                output_data.append((c, m, h, t))
                                break
        
        print(cnt)
        print("\n".join(output))
    else:
        print("No solution found.")

[T, M, N, subject_teachers, class_subjects, subject_periods] = Input()
timetable_optimization(T, M, N, subject_teachers, class_subjects, subject_periods)