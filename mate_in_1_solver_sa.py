from mate_in_1_solver import *

def acc_prob(cur, new, temp):
    if new > cur:
        return 1
    return math.exp((new - cur)/ temp)

def join_boards(b1, b2):
    b1 = str(b1).split('\n')
    b2 = str(b2).split('\n')
    res = []
    for l1, l2 in zip(b1, b2):
        res.append(l1 + " | " + l2)
    return "\n".join(res)

def main_sa():
    temp = decimal.Decimal(20)
    cooling_rate = decimal.Decimal(1) - decimal.Decimal('0.0000001')
    cur = generate_starting_board()
    cur_fit = fitness(cur)[0]
    best = cur
    best_fit = cur_fit
    count = 0
    moves = 0
    end = decimal.Decimal('0.2')
    while temp > end:
        while True:
            new = mutate_board(cur)
            if verify_board(new):
                break
        ft = fitness(new)
        new_fit = ft[0]
        moves += ft[1]
        ap = acc_prob(cur_fit, new_fit, temp)
        if ap > random.random():
            cur = new
            cur_fit = new_fit
        if new_fit > best_fit:
            best = new
            best_fit = new_fit
        count += 1
        if count % 50 == 0:
            print()
            print(join_boards(cur, best))
        print("{}/{:0>3}/{:0.8f}: {:0>3} {:0.3f}".format(
            str(count).rjust(8, ' '),
            best_fit,
            temp,
            cur_fit,
            ap), end='\r')
        temp *= cooling_rate

    print("Best:")
    print(best)
    print("{} Mates".format(best_fit))

if __name__ == "__main__":
    main_sa()
