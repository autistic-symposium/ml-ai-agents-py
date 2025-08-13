import os.path as osp

import imageio
import numpy as np
import tensorflow as tf
from models import ResNet128
from tensorflow.python.platform import flags

flags.DEFINE_string(
    "logdir", "cachedir", "location where log of experiments will be stored"
)
flags.DEFINE_integer("num_steps", 200, "num of steps for conditional imagenet sampling")
flags.DEFINE_float("step_lr", 180.0, "step size for Langevin dynamics")
flags.DEFINE_integer("batch_size", 16, "number of steps to run")
flags.DEFINE_string("exp", "default", "name of experiments")
flags.DEFINE_integer("resume_iter", -1, "iteration to resume training from")
flags.DEFINE_bool(
    "spec_norm", True, "whether to use spectral normalization in weights in a model"
)
flags.DEFINE_bool("cclass", True, "conditional models")
flags.DEFINE_bool("use_attention", False, "using attention")

FLAGS = flags.FLAGS


def rescale_im(im):
    return np.clip(im * 256, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    model = ResNet128(num_filters=64)
    X_NOISE = tf.placeholder(shape=(None, 128, 128, 3), dtype=tf.float32)
    LABEL = tf.placeholder(shape=(None, 1000), dtype=tf.float32)

    sess = tf.InteractiveSession()
    weights = model.construct_weights("context_0")

    x_mod = X_NOISE
    x_mod = x_mod + tf.random_normal(tf.shape(x_mod), mean=0.0, stddev=0.005)

    energy_noise = energy_start = model.forward(
        x_mod, weights, label=LABEL, reuse=True, stop_at_grad=False, stop_batch=True
    )

    x_grad = tf.gradients(energy_noise, [x_mod])[0]
    energy_noise_old = energy_noise

    lr = FLAGS.step_lr

    x_last = x_mod - (lr) * x_grad

    x_mod = x_last
    x_mod = tf.clip_by_value(x_mod, 0, 1)
    x_output = x_mod

    sess.run(tf.global_variables_initializer())
    saver = loader = tf.train.Saver()

    logdir = osp.join(FLAGS.logdir, FLAGS.exp)
    model_file = osp.join(logdir, "model_{}".format(FLAGS.resume_iter))
    saver.restore(sess, model_file)

    lx = np.random.permutation(1000)[:16]
    ims = []

    # What to initialize sampling with.
    x_mod = np.random.uniform(0, 1, size=(FLAGS.batch_size, 128, 128, 3))
    labels = np.eye(1000)[lx]

    for i in range(FLAGS.num_steps):
        e, x_mod = sess.run([energy_noise, x_output], {X_NOISE: x_mod, LABEL: labels})
        ims.append(
            rescale_im(x_mod)
            .reshape((4, 4, 128, 128, 3))
            .transpose((0, 2, 1, 3, 4))
            .reshape((512, 512, 3))
        )

    imageio.mimwrite("sample.gif", ims)
