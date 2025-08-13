import numpy as np
import tensorflow as tf
from tensorflow.python.platform import flags
from utils import (
    conv_cond_concat,
    groupsort,
    init_attention_weight,
    init_conv_weight,
    init_fc_weight,
    init_res_weight,
    smart_atten_block,
    smart_conv_block,
    smart_fc_block,
    smart_res_block,
    swish,
)

flags.DEFINE_bool("swish_act", False, "use the swish activation for dsprites")

FLAGS = flags.FLAGS


class MnistNet(object):
    def __init__(self, num_channels=1, num_filters=64):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.datasource = FLAGS.datasource

        if FLAGS.cclass:
            self.label_size = 10
        else:
            self.label_size = 0

    def construct_weights(self, scope=""):
        weights = {}

        dtype = tf.float32
        conv_initializer = tf.contrib.layers.xavier_initializer_conv2d(dtype=dtype)
        fc_initializer = tf.contrib.layers.xavier_initializer(dtype=dtype)

        classes = 1

        with tf.variable_scope(scope):
            init_conv_weight(weights, "c1_pre", 3, 1, 64)
            init_conv_weight(weights, "c1", 4, 64, self.dim_hidden, classes=classes)
            init_conv_weight(
                weights, "c2", 4, self.dim_hidden, 2 * self.dim_hidden, classes=classes
            )
            init_conv_weight(
                weights,
                "c3",
                4,
                2 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(
                weights,
                "fc_dense",
                4 * 4 * 4 * self.dim_hidden,
                2 * self.dim_hidden,
                spec_norm=True,
            )
            init_fc_weight(weights, "fc5", 2 * self.dim_hidden, 1, spec_norm=False)

        if FLAGS.cclass:
            self.label_size = 10
        else:
            self.label_size = 0
        return weights

    def forward(
        self, inp, weights, reuse=False, scope="", stop_grad=False, label=None, **kwargs
    ):
        self.channels
        weights = weights.copy()
        inp = tf.reshape(inp, (tf.shape(inp)[0], 28, 28, 1))

        if FLAGS.swish_act:
            act = swish
        else:
            act = tf.nn.leaky_relu

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        if FLAGS.cclass:
            label_d = tf.reshape(
                label, shape=(tf.shape(label)[0], 1, 1, self.label_size)
            )
            inp = conv_cond_concat(inp, label_d)

        h1 = smart_conv_block(
            inp, weights, reuse, "c1_pre", use_stride=False, activation=act
        )
        h2 = smart_conv_block(
            h1,
            weights,
            reuse,
            "c1",
            use_stride=True,
            downsample=True,
            label=label,
            extra_bias=False,
            activation=act,
        )
        h3 = smart_conv_block(
            h2,
            weights,
            reuse,
            "c2",
            use_stride=True,
            downsample=True,
            label=label,
            extra_bias=False,
            activation=act,
        )
        h4 = smart_conv_block(
            h3,
            weights,
            reuse,
            "c3",
            use_stride=True,
            downsample=True,
            label=label,
            use_scale=False,
            extra_bias=False,
            activation=act,
        )

        h5 = tf.reshape(h4, [-1, np.prod([int(dim) for dim in h4.get_shape()[1:]])])
        h6 = act(smart_fc_block(h5, weights, reuse, "fc_dense"))
        hidden6 = smart_fc_block(h6, weights, reuse, "fc5")

        return hidden6


class DspritesNet(object):
    def __init__(
        self,
        num_channels=1,
        num_filters=64,
        cond_size=False,
        cond_shape=False,
        cond_pos=False,
        cond_rot=False,
        label_size=1,
    ):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.img_size = 64
        self.label_size = label_size

        if FLAGS.cclass:
            self.label_size = 3

        try:
            if FLAGS.dshape_only:
                self.label_size = 3

            if FLAGS.dpos_only:
                self.label_size = 2

            if FLAGS.dsize_only:
                self.label_size = 1

            if FLAGS.drot_only:
                self.label_size = 2
        except BaseException:
            pass

        if cond_size:
            self.label_size = 1

        if cond_shape:
            self.label_size = 3

        if cond_pos:
            self.label_size = 2

        if cond_rot:
            self.label_size = 2

        self.cond_size = cond_size
        self.cond_shape = cond_shape
        self.cond_pos = cond_pos

    def construct_weights(self, scope=""):
        weights = {}

        dtype = tf.float32
        conv_initializer = tf.contrib.layers.xavier_initializer_conv2d(dtype=dtype)
        fc_initializer = tf.contrib.layers.xavier_initializer(dtype=dtype)
        classes = self.label_size

        with tf.variable_scope(scope):
            init_conv_weight(weights, "c1_pre", 3, 1, 32)
            init_conv_weight(weights, "c1", 4, 32, self.dim_hidden, classes=classes)
            init_conv_weight(
                weights, "c2", 4, self.dim_hidden, 2 * self.dim_hidden, classes=classes
            )
            init_conv_weight(
                weights,
                "c3",
                4,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_conv_weight(
                weights,
                "c4",
                4,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(
                weights,
                "fc_dense",
                2 * 4 * 4 * self.dim_hidden,
                2 * self.dim_hidden,
                spec_norm=True,
            )
            init_fc_weight(weights, "fc5", 2 * self.dim_hidden, 1, spec_norm=False)

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
        return_logit=False,
    ):
        self.channels
        batch_size = tf.shape(inp)[0]

        inp = tf.reshape(inp, (batch_size, 64, 64, 1))

        if FLAGS.swish_act:
            act = swish
        else:
            act = tf.nn.leaky_relu

        if not FLAGS.cclass:
            label = None

        weights = weights.copy()

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        h1 = smart_conv_block(
            inp, weights, reuse, "c1_pre", use_stride=False, activation=act
        )
        h2 = smart_conv_block(
            h1,
            weights,
            reuse,
            "c1",
            use_stride=True,
            downsample=True,
            label=label,
            extra_bias=True,
            activation=act,
        )
        h3 = smart_conv_block(
            h2,
            weights,
            reuse,
            "c2",
            use_stride=True,
            downsample=True,
            label=label,
            extra_bias=True,
            activation=act,
        )
        h4 = smart_conv_block(
            h3,
            weights,
            reuse,
            "c3",
            use_stride=True,
            downsample=True,
            label=label,
            use_scale=True,
            extra_bias=True,
            activation=act,
        )
        h5 = smart_conv_block(
            h4,
            weights,
            reuse,
            "c4",
            use_stride=True,
            downsample=True,
            label=label,
            extra_bias=True,
            activation=act,
        )

        hidden6 = tf.reshape(h5, (tf.shape(h5)[0], -1))
        hidden7 = act(smart_fc_block(hidden6, weights, reuse, "fc_dense"))
        energy = smart_fc_block(hidden7, weights, reuse, "fc5")

        if return_logit:
            return hidden7
        else:
            return energy


class ResNet32(object):
    def __init__(self, num_channels=3, num_filters=128):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.groupsort = groupsort()

    def construct_weights(self, scope=""):
        weights = {}
        tf.float32

        if FLAGS.cclass:
            classes = 10
        else:
            classes = 1

        with tf.variable_scope(scope):
            # First block
            init_conv_weight(weights, "c1_pre", 3, self.channels, self.dim_hidden)
            init_res_weight(
                weights,
                "res_optim",
                3,
                self.dim_hidden,
                self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights, "res_1", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights,
                "res_2",
                3,
                self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_3",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_4",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(
                weights, "fc_dense", 4 * 4 * 2 * self.dim_hidden, 4 * self.dim_hidden
            )
            init_fc_weight(weights, "fc5", 2 * self.dim_hidden, 1, spec_norm=False)

            init_attention_weight(
                weights,
                "atten",
                2 * self.dim_hidden,
                self.dim_hidden / 2,
                trainable_gamma=True,
            )

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
    ):
        weights = weights.copy()
        tf.shape(inp)[0]

        act = tf.nn.leaky_relu

        if not FLAGS.cclass:
            label = None

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        # Make sure gradients are modified a bit
        inp = smart_conv_block(inp, weights, reuse, "c1_pre", use_stride=False)

        hidden1 = smart_res_block(
            inp, weights, reuse, "res_optim", adaptive=False, label=label, act=act
        )
        hidden2 = smart_res_block(
            hidden1,
            weights,
            reuse,
            "res_1",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
            act=act,
        )
        hidden3 = smart_res_block(
            hidden2,
            weights,
            reuse,
            "res_2",
            stop_batch=stop_batch,
            label=label,
            act=act,
        )

        if FLAGS.use_attention:
            hidden4 = smart_atten_block(
                hidden3, weights, reuse, "atten", stop_at_grad=stop_at_grad, label=label
            )
        else:
            hidden4 = smart_res_block(
                hidden3,
                weights,
                reuse,
                "res_3",
                adaptive=False,
                downsample=False,
                stop_batch=stop_batch,
                label=label,
                act=act,
            )

        hidden5 = smart_res_block(
            hidden4,
            weights,
            reuse,
            "res_4",
            stop_batch=stop_batch,
            adaptive=False,
            label=label,
            act=act,
        )
        compact = hidden6 = smart_res_block(
            hidden5,
            weights,
            reuse,
            "res_5",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        hidden6 = tf.nn.relu(hidden6)
        hidden5 = tf.reduce_sum(hidden6, [1, 2])

        hidden6 = smart_fc_block(hidden5, weights, reuse, "fc5")

        energy = hidden6

        return energy


class ResNet32Large(object):
    def __init__(self, num_channels=3, num_filters=128, train=False):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.dropout = train
        self.train = train

    def construct_weights(self, scope=""):
        weights = {}
        tf.float32

        if FLAGS.cclass:
            classes = 10
        else:
            classes = 1

        with tf.variable_scope(scope):
            # First block
            init_conv_weight(weights, "c1_pre", 3, self.channels, self.dim_hidden)
            init_res_weight(
                weights,
                "res_optim",
                3,
                self.dim_hidden,
                self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights, "res_1", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_2", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights,
                "res_3",
                3,
                self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_4",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_6",
                3,
                2 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_7",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_8",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(weights, "fc5", 4 * self.dim_hidden, 1, spec_norm=False)

            init_attention_weight(
                weights,
                "atten",
                2 * self.dim_hidden,
                self.dim_hidden,
                trainable_gamma=True,
            )

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
    ):
        weights = weights.copy()
        tf.shape(inp)[0]

        if not FLAGS.cclass:
            label = None

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        # Make sure gradients are modified a bit
        inp = smart_conv_block(inp, weights, reuse, "c1_pre", use_stride=False)

        dropout = self.dropout
        train = self.train

        hidden1 = smart_res_block(
            inp,
            weights,
            reuse,
            "res_optim",
            adaptive=False,
            label=label,
            dropout=dropout,
            train=train,
        )
        hidden2 = smart_res_block(
            hidden1,
            weights,
            reuse,
            "res_1",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
            dropout=dropout,
            train=train,
        )
        hidden3 = smart_res_block(
            hidden2,
            weights,
            reuse,
            "res_2",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
            dropout=dropout,
            train=train,
        )
        hidden4 = smart_res_block(
            hidden3,
            weights,
            reuse,
            "res_3",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
        )

        if FLAGS.use_attention:
            hidden5 = smart_atten_block(
                hidden4, weights, reuse, "atten", stop_at_grad=stop_at_grad
            )
        else:
            hidden5 = smart_res_block(
                hidden4,
                weights,
                reuse,
                "res_4",
                adaptive=False,
                downsample=False,
                stop_batch=stop_batch,
                label=label,
                dropout=dropout,
                train=train,
            )

        hidden6 = smart_res_block(
            hidden5,
            weights,
            reuse,
            "res_5",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
        )

        hidden7 = smart_res_block(
            hidden6,
            weights,
            reuse,
            "res_6",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
        )
        hidden8 = smart_res_block(
            hidden7,
            weights,
            reuse,
            "res_7",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
        )

        compact = hidden9 = smart_res_block(
            hidden8,
            weights,
            reuse,
            "res_8",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
        )

        if FLAGS.cclass:
            hidden6 = tf.nn.leaky_relu(hidden9)
        else:
            hidden6 = tf.nn.relu(hidden9)
        hidden5 = tf.reduce_sum(hidden6, [1, 2])

        hidden6 = smart_fc_block(hidden5, weights, reuse, "fc5")

        energy = hidden6

        return energy


class ResNet32Wider(object):
    def __init__(self, num_channels=3, num_filters=128, train=False):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.dropout = train
        self.train = train

    def construct_weights(self, scope=""):
        weights = {}
        tf.float32

        if FLAGS.cclass and FLAGS.dataset == "cifar10":
            classes = 10
        elif FLAGS.cclass and FLAGS.dataset == "imagenet":
            classes = 1000
        else:
            classes = 1

        with tf.variable_scope(scope):
            # First block
            init_conv_weight(weights, "c1_pre", 3, self.channels, 128)
            init_res_weight(
                weights, "res_optim", 3, 128, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_1", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_2", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights,
                "res_3",
                3,
                self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_4",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_6",
                3,
                2 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_7",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_8",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(weights, "fc5", 4 * self.dim_hidden, 1, spec_norm=False)

            init_attention_weight(
                weights,
                "atten",
                self.dim_hidden,
                self.dim_hidden / 2,
                trainable_gamma=True,
            )

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
    ):
        weights = weights.copy()
        tf.shape(inp)[0]

        if not FLAGS.cclass:
            label = None

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        if FLAGS.swish_act:
            act = swish
        else:
            act = tf.nn.leaky_relu

        # Make sure gradients are modified a bit
        inp = smart_conv_block(
            inp, weights, reuse, "c1_pre", use_stride=False, activation=act
        )
        dropout = self.dropout
        train = self.train

        hidden1 = smart_res_block(
            inp,
            weights,
            reuse,
            "res_optim",
            adaptive=True,
            label=label,
            dropout=dropout,
            train=train,
        )

        if FLAGS.use_attention:
            hidden2 = smart_atten_block(
                hidden1,
                weights,
                reuse,
                "atten",
                train=train,
                dropout=dropout,
                stop_at_grad=stop_at_grad,
            )
        else:
            hidden2 = smart_res_block(
                hidden1,
                weights,
                reuse,
                "res_1",
                stop_batch=stop_batch,
                downsample=False,
                adaptive=False,
                label=label,
                dropout=dropout,
                train=train,
                act=act,
            )

        hidden3 = smart_res_block(
            hidden2,
            weights,
            reuse,
            "res_2",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )
        hidden4 = smart_res_block(
            hidden3,
            weights,
            reuse,
            "res_3",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )

        hidden5 = smart_res_block(
            hidden4,
            weights,
            reuse,
            "res_4",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )

        hidden6 = smart_res_block(
            hidden5,
            weights,
            reuse,
            "res_5",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )

        hidden7 = smart_res_block(
            hidden6,
            weights,
            reuse,
            "res_6",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )
        hidden8 = smart_res_block(
            hidden7,
            weights,
            reuse,
            "res_7",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )

        hidden9 = smart_res_block(
            hidden8,
            weights,
            reuse,
            "res_8",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )

        if FLAGS.swish_act:
            hidden6 = act(hidden9)
        else:
            hidden6 = tf.nn.relu(hidden9)

        hidden5 = tf.reduce_sum(hidden6, [1, 2])
        hidden6 = smart_fc_block(hidden5, weights, reuse, "fc5")
        energy = hidden6

        return energy


class ResNet32Larger(object):
    def __init__(self, num_channels=3, num_filters=128):

        self.channels = num_channels
        self.dim_hidden = num_filters

    def construct_weights(self, scope=""):
        weights = {}
        tf.float32

        if FLAGS.cclass:
            classes = 10
        else:
            classes = 1

        with tf.variable_scope(scope):
            # First block
            init_conv_weight(weights, "c1_pre", 3, self.channels, self.dim_hidden)
            init_res_weight(
                weights,
                "res_optim",
                3,
                self.dim_hidden,
                self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights, "res_1", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_2", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_2a", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights, "res_2b", 3, self.dim_hidden, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights,
                "res_3",
                3,
                self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_4",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5a",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5b",
                3,
                2 * self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_6",
                3,
                2 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_7",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_8",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_8a",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_8b",
                3,
                4 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(
                weights, "fc_dense", 4 * 4 * 2 * self.dim_hidden, 4 * self.dim_hidden
            )
            init_fc_weight(weights, "fc5", 4 * self.dim_hidden, 1, spec_norm=False)

            init_attention_weight(
                weights,
                "atten",
                2 * self.dim_hidden,
                self.dim_hidden / 2,
                trainable_gamma=True,
            )

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
    ):
        weights = weights.copy()
        tf.shape(inp)[0]

        if not FLAGS.cclass:
            label = None

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        # Make sure gradients are modified a bit
        inp = smart_conv_block(inp, weights, reuse, "c1_pre", use_stride=False)

        hidden1 = smart_res_block(
            inp, weights, reuse, "res_optim", adaptive=False, label=label
        )
        hidden2 = smart_res_block(
            hidden1,
            weights,
            reuse,
            "res_1",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
        )
        hidden3 = smart_res_block(
            hidden2,
            weights,
            reuse,
            "res_2",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
        )
        hidden3 = smart_res_block(
            hidden3,
            weights,
            reuse,
            "res_2a",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
        )
        hidden3 = smart_res_block(
            hidden3,
            weights,
            reuse,
            "res_2b",
            stop_batch=stop_batch,
            downsample=False,
            adaptive=False,
            label=label,
        )
        hidden4 = smart_res_block(
            hidden3, weights, reuse, "res_3", stop_batch=stop_batch, label=label
        )

        if FLAGS.use_attention:
            hidden5 = smart_atten_block(
                hidden4, weights, reuse, "atten", stop_at_grad=stop_at_grad
            )
        else:
            hidden5 = smart_res_block(
                hidden4,
                weights,
                reuse,
                "res_4",
                adaptive=False,
                downsample=False,
                stop_batch=stop_batch,
                label=label,
            )

        hidden6 = smart_res_block(
            hidden5,
            weights,
            reuse,
            "res_5",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )

        hidden6 = smart_res_block(
            hidden6,
            weights,
            reuse,
            "res_5a",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        hidden6 = smart_res_block(
            hidden6,
            weights,
            reuse,
            "res_5b",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        hidden7 = smart_res_block(
            hidden6, weights, reuse, "res_6", stop_batch=stop_batch, label=label
        )
        hidden8 = smart_res_block(
            hidden7,
            weights,
            reuse,
            "res_7",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        hidden9 = smart_res_block(
            hidden8,
            weights,
            reuse,
            "res_8",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        hidden9 = smart_res_block(
            hidden9,
            weights,
            reuse,
            "res_8a",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )
        compact = hidden9 = smart_res_block(
            hidden9,
            weights,
            reuse,
            "res_8b",
            adaptive=False,
            downsample=False,
            stop_batch=stop_batch,
            label=label,
        )

        if FLAGS.cclass:
            hidden6 = tf.nn.leaky_relu(hidden9)
        else:
            hidden6 = tf.nn.relu(hidden9)
        hidden5 = tf.reduce_sum(hidden6, [1, 2])

        hidden6 = smart_fc_block(hidden5, weights, reuse, "fc5")

        energy = hidden6

        return energy


class ResNet128(object):
    """Construct the convolutional network specified in MAML"""

    def __init__(self, num_channels=3, num_filters=64, train=False):

        self.channels = num_channels
        self.dim_hidden = num_filters
        self.dropout = train
        self.train = train

    def construct_weights(self, scope=""):
        weights = {}
        tf.float32

        classes = 1000

        with tf.variable_scope(scope):
            # First block
            init_conv_weight(weights, "c1_pre", 3, self.channels, 64)
            init_res_weight(
                weights, "res_optim", 3, 64, self.dim_hidden, classes=classes
            )
            init_res_weight(
                weights,
                "res_3",
                3,
                self.dim_hidden,
                2 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_5",
                3,
                2 * self.dim_hidden,
                4 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_7",
                3,
                4 * self.dim_hidden,
                8 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_9",
                3,
                8 * self.dim_hidden,
                8 * self.dim_hidden,
                classes=classes,
            )
            init_res_weight(
                weights,
                "res_10",
                3,
                8 * self.dim_hidden,
                8 * self.dim_hidden,
                classes=classes,
            )
            init_fc_weight(weights, "fc5", 8 * self.dim_hidden, 1, spec_norm=False)

            init_attention_weight(
                weights,
                "atten",
                self.dim_hidden,
                self.dim_hidden / 2.0,
                trainable_gamma=True,
            )

        return weights

    def forward(
        self,
        inp,
        weights,
        reuse=False,
        scope="",
        stop_grad=False,
        label=None,
        stop_at_grad=False,
        stop_batch=False,
    ):
        weights = weights.copy()
        tf.shape(inp)[0]

        if not FLAGS.cclass:
            label = None

        if stop_grad:
            for k, v in weights.items():
                if isinstance(v, dict):
                    v = v.copy()
                    weights[k] = v
                    for k_sub, v_sub in v.items():
                        v[k_sub] = tf.stop_gradient(v_sub)
                else:
                    weights[k] = tf.stop_gradient(v)

        if FLAGS.swish_act:
            act = swish
        else:
            act = tf.nn.leaky_relu

        dropout = self.dropout
        train = self.train

        # Make sure gradients are modified a bit
        inp = smart_conv_block(
            inp, weights, reuse, "c1_pre", use_stride=False, activation=act
        )
        hidden1 = smart_res_block(
            inp,
            weights,
            reuse,
            "res_optim",
            label=label,
            dropout=dropout,
            train=train,
            downsample=True,
            adaptive=False,
        )

        if FLAGS.use_attention:
            hidden1 = smart_atten_block(
                hidden1, weights, reuse, "atten", stop_at_grad=stop_at_grad
            )

        hidden2 = smart_res_block(
            hidden1,
            weights,
            reuse,
            "res_3",
            stop_batch=stop_batch,
            downsample=True,
            adaptive=True,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )
        hidden3 = smart_res_block(
            hidden2,
            weights,
            reuse,
            "res_5",
            stop_batch=stop_batch,
            downsample=True,
            adaptive=True,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
        )
        hidden4 = smart_res_block(
            hidden3,
            weights,
            reuse,
            "res_7",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
            downsample=True,
            adaptive=True,
        )
        hidden5 = smart_res_block(
            hidden4,
            weights,
            reuse,
            "res_9",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
            downsample=True,
            adaptive=False,
        )
        hidden6 = smart_res_block(
            hidden5,
            weights,
            reuse,
            "res_10",
            stop_batch=stop_batch,
            label=label,
            dropout=dropout,
            train=train,
            act=act,
            downsample=False,
            adaptive=False,
        )

        if FLAGS.swish_act:
            hidden6 = act(hidden6)
        else:
            hidden6 = tf.nn.relu(hidden6)

        hidden5 = tf.reduce_sum(hidden6, [1, 2])
        hidden6 = smart_fc_block(hidden5, weights, reuse, "fc5")
        energy = hidden6

        return energy
