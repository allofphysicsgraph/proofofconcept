
def arg_count(inference_rule):
    # these should be determined based on string match in CSV file
    num_input = 2
    num_feed = 1
    num_output = 1
    return num_input, num_feed, num_output


if __name__ == '__main__':
    print compute(1, 0.1)  # default values
