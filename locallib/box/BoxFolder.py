from gasanalytics.box import *
from pathlib import Path
import warnings
class BoxFolder:
    def __init__(self, folder_name, parent_folder_id = None):
        self.name = folder_name
        self.id = None
        if parent_folder_id is None:
            raise ValueError('Parent folder id is required')
        self.parent_folder_id = parent_folder_id
        try:
            self.box_obj = create_subfolder(self.parent_folder_id, self.name)
            self.id = self.box_obj.id
        except Exception as e:
            print(f'Error creating folder {self.name}')
            folder_items = get_item_ids_in_folder(self.parent_folder_id)
            for key, value in folder_items.items():
                if key == self.name:
                    self.id = value
                    print(f'Folder {self.name} found in parent folder {self.parent_folder_id}')
                    break
            if self.id is None:
                raise ValueError(f'Folder {self.name} not found in parent folder {self.parent_folder_id}')