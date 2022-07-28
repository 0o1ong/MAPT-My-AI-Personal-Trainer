def get_routine(routine):
    total_exercise = routine[0]
    total_info = exercise_split(total_exercise)
    total_num = routine[1]
    total_set = routine[2]

    for i in range(len(total_info)):
        total_info[i].append(int(total_num[:2]))
        total_info[i].append(int(total_set[:1]))
        total_num = total_num[2:]
        total_set = total_set[1:]

    return total_info


def exercise_split(total_exercise):
    exercise = []
    while True:
        letter = total_exercise[0]
        if letter == "S":
            idx = 14
            data = "shoulderpress"
        elif letter == "L":
            idx = 5
            data = "lunge"
        else:
            idx = 7
            data = "pushup"
        
        exercise.append([data])
        total_exercise = total_exercise[idx:]
        if len(total_exercise) < 5:
            break
    return exercise