from mate_in_1_solver import *

def create_initial_generation(n, thread_pool):
    gen = [None] * n

    new_boards = thread_pool.imap(generate_starting_board, range(n), 10)
    start_time = time.perf_counter()
    for i, brd in enumerate(new_boards):
        gen[i] = brd
        if i%10 == 0:
            progress = str(i).rjust(9, " ")
            velocity = round(i/(time.perf_counter() - start_time))
            print("{}/{} Creating generation {}B/s".format(progress, n, velocity), end="\r")

    return gen

def score_generation(gen, thread_pool):
    gen_scores = np.zeros(len(gen))
    total_positions = 0
    velocity = 0

    start_time = time.time()
    fitnesses = thread_pool.imap(fitness, gen, 10)
    last_status = 0
    for i, (fit, moves) in enumerate(fitnesses):
        gen_scores[i] = fit
        total_positions += moves
        if total_positions - last_status > 1000:
            last_status = total_positions
            velocity = round(total_positions/(time.time() - start_time))
            progress = str(i).rjust(9, ' ')
            print("{}/{} Scoring generation {}N/s".format(progress, len(gen), velocity), end="\r")
    print(" "*80, end="\r")
    return gen_scores

def select_from_current_generation(gen, gen_scores, n):
    select_rate = 0.85

    k = round(n * select_rate)
    total_fitness = np.sum(gen_scores)
    p = total_fitness/k
    start = np.random.random() * p
    keep = []
    i = 0
    cum_fit = 0
    fits = np.arange(start, total_fitness, p)
    for floor_cum_fit in fits:
        while cum_fit + gen_scores[i] < floor_cum_fit:
            cum_fit += gen_scores[i]
            i += 1
        keep.append(gen[i])

    assert len(keep) == k
    return keep

def create_new_generation(parents, n):
    crossover_rate = 0.85
    mutation_rate = 0.05

    newgen = [None] * n
    total_tries = 0

    count = 0
    while True:
        b1, b2 = random.sample(parents, 2)
        if random.random() < crossover_rate:
            newb = blend_boards(b1, b2)
        else:
            newb = random.choice([b1, b2])

        if random.random() < mutation_rate:
            newb = mutate_board(newb)

        total_tries += 1
        if verify_board(newb):
            newgen[count] = newb
            count += 1
            progress = str(count).rjust(9, " ")
            print("{}/{} Creating generation".format(progress, n), end="\r")

        if count == n:
            break

    return newgen

def main_ga():
    if PLOTTING:
        plt.ion()
        plt.show()
    gen_size = 10000
    gens_to_keep = 100
    p = mp.Pool()

    gen = create_initial_generation(gen_size, p)
    gen_number = 1
    prev_gens = []
    while True:
        gen_scores = score_generation(gen, p)
        if PLOTTING:
            prev_gens.append(gen_scores)
            if len(prev_gens) > gens_to_keep:
                prev_gens = prev_gens[-gens_to_keep:]
            hists = []
            plt.figure(1)
            plt.clf()
            plot_curves_count = 10
            for i, g in enumerate(prev_gens[-plot_curves_count:]):
                opacity = 0.2
                if i == plot_curves_count - 1:
                    opacity = 1
                X = np.sort(g)
                Y = np.linspace(0, 1, len(g), endpoint=False)
                hists.append(plt.plot(X, Y, alpha=opacity, label="Gen {}".format(gen_number-len(prev_gens)+i+1)))
            plt.figure(2)
            plt.clf()
            for pct in [0, 25, 75, 100]:
                pct_fun = lambda arr: np.percentile(arr, pct)
                plt.plot(range(len(prev_gens)), list(map(pct_fun, prev_gens)))
            plt.plot(range(len(prev_gens)), list(map(np.mean, prev_gens)))
            plt.draw()
            plt.pause(0.001)

        best = max(gen_scores)
        print(gen[np.nonzero(gen_scores == best)[0][0]])
        print("Gen {}: {} Mates/{} Mean".format(gen_number, best, sum(gen_scores)/gen_size))
        parents = select_from_current_generation(gen, gen_scores, gen_size)
        gen = create_new_generation(parents, gen_size)
        gen_number += 1

if __name__ == "__main__":
    main_ga()
