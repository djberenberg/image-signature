#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#
# author: dan berenberg
import secrets
from typing import Tuple
from operator import concat
from functools import reduce
from pathlib import Path

# image processing lib
from PIL import Image

import numpy as np

SECRET_LEN = 8
class User(object):
    """barebones user"""
    def __init__(self, **metadata):    
        self.metadata = metadata
        self.__token = secrets.token_hex(SECRET_LEN)
        self.__userid = int(sum(map(ord, self.__token)))
        #self.__userid = int(sum(
        #                        map(ord, 
        #                             reduce(concat,
        #                                    map(str, metadata.values())))))
        
    def __getitem__(self, key):
        return self.metadata.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self.metadata.__setitem(key, value)
    
    @property
    def userid(self):
        return self.__userid
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.metadata})"
    
    def __repr__(self):
        return str(self)


def generate_mask(mask_size, img_height, img_width, seed=None):
    # generating a mask -- it's just a `mask_size` many coordinates 
    # that live on an `img_height` x `img_width` grid
    if seed is not None:
        np.random.seed(seed)
        
    left  = np.random.randint(low=0, high=img_height, size=mask_size)
    right = np.random.randint(low=0, high=img_width, size=mask_size)
    return left, right

def apply_signature(img: np.ndarray, fillvalue=1., mask_size=5, seed=None):
    # gathering the mask information
    height, width = img.shape[:2]
    mask_fst, mask_snd = generate_mask(mask_size, 
                                       height, width, seed=seed)
    
    # applying the mask
    img[mask_fst, mask_snd, :] = fillvalue
    return img, (mask_fst, mask_snd)


def apply_signature_given_user(img, user):
    seed = user.userid
    signed, mask_info = apply_signature(img, mask_size=5, seed=seed)
    
    return signed, mask_info

def recover_user_from_signature(img: np.ndarray, users, mask_size=5, fillvalue=1.):
    h, w, _ = img.shape
    for user in users:
        mask_info = generate_mask(mask_size, h, w, seed=user.userid)
        vals = img[mask_info[0], mask_info[1], :].ravel()
        if (vals == fillvalue).all():
            return user
    return None

if __name__ == '__main__':
    image_path = "data/spidey.jpg"
    signed_image_path = Path(image_path).parent / f"{Path(image_path).stem}-SIGNED.jpg"
    # read the image
    image = Image.open(image_path)
    
    # convert to matrix (rgb format)
    MAX_PIXEL_VAL = 255.
    img_mat = np.asarray(image)
    img_mat = img_mat / MAX_PIXEL_VAL

    print(f"image is {img_mat.shape[0]} x {img_mat.shape[1]} with channel order {image.mode}")

    me = User(name='samus', lastname='aran')
    you = User(name='mario', lastname='luigi')
    badguy = User(name="blackbeard", lastname='yarr')
	
    userdb = [me, you, badguy]
    print([(user['name'], user.userid) for user in userdb])
	
    signed, maskinfo = apply_signature_given_user(img_mat, badguy)
    signed_image = Image.fromarray( (signed * 255).astype(np.uint8) )

    pirate = recover_user_from_signature(signed, userdb)
    
    signed_image.save(signed_image_path)
    print(f"saved {image_path} to {signed_image_path}")
    print(f"busted: {pirate['name']}")

