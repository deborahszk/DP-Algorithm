import time
import tracemalloc

MAX_STEPS = 10000 

def davis_putnam(cnf, max_steps=MAX_STEPS):
    cnf = set(cnf)
    steps = 0

    while True:
        # Timeout check
        if steps >= max_steps:
            return None

        # Remove clauses containing pure literals
        pure_literals = find_pure_literals(cnf)
        if pure_literals:
            cnf = {clause for clause in cnf if all(lit not in clause for lit in pure_literals)}
            steps += 1
            continue

        # Unit propagation
        unit_clauses = {next(iter(clause)) for clause in cnf if len(clause) == 1}
        if unit_clauses:
            cnf = unit_propagate(cnf, unit_clauses)
            steps += 1
            continue

        # Empty clause = UNSAT
        if frozenset() in cnf:
            return False

        # No clauses left = SAT
        if not cnf:
            return True

        # Choose literal to resolve on
        lit = next(iter(next(iter(cnf))))  # pick any literal
        pos = resolve_literal(cnf, lit)
        neg = resolve_literal(cnf, negate(lit))
        cnf = pos | neg
        steps += 1

def find_pure_literals(cnf):
    literals = set()
    negations = set()
    for clause in cnf:
        for literal in clause:
            if literal.startswith('¬'):
                negations.add(literal[1:])
            else:
                literals.add(literal)
    pure = (literals - negations) | ({'¬' + l for l in (negations - literals)})
    return pure

def unit_propagate(cnf, unit_literals):
    new_cnf = set()
    for clause in cnf:
        if clause & unit_literals:
            continue
        new_clause = {lit for lit in clause if negate(lit) not in unit_literals}
        new_cnf.add(frozenset(new_clause))
    return new_cnf

def resolve_literal(cnf, literal):
    return {frozenset(clause - {literal}) for clause in cnf if literal in clause}

def negate(literal):
    return literal[1:] if literal.startswith('¬') else '¬' + literal

def print_cnf(cnf):
    return ' ∧ '.join(['(' + ' ∨ '.join(sorted(clause)) + ')' for clause in cnf])

# --- Test Examples ---
cnf_examples = [
    {'name': 'Trivial SAT', 'cnf': [{ 'A' }]},
    {'name': 'Trivial UNSAT', 'cnf': [{ 'A' }, { '¬A' }]},
    {'name': 'Simple SAT', 'cnf': [{ 'A', 'B' }, { '¬A' }]},
    {'name': 'Simple UNSAT', 'cnf': [{ 'A' }, { 'B' }, { '¬A', '¬B' }]},
    {'name': 'Chain SAT', 'cnf': [{ 'A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }]},
    {'name': 'Chain UNSAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', '¬A' }]},
    {'name': '3-SAT SAT', 'cnf': [{ 'A', 'B', 'C' }, { '¬A', 'D', 'E' }, { '¬B', '¬E', 'F' }]},
    {'name': '3-SAT UNSAT', 'cnf': [{ 'A' }, { 'B' }, { 'C' }, { '¬A', '¬B' }, { '¬B', '¬C' }, { '¬C', '¬A' }]},
    {'name': 'Redundant SAT', 'cnf': [{ 'A' }, { 'A', 'B' }, { 'A', 'B', 'C' }]},
    {'name': 'Deep Contradiction', 'cnf': [{ 'A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', '¬A' }]},
    {'name': 'Pure Literal SAT', 'cnf': [{ 'A' }, { 'B', 'C' }, { 'C', 'D' }]},
    {'name': 'Unit Propagation SAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }]},
    {'name': 'Deep UNSAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', '¬A' }]},
    {'name': 'Complex 3-SAT SAT', 'cnf': [{ 'A', 'B', 'C' }, { '¬A', 'D', 'E' }, { '¬B', '¬E', 'F' }, { '¬C', 'F', 'G' }, { '¬D', '¬F', 'G' }]},
    {'name': 'Hard contradiction', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', 'F' }, { '¬F', '¬A' }]},
]

for i, example in enumerate(cnf_examples, start=1):
    name = example['name']
    cnf = {frozenset(clause) for clause in example['cnf']}

    print(f"Example {i}: {name}")
    print("CNF:", print_cnf(cnf))

    tracemalloc.start()
    start = time.perf_counter()
    result = davis_putnam(cnf)
    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result is None:
        print("Result:️ Too complex")
    elif result is True:
        print("Result: SATISFIABLE")
    else:
        print("Result: UNSATISFIABLE")

    print(f" Time: {(end - start) * 1e6:.2f} μs")
    print(f" Peak memory: {peak / 1024:.2f} KB")
