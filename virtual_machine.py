from vm.file_loader import FileLoader


def main():
    file_loader = FileLoader("./output/out.obj")
    (quadruples, functions, memory, constants) = file_loader.get_data()
    print(quadruples)


if __name__ == "__main__":
    main()
