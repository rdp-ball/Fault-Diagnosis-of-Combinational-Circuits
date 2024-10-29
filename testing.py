import numpy as np
import itertools

def evaluate_boolean_expression(expression, variables):
    return int(eval(expression, {}, variables))

def generate_truth_table(circuit_description, input_nets, output_nets, fault_at, fault_type):
    input_combinations = list(itertools.product([0, 1], repeat=len(input_nets)))
    num_inputs = len(input_combinations)
    num_outputs = len(output_nets)
    truth_table = np.zeros((num_inputs, len(input_nets) + num_outputs), dtype=int)
    
    for i, inputs in enumerate(input_combinations):
        variables = {name: value for name, value in zip(input_nets, inputs)}
        former = variables.copy()
        
        if fault_at in input_nets:
            variables[fault_at] = fault_type
        
        for net, expression in circuit_description.items():
            if net != fault_at:
                variables[net] = evaluate_boolean_expression(expression, variables)
            else:
                variables[net] = fault_type
        
        row = [former[name] for name in input_nets] + [variables[name] for name in output_nets]
        truth_table[i] = row
    
    return truth_table

def generate_fault_matrices(circuit_description, input_nets, output_nets):
    fault_matrices = {}
    fault_types = [0, 1]  # Stuck-at-zero and stuck-at-one
    
    # Add a special case for no fault
    fault_matrices["no_fault"] = generate_truth_table(circuit_description, input_nets, output_nets, '#', -1)
    
    for fault_at in input_nets + list(circuit_description.keys()):
        for fault_type in fault_types:
            fault_key = f"{fault_at}_{fault_type}"
            fault_matrices[fault_key] = generate_truth_table(circuit_description, input_nets, output_nets, fault_at, fault_type)
    
    return fault_matrices

def find_faults(circuit_description, input_nets, output_nets, matrix):
    NoFault = generate_truth_table(circuit_description, input_nets, output_nets, '#', -1)
    inp_size = len(input_nets)
    
    for i in range(len(matrix)):
        for j in range(len(NoFault)):
            if np.array_equal(matrix[i][:inp_size], NoFault[j][:inp_size]):
                NoFault[j][inp_size:] = matrix[i][inp_size:]
    
    NoFault = np.array(NoFault)
    fault_matrices = generate_fault_matrices(circuit_description, input_nets, output_nets)
    
    print("Possible Single Stuck-at Faults:")
    for net, fault_matrix in fault_matrices.items():
        if np.array_equal(NoFault, fault_matrix):  # Using np.array_equal for exact equality
            fault_at, fault_type = net.split('_')
            print(f"Fault Site: {fault_at}, Fault Type: {int(fault_type)}")

# Example usage:
circuit_description = {
    "A": "A and A0",
    "L": "Be and BO",
    "B": "not(A and B0)",
    "C": "not(Ae or L)",
    "D": "not Co",
    "E": "C and C",
    "F": "D and D",
    "G": "E and F",
    "H": "B and B",
    "C1": "not(G and H)",
    "I": "not B",
    "J": "C and T",
    "K": "not D",
    "SO": "J ^ K",
    "L": "I and J",
    "M": "K and K",
    "N": "not(L and M)",
    "O": "N and N",
    "P": "N and N",
    "Q": "not(O and J)",
    "R": "not(P and K)",
    "SO": "not(Q and R)"
}

input_nets = ["C0", "A0", "B0"]
output_nets = ["SO", "C1"]

test_vectors = np.array([
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 1, 0, 0, 1],
    [1, 1, 1, 0, 2]
])

find_faults(circuit_description, input_nets, output_nets, test_vectors)
ans = generate_fault_matrices(circuit_description, input_nets, output_nets)

for key, val in ans.items():
    print(f"{key} : {val}")

no_fault = ans["no_fault"]
K_0 = ans["K_0"]
print("NoFault:\n", no_fault)
print()
print("K_0\n", K_0)
print()
print("Rows of K_0 that are different from NoFault:")

for i in range(len(no_fault)):
    temp1 = np.array(no_fault[i])
    temp2 = np.array(K_0[i])
    if not np.array_equal(temp1, temp2):
        print(temp2)
