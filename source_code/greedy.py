#PYTHON 
def can_assign(schedule, class_id, subject, start_time, periods, teacher_schedule):
    # Check if the time slots are available for both class and teacher
    end_time = start_time + periods - 1
    
    # Check class schedule
    for t in range(start_time, end_time + 1):
        if schedule[class_id][t]:
            return False
            
    # Check teacher schedule
    for t in range(start_time, end_time + 1):
        if teacher_schedule[t]:
            return False
            
    return True

def solve_scheduling():
    # Read input
    T, N, M = map(int, input().split())
    
    # Read class subjects
    class_subjects = []
    for _ in range(N):
        subjects = list(map(int, input().split()))
        class_subjects.append(subjects[:-1])  # Remove the trailing 0
    
    # Read teacher capabilities
    teacher_subjects = []
    for _ in range(T):
        subjects = list(map(int, input().split()))
        teacher_subjects.append(subjects[:-1])  # Remove the trailing 0
    
    # Read subject periods
    subject_periods = list(map(int, input().split()))
    
    # Initialize schedules
    total_periods = 5 * 2 * 6  # 5 days * 2 sessions * 6 periods
    schedule = [[False] * total_periods for _ in range(N)]  # Class schedule
    teacher_schedules = [[False] * total_periods for _ in range(T)]  # Teacher schedules
    
    # Store assignments
    assignments = []  # (class_id, subject, start_time, teacher_id)
    
    # Try to assign each class-subject
    for class_id in range(N):
        for subject in class_subjects[class_id]:
            periods = subject_periods[subject-1]
            assigned = False
            
            # Try each teacher
            for teacher_id in range(T):
                if subject not in teacher_subjects[teacher_id]:
                    continue
                    
                # Try each possible start time
                for start_time in range(total_periods - periods + 1):
                    if can_assign(schedule, class_id, subject, start_time, periods, 
                                teacher_schedules[teacher_id]):
                        # Assign the slots
                        for t in range(start_time, start_time + periods):
                            schedule[class_id][t] = True
                            teacher_schedules[teacher_id][t] = True
                            
                        assignments.append((class_id + 1, subject, start_time + 1, teacher_id + 1))
                        assigned = True
                        break
                        
                if assigned:
                    break
    
    # Output results
    print(len(assignments))
    for class_id, subject, start_time, teacher_id in sorted(assignments):
        print(class_id, subject, start_time, teacher_id)

# Run the solution
solve_scheduling()