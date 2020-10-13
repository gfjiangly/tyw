# coding:utf8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import yaml
import copy
import logging
import numpy as np
import os
import os.path as osp
from ast import literal_eval


from tyw.utils.collections import AttrDict

logger = logging.getLogger(__name__)

__C = AttrDict()
# Consumers can get config by:
#   from config import cfg
cfg = __C

__C.DEBUG = False
__C.DATA = 'data/'

# ---------------------------------------------------------------------------- #
# draw options
# ---------------------------------------------------------------------------- #
__C.PROCESSOR = AttrDict()
__C.PROCESSOR.USE_CLEAR = False
__C.PROCESSOR.ANN_SRC = 'E:/tyw-data/original/anns'
__C.PROCESSOR.DISCARD = 0


# Random note: avoid using '.ON' as a config key since yaml converts it to True;
# prefer 'ENABLED' instead


# ---------------------------------------------------------------------------- #
# PPG options
# ---------------------------------------------------------------------------- #
__C.PPG = AttrDict()
__C.PPG.LOOK_BACK = 100
__C.PPG.THRESHOLD = 200
__C.PPG.INTERVAL_UP_THRESHOLD = 3000


# ---------------------------------------------------------------------------- #
# EDA options
# ---------------------------------------------------------------------------- #
__C.EDA = AttrDict()
__C.EDA.DOWN_SAMPLE = 100
__C.EDA.LOOK_BACK = 100

__C.EDA.H_TH = 0.
__C.EDA.L_TH = 0.

__C.EDA.MEAN = 0.
__C.EDA.MEAN_STD = 1.
__C.EDA.MEAN_PROP = 2.

__C.EDA.MAX_MIN = 1.
__C.EDA.MAX_MIN_STD = 1.
__C.EDA.MAX_MIN_PROP = 5.

__C.EDA.FEATS_MEAN = False
__C.EDA.FEATS_MAX_MIN = False
__C.EDA.FEATS_LEARN = False

__C.EDA.STAT_FILES_MEAN = False

__C.EDA.DRAW_FRAGMENTS = False
__C.EDA.DRAW_WHOLE = False
__C.EDA.DRAW_FEATURES = False
__C.EDA.DRAW_FILES_MEAN = True

__C.EDA.ADAPT_TH = True


# ---------------------------------------------------------------------------- #
# TRAIN options
# ---------------------------------------------------------------------------- #
__C.TRAIN = AttrDict()
__C.TRAIN.HUNGRY_MODEL = AttrDict()
__C.TRAIN.HUNGRY_MODEL.TYPE = 'lstm'
__C.TRAIN.HUNGRY_MODEL.LAYERS = [6, 30, 20, 7]
__C.TRAIN.HUNGRY_MODEL.LOOK_BACK = 100
__C.TRAIN.HUNGRY_MODEL.BATCH_SIZE = 32
__C.TRAIN.HUNGRY_MODEL.EPOCHS = 12
__C.TRAIN.HUNGRY_MODEL.COLUMN_NUM = 1
__C.TRAIN.HUNGRY_MODEL.CLASS_NUM = 2

__C.TRAIN.TIRED_MODEL = AttrDict()
__C.TRAIN.TIRED_MODEL.TYPE = 'lstm'
__C.TRAIN.TIRED_MODEL.LAYERS = [6, 30, 20, 7]
__C.TRAIN.TIRED_MODEL.LOOK_BACK = 100
__C.TRAIN.TIRED_MODEL.BATCH_SIZE = 32
__C.TRAIN.TIRED_MODEL.EPOCHS = 12
__C.TRAIN.TIRED_MODEL.COLUMN_NUM = 1
__C.TRAIN.TIRED_MODEL.CLASS_NUM = 2


# ---------------------------------------------------------------------------- #
# TEST options
# ---------------------------------------------------------------------------- #
__C.TEST = AttrDict()
__C.TEST.HUNGRY_MODEL = AttrDict()
__C.TEST.HUNGRY_MODEL.OPEN = False
__C.TEST.HUNGRY_MODEL.PATH = '../model_file/200-30-20-0.869565_cont.h5'
__C.TEST.FEAR_MODEL = AttrDict()
__C.TEST.FEAR_MODEL.OPEN = False


# ---------------------------------------------------------------------------- #
# CACHE options
# ---------------------------------------------------------------------------- #
__C.CACHE = AttrDict()
__C.CACHE.CLEAR = 'E:/tyw-data/original/clear'
__C.CACHE.PPG = '.cache/ppg'


# ---------------------------------------------------------------------------- #
# draw options
# ---------------------------------------------------------------------------- #
__C.DRAW = AttrDict()
__C.DRAW.PPG = False
__C.DRAW.PPG_PATH = 'E:/tyw-data/draw/ppg'
__C.DRAW.PATH = 'draw/'
__C.DRAW.EDA_WHOLE = False
__C.DRAW.EDA_FEATURES = False
__C.DRAW.EDA_FILES_MEAN = False
__C.DRAW.EDA_FRAGMENTS = False


def assert_and_infer_cfg():
    """Call this function in your script after you have finished setting all cfg
    values that are necessary (e.g., merging a config from a file, merging
    command line config options, etc.). By default, this function will also
    mark the global cfg as immutable to prevent changing the global cfg settings
    during script execution (which can lead to hard to debug errors or code
    that's harder to understand than is necessary).
    """
    pass


def cache_cfg_urls():
    """Download URLs in the config, cache them locally, and rewrite cfg to make
    use of the locally cached file.
    """
    pass


def get_output_dir(datasets, training=True):
    """Get the output directory determined by the current global config."""
    assert isinstance(datasets, tuple([tuple, list] + list(six.string_types))), \
        'datasets argument must be of type tuple, list or string'
    is_string = isinstance(datasets, six.string_types)
    dataset_name = datasets if is_string else ':'.join(datasets)
    tag = 'train' if training else 'test'
    # <output-dir>/<train|test>/<dataset-name>/<model-type>/
    outdir = osp.join(__C.OUTPUT_DIR, tag, dataset_name, __C.MODEL.TYPE)
    if not osp.exists(outdir):
        os.makedirs(outdir)
    return outdir


def merge_cfg_from_file(cfg_filename):
    """Load a yaml config file and merge it into the global config."""
    with open(cfg_filename, 'r', encoding='UTF-8') as f:
        yaml_cfg = AttrDict(yaml.load(f, Loader=yaml.FullLoader))
    _merge_a_into_b(yaml_cfg, __C)


def merge_cfg_from_cfg(cfg_other):
    """Merge `cfg_other` into the global config."""
    _merge_a_into_b(cfg_other, __C)


def merge_cfg_from_list(cfg_list):
    """Merge config keys, values in a list (e.g., from command line) into the
    global config. For example, `cfg_list = ['TEST.NMS', 0.5]`.
    """
    assert len(cfg_list) % 2 == 0
    for full_key, v in zip(cfg_list[0::2], cfg_list[1::2]):
        # if _key_is_deprecated(full_key):
        #     continue
        # if _key_is_renamed(full_key):
        #     _raise_key_rename_error(full_key)
        key_list = full_key.split('.')
        d = __C
        for subkey in key_list[:-1]:
            assert subkey in d, 'Non-existent key: {}'.format(full_key)
            d = d[subkey]
        subkey = key_list[-1]
        assert subkey in d, 'Non-existent key: {}'.format(full_key)
        value = _decode_cfg_value(v)
        value = _check_and_coerce_cfg_value_type(
            value, d[subkey], subkey, full_key
        )
        d[subkey] = value


def _merge_a_into_b(a, b, stack=None):
    """Merge config dictionary a into config dictionary b, clobbering the
    options in b whenever they are also specified in a.
    """
    assert isinstance(a, AttrDict), \
        '`a` (cur type {}) must be an instance of {}'.format(type(a), AttrDict)
    assert isinstance(b, AttrDict), \
        '`b` (cur type {}) must be an instance of {}'.format(type(b), AttrDict)

    for k, v_ in a.items():
        full_key = '.'.join(stack) + '.' + k if stack is not None else k
        # a must specify keys that are in b
        if k not in b:
            # if _key_is_deprecated(full_key):
            #     continue
            # elif _key_is_renamed(full_key):
            #     _raise_key_rename_error(full_key)
            # else:
            raise KeyError('Non-existent config key: {}'.format(full_key))

        v = copy.deepcopy(v_)
        v = _decode_cfg_value(v)
        v = _check_and_coerce_cfg_value_type(v, b[k], k, full_key)

        # Recursively merge dicts
        if isinstance(v, AttrDict):
            try:
                stack_push = [k] if stack is None else stack + [k]
                _merge_a_into_b(v, b[k], stack=stack_push)
            except BaseException:
                raise
        else:
            b[k] = v


def _decode_cfg_value(v):
    """Decodes a raw config value (e.g., from a yaml config files or command
    line argument) into a Python object.
    """
    # Configs parsed from raw yaml will contain dictionary keys that need to be
    # converted to AttrDict objects
    if isinstance(v, dict):
        return AttrDict(v)
    # All remaining processing is only applied to strings
    if not isinstance(v, six.string_types):
        return v
    # Try to interpret `v` as a:
    #   string, number, tuple, list, dict, boolean, or None
    try:
        v = literal_eval(v)
    # The following two excepts allow v to pass through when it represents a
    # string.
    #
    # Longer explanation:
    # The type of v is always a string (before calling literal_eval), but
    # sometimes it *represents* a string and other times a data structure, like
    # a list. In the case that v represents a string, what we got back from the
    # yaml parser is 'foo' *without quotes* (so, not '"foo"'). literal_eval is
    # ok with '"foo"', but will raise a ValueError if given 'foo'. In other
    # cases, like paths (v = 'foo/bar' and not v = '"foo/bar"'), literal_eval
    # will raise a SyntaxError.
    except ValueError:
        pass
    except SyntaxError:
        pass
    return v


def _check_and_coerce_cfg_value_type(value_a, value_b, key, full_key):
    """Checks that `value_a`, which is intended to replace `value_b` is of the
    right type. The type is correct if it matches exactly or is one of a few
    cases in which the type can be easily coerced.
    """
    # The types must match (with some exceptions)
    type_b = type(value_b)
    type_a = type(value_a)
    if type_a is type_b:
        return value_a

    # Exceptions: numpy arrays, strings, tuple<->list
    if isinstance(value_b, np.ndarray):
        value_a = np.array(value_a, dtype=value_b.dtype)
    elif isinstance(value_b, six.string_types):
        value_a = str(value_a)
    elif isinstance(value_a, tuple) and isinstance(value_b, list):
        value_a = list(value_a)
    elif isinstance(value_a, list) and isinstance(value_b, tuple):
        value_a = tuple(value_a)
    else:
        raise ValueError(
            'Type mismatch ({} vs. {}) with values ({} vs. {}) for config '
            'key: {}'.format(type_b, type_a, value_b, value_a, full_key)
        )
    return value_a
