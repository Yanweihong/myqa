#!/usr/bin/env python3
# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys

if sys.version_info < (3, 5):
    raise RuntimeError('DrQA supports Python 3.5 or higher.')