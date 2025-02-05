# -*- coding: utf-8 -*-

import re
import numpy as np
from skimage import exposure, measure
import tensorflow as tf
from keras import backend as K
from random import gauss
from tensorflow.python import math_ops
import os
from skimage import io


####### Ensemble des fonctions utiles pour la création des différents script #######

def sorted_aphanumeric(data):
    """
    :param data: list d'element alphanumerique.
    :return: list triee dans l'ordre croissant alphanumerique.
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def intersection(lst1, lst2):
    """
    :param lst1: list d'elements.
    :param lst2: list d'elements.
    :return: intersection de ses deux listes.
    """
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def contraste_and_reshape(souris):
    """
    :param souris: Ensemble d'image, verification si ensemble ou image unique avec la condition if.
    :return: Ensemble d'image avec contraste ameliore et shape modifie pour entrer dans le reseaux.
    """
    if len(souris.shape) > 2:
        data = []
        for i in np.arange(souris.shape[0]):
            img_adapteq = exposure.equalize_adapthist(souris[i], clip_limit=0.03)
            data.append(img_adapteq)
        data = np.array(data).reshape(-1, 128, 128, 1)
        return data
    else:
        img_adapteq = exposure.equalize_adapthist(souris, clip_limit=0.03)
        img = np.array(img_adapteq).reshape(128, 128, 1)
        return img

def calcul_numSouris(path_souris):
    """
    :param path_souris: path vers le dossier contenant des images de souris .tif
    :return: une liste contenant le numéro de chaque souris
    """
    list_souris = sorted_aphanumeric(os.listdir(path_souris))
    numSouris = []
    for k in np.arange(len(list_souris)):
        numSouris.append(int(re.findall('\d+', list_souris[k])[0]))
    return numSouris


def mean_iou(y_true, y_pred):
    """
    :param y_true: array de label annote.
    :param y_pred: array de label predit par le modele.
    :return: valeur de l'IoU.
    """
    prec = []
    for t in np.arange(0.5, 1.0, 0.05):
        y_pred_ = tf.to_int32(y_pred > t)
        score, up_opt = tf.metrics.mean_iou(y_true, y_pred, 2)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([up_opt]):
            score = tf.identity(score)
        prec.append(score)
    return K.mean(K.stack(prec), axis=0)


def apply_mask(img, mask):
    """
    :param img: image originale 128x128
    :param mask: masque 128x128 d'un objet de l'image originale
    :return: image 128x128 après application du masque
    """
    im = np.zeros((128, 128))
    for i in np.arange(128):
        for j in np.arange(128):
            if mask[i, j]:
                im[i, j] = img[i, j]*1
            else:
                im[i, j] = 0
    return im

def apply_mask_and_noise(img, mask, noise):
    """
    :param img: image originale 128x128
    :param mask: masque 128x128 d'un objet de l'image originale
    :param noise: intensité de pixel entre 0 et 255
    :return: image 128x128 après application du masque et zone masquée bruitée
    """
    im = np.zeros((128,128))
    for i in np.arange(128):
        for j in np.arange(128):
            if mask[i, j]:
                im[i, j] = img[i, j]*1
            else:
                im[i, j] = noise + gauss(0, 10)
    return im


def etale_hist(img):
    """
    :param img: image originale 128x128
    :return: image avec intensité des pixels compris entre 0 et 1
    """
    new_img = (img - img.min())*255/(img.max()-img.min())
    return new_img


def concat_data(a, b):
    """
    :param a: ensemble de x images 128x128
    :param b: ensemble de y images 128x128
    :return: ensemble concaténé de x+y images 128x128
    """
    new = np.zeros((np.shape(a)[0]+np.shape(b)[0], 128, 128))
    new[0:np.shape(a)[0]] = a
    new[np.shape(a)[0]:(np.shape(a)[0]+np.shape(b)[0])] = b
    return new

# def conc3D(a,b):
#
#     r = a.shape[0] + b.shape[0]
#     z = np.zeros(((r,128,128)))
#     for i in np.arange(a.shape[0]):
#         z[i] = a[i]
#     for j in np.arange(b.shape[0]):
#         z[(a.shape[0]+j)] = b[j]
#     return z

def inverse_binary_mask(msk):
    """
    :param msk: masque binaire 128x128
    :return: masque avec binarisation inversée 128x128
    """
    new_mask = np.ones((128, 128)) - msk
    return new_mask


def weight_map(label, a, b):
    """
    Création du carte de poids définissant une valeur d'importance pour chaque pixel
    Les pixels n'appartenant pas au masque ont une valeur de poids définit à 1 par défaut
    :param label: ensemble de x masque label 128x128
    :param a: valeur du poids pour pixel appartenant au maque
    :param b: valeur du poids pour pixel appartenant au contour du maque
    :return: ensemble de y weight map 128x128
    """
    weight = np.zeros((label.shape[0], 128, 128))

    for k in np.arange(label.shape[0]):

        lab = label[k]
        contour = measure.find_contours(lab, 0.8)
        indx_mask = np.where(lab == 1)[0]
        indy_mask = np.where(lab == 1)[1]

        w = np.ones((128, 128))
        w[indx_mask, indy_mask] = a

        for i in np.arange(len(contour)):
            indx_cont = np.array(contour[i][:, 0], dtype='int')
            indy_cont = np.array(contour[i][:, 1], dtype='int')
            w[indx_cont, indy_cont] = b

        #w = w ** 2
        weight[k] = w

    return(weight)


def weighted_cross_entropy(y_true, y_pred):
    """
    -- Fonction de coût pondéré --
    :param y_true: vrai valeur de y (label)
    :param y_pred: valeur prédite de y par le modèle
    :return: valeur de la fonction de cout d'entropie croisée pondérée
    """
    try:
        [seg, weight] = tf.unstack(y_true, 2, axis=3)

        seg = tf.expand_dims(seg, -1)
        weight = tf.expand_dims(weight, -1)
    except:
        pass

    epsilon = tf.convert_to_tensor(10e-8, y_pred.dtype.base_dtype)
    y_pred = tf.clip_by_value(y_pred, epsilon, 1 - epsilon)
    y_pred = tf.log(y_pred / (1 - y_pred))

    zeros = tf.zeros_like(y_pred, dtype=y_pred.dtype)  #array_ops
    cond = (y_pred >= zeros)
    relu_logits = math_ops.select(cond, y_pred, zeros)
    neg_abs_logits = math_ops.select(cond, -y_pred, y_pred)
    entropy = math_ops.add(relu_logits - y_pred * seg, math_ops.log1p(math_ops.exp(neg_abs_logits)), name=None)
    return K.mean(math_ops.multiply(weight, entropy), axis=-1)


def stats_pixelbased(y_true, y_pred):
    """Calculates pixel-based statistics
    (Dice, Jaccard, Precision, Recall, F-measure)
    Takes in raw prediction and truth data in order to calculate accuracy
    metrics for pixel based classfication. Statistics were chosen according
    to the guidelines presented in Caicedo et al. (2018) Evaluation of Deep
    Learning Strategies for Nucleus Segmentation in Fluorescence Images.
    BioRxiv 335216.
    Args:
        y_true (3D np.array): Binary ground truth annotations for a single
            feature, (batch,x,y)
        y_pred (3D np.array): Binary predictions for a single feature,
            (batch,x,y)
    Returns:
        dictionary: Containing a set of calculated statistics
    Raises:
        ValueError: Shapes of `y_true` and `y_pred` do not match.
    Warning:
        Comparing labeled to unlabeled data will produce low accuracy scores.
        Make sure to input the same type of data for `y_true` and `y_pred`
    """

    if y_pred.shape != y_true.shape:
        raise ValueError('Shape of inputs need to match. Shape of prediction '
                         'is: {}.  Shape of y_true is: {}'.format(
            y_pred.shape, y_true.shape))

    pred = y_pred
    truth = y_true

    # if pred.sum() == 0 and truth.sum() == 0:
    #     logging.warning('DICE score is technically 1.0, '
    #                     'but prediction and truth arrays are empty. ')

    if truth.sum() == 0:
        pred = inverse_binary_mask(pred)
        truth = inverse_binary_mask(truth)

    # Calculations for IOU
    intersection = np.logical_and(pred, truth)
    union = np.logical_or(pred, truth)

    # Sum gets count of positive pixels
    dice = (2 * intersection.sum() / (pred.sum() + truth.sum()))
    jaccard = intersection.sum() / union.sum()
    precision = intersection.sum() / pred.sum()
    recall = intersection.sum() / truth.sum()
    Fmeasure = (2 * precision * recall) / (precision + recall)

    return {
        'Dice': dice,
        'IoU': jaccard,
        'precision': precision,
        'recall': recall,
        'Fmeasure': Fmeasure
    }

def give_img(path, name, val_min, val_max):
    """
    Permet d'obtenir l'ensemble des slices du souris dans un intervalle
    :param path: path du dossier contenant les souris .tif
    :param name: nom de la souris .tif
    :param val_min: borne inférieure de l'intervalle
    :param val_max: borne supérieure de l'intervalle
    :return:
    """
    souris = io.imread(path + name)
    x = souris[val_min-1:val_max]
    return x