import os
import json

def get_doc_metadata():

    """
    Retrieves source folder metadata.

    Parameters:
    None

    Returned value:
    A JSON containing source folder metadata
    """

    try:
        with open("meta/file_list.json", "r") as f:
            file_list = json.load(f)
        return file_list
    except FileNotFoundError as fnf:
        # Creates a file if it does not exist
        file_list = {}
        for doc in os.listdir("docs"):
            file_list[doc] = {"modified_date" : str(os.path.getmtime(f"docs/{doc}")), 
                              "size" : str(os.path.getsize(f"docs/{doc}"))}
        with open("meta/file_list.json", "w") as f:
            json.dump(file_list, f)
        return file_list
    except Exception as e:
        raise Exception(f"An unexpected error has occurred: {e}")

def update_metadata() -> bool:

    """
    Function which triggers command to update the vector database when the source folder has any change 
    (files added, changed or removed).

    Parameters:
    None

    Returned value:
    bool - indicates if any changes in the source folder were detected
    """

    update = False

    # 1. get metadata from folder
    file_list = {}
    for doc in os.listdir("docs"):
        file_list[doc] = {"modified_date" : str(os.path.getmtime(f"docs/{doc}")), 
                            "size" : str(os.path.getsize(f"docs/{doc}"))}

    # 2. compare with existing metadata and update if any changes found
    with open("meta/file_list.json", "r") as f:
        current_metadata = json.load(f)

    # different files in the folder
    is_list_same_as_meta = sorted(list(file_list.keys())) == sorted(list(current_metadata.keys()))
    is_file_changed = False

    if is_list_same_as_meta:
        print(list(file_list.keys()).sort())
        print(list(current_metadata.keys()).sort())
        for doc in list(file_list.keys()):
            print(file_list[doc], current_metadata[doc])
            if file_list[doc] != current_metadata[doc]:
                is_file_changed = True
                break

    # update metadata file is any changes found
    if not is_list_same_as_meta or is_file_changed:
        with open("meta/file_list.json", "w") as f:
            json.dump(file_list, f)
        update = True

    return update
     

if __name__ == "__main__":

    file_list = get_doc_metadata()
    update = update_metadata()

    print(file_list)
    print(update)