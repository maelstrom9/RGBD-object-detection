import os
import numpy as np
import torch
import torch.utils.data
from PIL import Image
class EPFLDataset(torch.utils.data.Dataset):
    def __init__(self, transforms=None):
        self.transforms = transforms
        depth_channel0 = np.array(Image.open(image_directory + "depth"+ str(1).zfill(6) + ".png"))
        depth_channel1 = np.array(Image.open(image_directory + "depth"+ str(2).zfill(6) + ".png"))
        depth_channel2 = np.array(Image.open(image_directory + "depth"+ str(3).zfill(6) + ".png"))
        self.depth = np.array(depth_channel0 + depth_channel1 + depth_channel2)/3. 
        self.depth = self.depth[:,:] 



    def __getitem__(self, idx):
        idx += 34
        # load images ad masks
        img = Image.open(image_directory + "rgb"+ str(idx).zfill(6) + ".png").convert("RGB")
        depth = np.array(Image.open(image_directory + "depth"+ str(idx).zfill(6) + ".png"))
        mask = np.abs(np.array(depth) - self.depth)
        mask = mask - mask.min()
        mask = mask/mask.max()
        mask = mask > 0.1
        #img_array = mask
        img_array = img * mask[:,:,None]        
        #import pdb;pdb.set_trace()
        #final_img_arr = np.concatenate([img_array,depth_channel_array],axis=2)
        # id_to_bboxes represent bbox as https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.Rectangle.html
        boxes = id_to_bboxes[idx] if idx in id_to_bboxes else []
        num_objs = len(boxes)
        boxes_area = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.ones((num_objs,), dtype=torch.int64)
        image_id = torch.tensor([idx])
        area = boxes_area[:, 3] * (boxes_area[:, 2])
        bbox = []
        for box in boxes:
            bbox.append([box[0],box[1],box[0] + box[2], box[1] + box[3]])
        bbox = torch.as_tensor(bbox,dtype=torch.float32)
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)
        target = {}
        #[xmin,ymin,xmax,ymax]
        target["boxes"] = bbox
        # all 1 as we have pedestrians
        target["labels"] = labels
        # idx
        target["image_id"] = image_id
        # area of each bbox
        target["area"] = area
        # set crowd to false
        target["iscrowd"] = iscrowd
        if self.transforms is not None:
            img_array, target = self.transforms(img_array, target)
        return img_array, target

    def __len__(self):
        return 916
