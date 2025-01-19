#PYTHON 
import random

# ---------------------------------------------------------------------------------------
# HÀM ĐỌC DỮ LIỆU TỪ INPUT
# ---------------------------------------------------------------------------------------
def read_input():
    # Đọc số lượng giáo viên, lớp học và môn học
    T, N, M = map(int, input().split())
    
    # Đọc danh sách môn học của mỗi lớp
    class_subjects = [[] for _ in range(N + 1)]
    for x in range(1, N + 1):
        class_subjects[x] = list(map(int, input().split()[:-1]))
    
    # Đọc danh sách môn học mà mỗi giáo viên có thể dạy
    teacher_subjects = [[] for _ in range(T + 1)]
    for t in range(1, T + 1):
        teacher_subjects[t] = list(map(int, input().split()[:-1]))
    
    # Đọc thời gian tiết của mỗi môn học
    duration = [0] + list(map(int, input().split()))
    
    return T, N, M, class_subjects, teacher_subjects, duration
# ---------------------------------------------------------------------------------------
# CẤU TRÚC GIẢI PHÁP (SOLUTION) & HỖ TRỢ KIỂM TRA HỢP LỆ
# ---------------------------------------------------------------------------------------
# Mỗi slot = 1 tiết, ta có 60 slot (5 ngày * 2 buổi * 6 tiết = 60)
# Ta đánh số slot từ 1..60, giả sử slot 1..6 = sáng ngày 1, 7..12 = chiều ngày 1, ...
MAX_SLOT = 60

def is_valid_assignment(x, y, start_slot, v,
                        solution,
                        occupied_class, occupied_teacher,
                        duration, teacher_subjects):
    """ Kiểm tra xem có thể xếp (lớp x, môn y) tại slot start_slot, giáo viên v) không """
    d = duration[y]  # số tiết môn y
    # 1. start_slot + d - 1 <= 60
    if start_slot + d - 1 > MAX_SLOT:
        return False

    # 2. Giáo viên v có dạy môn y không?
    if y not in teacher_subjects[v]:
        return False

    # 3. Kiểm tra lớp x có bị trùng slot?
    for s in range(start_slot, start_slot + d):
        if occupied_class[x][s]:
            return False

    # 4. Kiểm tra giáo viên v có bị trùng slot?
    for s in range(start_slot, start_slot + d):
        if occupied_teacher[v][s]:
            return False

    # Nếu không vi phạm thì ok
    return True

def apply_assignment(x, y, start_slot, v,
                     solution,
                     occupied_class, occupied_teacher,
                     duration):
    """ Ghi nhận (x, y) -> (start_slot, v) vào solution và cập nhật occupied """
    d = duration[y]
    solution[(x, y)] = (start_slot, v)
    # đánh dấu occupied
    for s in range(start_slot, start_slot + d):
        occupied_class[x][s] = True
        occupied_teacher[v][s] = True

def remove_assignment(x, y,
                      solution,
                      occupied_class, occupied_teacher,
                      duration):
    """ Tháo gỡ (x, y) khỏi solution, cập nhật lại occupied """
    if (x, y) not in solution or solution[(x, y)] is None:
        return
    start_slot, v = solution[(x, y)]
    d = duration[y]
    # remove occupied
    for s in range(start_slot, start_slot + d):
        occupied_class[x][s] = False
        occupied_teacher[v][s] = False
    solution[(x, y)] = None

# ---------------------------------------------------------------------------------------
# HÀM TÍNH ĐIỂM (SCORE) = SỐ LỚP-MÔN ĐÃ XẾP
# ---------------------------------------------------------------------------------------
def compute_score(solution):
    count = 0
    for k, val in solution.items():
        if val is not None:
            count += 1
    return count

# ---------------------------------------------------------------------------------------
# KHỞI TẠO GIẢI PHÁP BAN ĐẦU
# ---------------------------------------------------------------------------------------
def initialize_solution(T, N, M,
                       class_subjects, teacher_subjects, duration):
    """ 
    Khởi tạo random: lần lượt duyệt (x,y) theo thứ tự ngẫu nhiên,
    cố gắng gán (start_slot, teacher) khả thi đầu tiên tìm được.
    """
    solution = {}
    occupied_class = [[False]*(MAX_SLOT+1) for _ in range(N+1)]
    occupied_teacher = [[False]*(MAX_SLOT+1) for _ in range(T+1)]

    all_class_sub = []
    for x in range(1, N+1):
        for y in class_subjects[x]:
            all_class_sub.append((x,y))
    random.shuffle(all_class_sub)

    for (x,y) in all_class_sub:
        assigned = False
        possible_teachers = [t for t in range(1, T+1) if y in teacher_subjects[t]]
        random.shuffle(possible_teachers)
        
        # Thử các slot + teacher ngẫu nhiên
        start_slots = list(range(1, MAX_SLOT+1))
        random.shuffle(start_slots)

        for v in possible_teachers:
            for s in start_slots:
                if is_valid_assignment(x, y, s, v,
                                       solution,
                                       occupied_class, occupied_teacher,
                                       duration, teacher_subjects):
                    apply_assignment(x, y, s, v,
                                     solution,
                                     occupied_class, occupied_teacher,
                                     duration)
                    assigned = True
                    break
            if assigned: 
                break

        if not assigned:
            solution[(x,y)] = None  # chưa xếp được

    return solution, occupied_class, occupied_teacher

# ---------------------------------------------------------------------------------------
# SINH LÁNG GIỀNG (NEIGHBOR) BẰNG CÁC "MOVE" NHỎ
# ---------------------------------------------------------------------------------------
def get_neighbor_solution(solution,
                          occupied_class, occupied_teacher,
                          T, N, M,
                          class_subjects, teacher_subjects, duration):
    """
    Sinh 1 láng giềng bằng cách chọn ngẫu nhiên 1 trong các "move":
      - Move 1: Đổi kíp bắt đầu của 1 lớp-môn đã xếp.
      - Move 2: Đổi giáo viên của 1 lớp-môn đã xếp.
      - Move 3: Thử xếp 1 lớp-môn chưa xếp (nếu còn).
    Ta chỉ sinh 1 láng giềng để so sánh.
    """

    # Sao chép solution và occupied
    new_solution = dict(solution)
    new_occupied_class = [row[:] for row in occupied_class]
    new_occupied_teacher = [row[:] for row in occupied_teacher]

    assigned_class_subs = [(x,y) for (x,y) in new_solution.keys()
                                 if new_solution[(x,y)] is not None]
    unassigned_class_subs = [(x,y) for (x,y) in new_solution.keys()
                                   if new_solution[(x,y)] is None]

    # Lựa chọn move
    moves = []
    if assigned_class_subs:
        moves.append("move_slot")
        moves.append("move_teacher")
    if unassigned_class_subs:
        moves.append("assign_unassigned")

    if not moves:
        # Không có gì để move, trả về chính nó
        return new_solution, new_occupied_class, new_occupied_teacher

    chosen_move = random.choice(moves)

    # Move 1: Đổi kíp bắt đầu
    if chosen_move == "move_slot":
        (x,y) = random.choice(assigned_class_subs)
        # tháo ra
        remove_assignment(x, y, new_solution,
                          new_occupied_class, new_occupied_teacher, duration)
        # thử gán slot khác
        possible_slots = list(range(1, MAX_SLOT+1))
        random.shuffle(possible_slots)
        start_assigned = False
        _, old_teacher = solution[(x,y)]
        for s in possible_slots:
            if is_valid_assignment(x, y, s, old_teacher,
                                   new_solution,
                                   new_occupied_class, new_occupied_teacher,
                                   duration, teacher_subjects):
                apply_assignment(x, y, s, old_teacher,
                                 new_solution,
                                 new_occupied_class, new_occupied_teacher,
                                 duration)
                start_assigned = True
                break
        # nếu không gán được, để None
        if not start_assigned:
            new_solution[(x,y)] = None

    # Move 2: Đổi giáo viên
    elif chosen_move == "move_teacher":
        (x,y) = random.choice(assigned_class_subs)
        # tháo ra
        remove_assignment(x, y, new_solution,
                          new_occupied_class, new_occupied_teacher, duration)
        possible_teachers = [t for t in range(1, T+1) if y in teacher_subjects[t]]
        random.shuffle(possible_teachers)
        start_slots = list(range(1, MAX_SLOT+1))
        random.shuffle(start_slots)

        assigned_ = False
        for v in possible_teachers:
            for s in start_slots:
                if is_valid_assignment(x, y, s, v,
                                       new_solution,
                                       new_occupied_class, new_occupied_teacher,
                                       duration, teacher_subjects):
                    apply_assignment(x, y, s, v,
                                     new_solution,
                                     new_occupied_class, new_occupied_teacher,
                                     duration)
                    assigned_ = True
                    break
            if assigned_:
                break
        if not assigned_:
            new_solution[(x,y)] = None

    # Move 3: Gán 1 lớp-môn chưa xếp
    elif chosen_move == "assign_unassigned":
        (x,y) = random.choice(unassigned_class_subs)
        possible_teachers = [t for t in range(1, T+1) if y in teacher_subjects[t]]
        random.shuffle(possible_teachers)
        start_slots = list(range(1, MAX_SLOT+1))
        random.shuffle(start_slots)

        assigned_ = False
        for v in possible_teachers:
            for s in start_slots:
                if is_valid_assignment(x, y, s, v,
                                       new_solution,
                                       new_occupied_class, new_occupied_teacher,
                                       duration, teacher_subjects):
                    apply_assignment(x, y, s, v,
                                     new_solution,
                                     new_occupied_class, new_occupied_teacher,
                                     duration)
                    assigned_ = True
                    break
            if assigned_:
                break

    return new_solution, new_occupied_class, new_occupied_teacher

# ---------------------------------------------------------------------------------------
# HILL CLIMBING CHÍNH
# ---------------------------------------------------------------------------------------
def hill_climbing(T, N, M, class_subjects, teacher_subjects, duration,
                  max_iterations=2000):
    """
    Triển khai hill climbing:
      1. Khởi tạo lời giải
      2. Lặp sinh láng giềng, nếu cải thiện thì thay
      3. Dừng khi hết vòng lặp hoặc không cải thiện
    """
    # Khởi tạo
    solution, occupied_class, occupied_teacher = initialize_solution(
        T, N, M, class_subjects, teacher_subjects, duration
    )
    best_solution = dict(solution)
    best_occupied_class = [row[:] for row in occupied_class]
    best_occupied_teacher = [row[:] for row in occupied_teacher]
    best_score = compute_score(best_solution)

    for iteration in range(max_iterations):
        # Sinh neighbor
        new_solution, new_occupied_class, new_occupied_teacher = get_neighbor_solution(
            best_solution,
            best_occupied_class,
            best_occupied_teacher,
            T, N, M,
            class_subjects, teacher_subjects, duration
        )
        new_score = compute_score(new_solution)

        # So sánh
        if new_score > best_score:
            best_solution = new_solution
            best_occupied_class = new_occupied_class
            best_occupied_teacher = new_occupied_teacher
            best_score = new_score
        else:
            # Nếu không cải thiện, có thể bỏ qua
            pass

    return best_solution, best_score

# ---------------------------------------------------------------------------------------
# HÀM MAIN CHẠY THỬ
# ---------------------------------------------------------------------------------------
def main():
    # Đọc input
    T, N, M, class_subjects, teacher_subjects, duration = read_input()

    # Gọi hill_climbing
    best_sol, best_score = hill_climbing(
        T, N, M,
        class_subjects, teacher_subjects, duration,
        max_iterations=2000  # Bạn có thể điều chỉnh
    )

    # In ra kết quả
    # best_sol[(x,y)] = (start_slot, teacher)
    # Đề bài yêu cầu:
    # Dòng 1: K (tổng số lớp-môn xếp được)
    # Tiếp theo K dòng: x y u v
    print(best_score)
    for (x,y), val in best_sol.items():
        if val is not None:
            start_slot, v = val
            print(x, y, start_slot, v)

main()
