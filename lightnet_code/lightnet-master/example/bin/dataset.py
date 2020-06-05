import copy
import logging
from PIL import Image
import torch
from torchvision import transforms as tf
import brambox as bb
import lightnet as ln

__all__ = ['VOCDataset']
log = logging.getLogger('lightnet.VOC.dataset')

# def identify_file(img_id):
#     return f'/Users/sai/Downloads/lightnet-master/data/VOCdevkit/{img_id}.jpg'

def identify_file(img_id):
    return f'epfl_lab/20140804_160621_00/{img_id}'

class VOCDataset(ln.models.BramboxDataset):
    """ Pascal VOC dataset, with annotations generated by `brambox.io.parser.box.PandasParser`

    Args:
        anno_file (str or Path): Path to annotation file (must be parseable by PandasParser)
        params (lightnet.engine.HyperParameters): Hyperparameters for this data (See Note)
        augment (boolean): Whether to perform data augmentation
        kwargs (optional): extra keyword arguments to pass on to the `brambox.io.load()` function

    Note:
        The hyperparameters object should at least contain the following attributes:

        - params.input_dimension (tuple): tuple containing base (width,height) for the network
        - params.class_label_map (list): List of class_labels (can be **None**, but this might lead to undeterministic behaviour)
        - params.anno_filter (str, optional): How to filter difficult annotations: ['ignore', 'rm', 'none']; Default **'none'**
        - params.flip (float): chance to flip the image
        - params.jitter (float): jitter percentage
        - params.hue (float): Hue change percentage
        - params.saturation (float): Saturation change percentage
        - params.value (float): Value change percentage
    """
    def __init__(self, anno_file, params, augment, **kwargs):
        annos = bb.io.load('pandas', anno_file, **kwargs)

        # Filter data
        self.filter = getattr(params, 'filter_anno', 'none')
        if not self.filter in ('ignore', 'rm', 'none'):
            log.error(f'filter ({self.filter}) is not one of [ignore, rm, none]. Choosing default "none" value')

        if self.filter == 'ignore':
            annos.loc[annos.difficult, 'ignore'] = True
        elif self.filter == 'rm':
            annos = annos[~annos.difficult]

        # Data transformation pipeline
        lb  = ln.data.transform.Letterbox(dataset=self)
        img_tf = ln.data.transform.Compose([lb, tf.ToTensor()])
        anno_tf = ln.data.transform.Compose([lb])
        augment = False  ## I have added.
        if augment:
            rf  = ln.data.transform.RandomFlip(params.flip)
            rc  = ln.data.transform.RandomJitter(params.jitter, True, 0.1)
            hsv = ln.data.transform.RandomHSV(params.hue, params.saturation, params.value)
            img_tf[0:0] = [hsv, rc, rf]
            anno_tf[0:0] = [rc, rf]

        super().__init__(annos, params.input_dimension, params.class_label_map, identify_file, img_tf, anno_tf)