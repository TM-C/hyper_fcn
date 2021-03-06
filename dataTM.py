import os, sys, cv2, argparse
from shutil import copy2
import numpy as np
import tensorflow as tf
import zipfile 
from pathlib import Path

def download_dataset(dataPath):
    
    #BASE_PATH = tf.keras.utils.get_file('flower_photos',
    #                        'http://download.tensorflow.org/example_images/flower_photos.tgz',
    #                        untar=True, cache_dir='.')
     
    BASE_PATH = dataPath
    print(f"Downloaded and extracted at {BASE_PATH}")

    return BASE_PATH

def split_dataset(BASE_PATH = 'flower_photos', DATASET_PATH = 'dataset', train_images = 300, val_images = 50):
    # Specify path to the downloaded folder
    classes = os.listdir(BASE_PATH)

    # Specify path for copying the dataset into train and val sets
    os.makedirs(DATASET_PATH, exist_ok=True)

    # Creating train directory
    train_dir = os.path.join(DATASET_PATH, 'train')
    os.makedirs(train_dir, exist_ok=True)

    # Creating val directory
    val_dir = os.path.join(DATASET_PATH, 'val')
    os.makedirs(val_dir, exist_ok=True)    

    # Copying images from original folder to dataset folder
    for class_name in classes:
        if len(class_name.split('.')) >= 2:
            continue
        print(f"Copying images for {class_name}...")
        
        # Creating destination folder (train and val)
        class_train_dir = os.path.join(train_dir, class_name)
        os.makedirs(class_train_dir, exist_ok=True)
        
        class_val_dir = os.path.join(val_dir, class_name)
        os.makedirs(class_val_dir, exist_ok=True)

        # Shuffling the image list
        class_path = os.path.join(BASE_PATH, class_name)
        class_images = os.listdir(class_path)
        np.random.shuffle(class_images)

        for image in class_images[:train_images]:
            copy2(os.path.join(class_path, image), class_train_dir)
        for image in class_images[train_images:train_images+val_images]:
            copy2(os.path.join(class_path, image), class_val_dir)

def get_dataset_stats(DATASET_PATH = 'dataset'):
    """
        This utility gives the following stats for the dataset:
        TOTAL_IMAGES: Total number of images for each class in train and val sets
        AVG_IMG_HEIGHT: Average height of images across complete dataset (incl. train and val)
        AVG_IMG_WIDTH: Average width of images across complete dataset (incl. train and val)
        MIN_HEIGHT: Minimum height of images across complete dataset (incl. train and val)
        MIN_WIDTH: Minimum width of images across complete dataset (incl. train and val)
        MAX_HEIGHT: Maximum height of images across complete dataset (incl. train and val)
        MAX_WIDTH: Maximum width of images across complete dataset (incl. train and val)

        NOTE: You should have enough memory to load complete dataset
    """
    train_dir = os.path.join(DATASET_PATH, 'train')
    val_dir = os.path.join(DATASET_PATH, 'val')

    len_classes = len(os.listdir(train_dir))

    assert len(os.listdir(train_dir)) == len(os.listdir(val_dir))

    avg_height = 0
    min_height = np.inf
    max_height = 0

    avg_width = 0
    min_width = np.inf
    max_width = 0

    total_train = 0
    print('\nTraining dataset stats:')
    for class_name in os.listdir(train_dir):
        class_path = os.path.join(train_dir, class_name)
        class_images = os.listdir(class_path)
        
        for img_name in class_images:
            h, w, c = cv2.imread(os.path.join(class_path, img_name)).shape
            avg_height += h
            avg_width += w
            min_height = min(min_height, h)
            min_width = min(min_width, w)
            max_height = max(max_height, h)
            max_width = max(max_width, w)
        
        total_train += len(class_images)
        print(f'--> Images in {class_name}: {len(class_images)}')
    
    total_val = 0
    print('\nValidation dataset stats:')
    for class_name in os.listdir(val_dir):
        class_path = os.path.join(val_dir, class_name)
        class_images = os.listdir(class_path)
        
        for img_name in class_images:
            h, w, c = cv2.imread(os.path.join(class_path, img_name)).shape
            avg_height += h
            avg_width += w
            min_height = min(min_height, h)
            min_width = min(min_width, w)
            max_height = max(max_height, h)
            max_width = max(max_width, w)

        total_val += len(class_images)
        print(f'--> Images in {class_name}: {len(os.listdir(os.path.join(val_dir, class_name)))}')

    IMG_HEIGHT = avg_height // total_train
    IMG_WIDTH = avg_width // total_train
    
    print()
    print(f'AVG_IMG_HEIGHT: {IMG_HEIGHT}')
    print(f'AVG_IMG_WIDTH: {IMG_WIDTH}')
    print(f'MIN_HEIGHT: {min_height}')
    print(f'MIN_WIDTH: {min_width}')
    print(f'MAX_HEIGHT: {max_height}')
    print(f'MAX_WIDTH: {max_width}')
    print()

    return len_classes, train_dir, val_dir, IMG_HEIGHT, IMG_WIDTH, total_train, total_val

def parse_args(args):
    """
    Example command:
    $ $ python data.py --train-count 500 --val-count 100
    """
    parser = argparse.ArgumentParser(description='Optimize RetinaNet anchor configuration')
    parser.add_argument('--train-count', type=int, help='Number of training images to be used for each class.')
    parser.add_argument('--val-count', type=int, help='Number of validation images to be used for each class.')
    parser.add_argument('--data-path', type=str, help='Path to directory of images. Each class is in a folder.')

    return parser.parse_args(args)


def main(args=None):
    # Parse command line arguments.
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    
    # Number of images required in train and val sets
    train_images = args.train_count
    val_images = args.val_count
    dataPath = args.data_path
    
    print(dataPath)

    
    BASE_PATH = download_dataset(dataPath)
       
    split_dataset(BASE_PATH=BASE_PATH, train_images = train_images, val_images = val_images)
    get_dataset_stats()

if __name__ == "__main__":
    
    main()
