def config_parser(config_path):
    with open(config_path, "r", encoding='utf-8') as file:
        config = dict()
        lines = file.readlines()
        for line in lines:
            k, v = line.split(' = ')
            config[k] = v.split('\n')[0]
        return config
