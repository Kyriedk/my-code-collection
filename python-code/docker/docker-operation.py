import argparse
import json
import logging
import os

import docker


def load_and_push(path: str, registry: str, username: str, password: str) -> None:
    image_list = list()
    for (root, dirs, file) in os.walk(path):
        for f in file:
            if '.tgz' in f:
                image_list.append(f)

    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    client.login(username=username, password=password, registry=registry)

    image_info_dict = dict()
    for image_name in image_list:
        try:
            file_name = os.path.join(path, image_name)
            with open(file_name, "rb") as f:
                data = f.read()

            images = client.images.load(data)
            for image in images:
                if not image.attrs:
                    continue
                repository_list = image.attrs.get("RepoTags", [])
                repo = repository_list[0]
                info_list = repository_list[0].split("/")
                module_name = info_list[1]
                image = info_list[-1]
                if not image_info_dict.get(module_name, []):
                    image_info_dict[module_name] = list()
                image_info_dict[module_name].append(image)
                res = client.images.push(repo)
                print(res)
        except Exception as e:
            logging.error(e)

    json_object = json.dumps(image_info_dict, indent=4)

    with open("/tmp/image-info.json", "w") as outfile:
        outfile.write(json_object)


def main():
    parser = argparse.ArgumentParser(description="tool for process docker images")
    parser.add_argument("--dir", type=str)
    parser.add_argument("--registry", type=str)
    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)
    args = parser.parse_args()
    directory = args.dir
    registry = args.registry
    username = args.username
    password = args.password

    if not registry or not username or not password:
        logging.error("please provide registry, username and password")
        exit()

    if directory and os.path.exists(directory):
        load_and_push(directory, registry, username, password)
    else:
        logging.error("this directory does not exists :{}: %s\n" % dir)


if __name__ == "__main__":
    main()
