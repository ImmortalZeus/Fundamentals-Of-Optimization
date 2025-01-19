#PYTHON 
import time

def parse_input():
    # Read T, N, M
    T, N, M = map(int, input().split())

    # Read class_subjects
    class_subjects = {}
    for i in range(1, N + 1):
        class_subjects[i] = list(map(int, input().split()))[:-1]  # Remove the trailing 0

    # Read teacher_subjects
    teacher_subjects = {}
    for i in range(N + 1, N + T + 1):
        teacher_subjects[i - N] = list(map(int, input().split()))[:-1]  # Remove the trailing 0

    # Read subject_periods
    subject_periods = list(map(int, input().split()))
    subject_periods = {i + 1: subject_periods[i] for i in range(len(subject_periods))}

    return T, N, M, class_subjects, teacher_subjects, subject_periods

def tabu_search_with_heuristic(T, N, M, class_subjects, teacher_subjects, subject_periods, max_iter=500, tabu_tenure=20):
    total_slots = 5 * 2 * 6  # Total time slots

    # feasible arr
    feasible_arr = list()

    # Initialize solutions
    current_solution = []
    best_solution = []
    best_K = 0

    # Tabu list
    tabu_list = set()

    # Helper: Generate heuristic-based neighbors
    def generate_neighbors(solution):
        neighbors = []
        # Prioritize unassigned class-subjects
        unassigned = []
        assigned = {(x, y) for x, y, _, _ in solution}
        for class_id, subjects in class_subjects.items():
            for subject_id in subjects:
                if (class_id, subject_id) not in assigned:
                    unassigned.append((class_id, subject_id))

        # Limit the number of neighbors generated
        for class_id, subject_id in unassigned[:min(len(unassigned), 5)]:
            for teacher_id in teacher_subjects:
                if subject_id in teacher_subjects[teacher_id]:
                    for start_time in range(1, total_slots - subject_periods[subject_id] + 1, 1):  # Skip intervals to reduce neighbors
                        new_assignment = (class_id, subject_id, start_time, teacher_id)
                        neighbors.append(solution + [new_assignment])

        # Optionally, remove an existing assignment
        if len(solution) > 0:
            for i in range(min(len(solution), 5)):  # Limit removals to the first 5
                neighbors.append(solution[:i] + solution[i + 1:])

        return neighbors

    # Feasibility check
    def is_feasible(solution):
        if(solution in feasible_arr):
            return True
        
        class_schedule = {i: set() for i in range(1, N + 1)}
        teacher_schedule = {i: set() for i in range(1, T + 1)}

        for x, y, u, v in solution:
            # Check if the teacher can teach this subject
            if y not in teacher_subjects[v]:
                return False

            # Check if the subject belongs to the class
            if y not in class_subjects[x]:
                return False

            # Check for class conflicts
            for t in range(u, u + subject_periods[y]):
                if t in class_schedule[x]:
                    return False
                class_schedule[x].add(t)

            # Check for teacher conflicts
            for t in range(u, u + subject_periods[y]):
                if t in teacher_schedule[v]:
                    return False
                teacher_schedule[v].add(t)
        feasible_arr.append(solution)
        return True

    # Tabu Search loop
    start_time = time.time() # this is to limit the runtime

    for _ in range(max_iter):
        # Generate neighbors using heuristic
        neighbors = generate_neighbors(current_solution)

        # Filter feasible neighbors
        feasible_neighbors = [n for n in neighbors if is_feasible(n)]

        if not feasible_neighbors:
            continue

        # Select the best neighbor not in tabu list
        feasible_neighbors.sort(key=lambda s: len(s), reverse=True)
        for neighbor in feasible_neighbors:
            neighbor_key = tuple(sorted(neighbor))
            if neighbor_key not in tabu_list:
                current_solution = neighbor
                tabu_list.add(neighbor_key)
                break

        # Update tabu list
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop()

        # Update the best solution
        if len(current_solution) > best_K:
            best_solution = current_solution
            best_K = len(current_solution)

        if(time.time() - start_time > 600):  # this is to limit the runtime
            break

    return best_K, best_solution

T, N, M, class_subjects, teacher_subjects, subject_periods = parse_input()
K, timetable = tabu_search_with_heuristic(T, N, M, class_subjects, teacher_subjects, subject_periods)

print(K)
for x, y, u, v in timetable:
    print(x, y, u, v)