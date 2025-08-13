## quantum ai: training energy-based-models using openAI

<br>


#### ⚛️ this repository contains my adapted code from [opeani's implicit generation and generalization in
energy-based-models](https://arxiv.org/pdf/1903.08689.pdf)

<br>

---

### installing

<br>

```bash
brew install gcc@6
brew install open-mpi
brew install pkg-config
```

<br>

* there is a **[bug](https://github.com/open-mpi/ompi/issues/7516)** in open-mpi for the specific libraries in this
problem (`PMIX ERROR: ERROR`) that can be fixed with:

<br>

```
export PMIX_MCA_gds=^ds12
```

<br>

* then install python's requirements:

<br>

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
<br>

* note that this is an adapted requirement file since the **[openai's
original](https://github.com/openai/ebm_code_release/blob/master/requirements.txt)** is not complete/correct
* finally, download and install **[mujoco](https://www.roboti.us/index.html)**
* you will also need to register for a license, which asks for a machine ID
* the documentation on the website is incomplete, so just download the suggested script and run:

<br>

```bash
mv getid_osx getid_osx.dms
./getid_osx.dms
```

<br>

---

### running

<br>

#### download pre-trained models (examples)

<br>

* download all **[pre-trained models](https://sites.google.com/view/igebm/home)** and unzip them into a local folder
`cachedir`:

<br>

```bash
mkdir cachedir
```

<br>

#### setting results directory

<br>

* openai's original code contains **[hardcoded constants that only work on
Linux](https://github.com/openai/ebm_code_release/blob/master/data.py#L218)**
* i changed this to a constant (`ROOT_DIR = "./results"`) in the top of `data.py`

<br>

#### running (parallelization with `mpiexec`)

<br>

* all code supports **[`horovod` execution](https://github.com/horovod/horovod)**, so model training can be increased
substantially by using multiple different workers by running each command:

<br>

```
mpiexec -n <worker_num>  <command>
```

<br>

##### cifar-10 unconditional

<br>

```
python train.py --exp=cifar10_uncond --dataset=cifar10 --num_steps=60 --batch_size=128 --step_lr=10.0 --proj_norm=0.01
--zero_kl --replay_batch --large_model
```

* this should generate the following output:

<br>

```bash
Instructions for updating:
Use tf.gfile.GFile.
2020-05-10 22:12:32.471415: W tensorflow/core/framework/op_def_util.cc:355] Op BatchNormWithGlobalNormalization is
deprecated. It will cease to work in GraphDef version 9. Use tf.nn.batch_normalization().
64 batch size
Local rank:  0 1
Loading data...
Files already downloaded and verified
Files already downloaded and verified
Files already downloaded and verified
Files already downloaded and verified
Done loading...
WARNING:tensorflow:From
/Users/mia/dev/ebm_code_release/venv/lib/python3.7/site-packages/tensorflow/python/framework/op_def_library.py:263:
colocate_with (from tensorflow.python.framework.ops) is deprecated and will be removed in a future version.
Instructions for updating:
Colocations handled automatically by placer.
Building graph...
WARNING:tensorflow:From
/Users/mia/dev/ebm_code_release/venv/lib/python3.7/site-packages/tensorflow/python/ops/math_ops.py:3066: to_int32 (from
tensorflow.python.ops.math_ops) is deprecated and will be removed in a future version.
Instructions for updating:
Use tf.cast instead.
Finished processing loop construction ...
Started gradient computation...
Applying gradients...
Finished applying gradients.
Model has a total of 7567880 parameters
Initializing variables...
Start broadcast
End broadcast
Obtained a total of e_pos: -0.0025530937127768993, e_pos_std: 0.09564747661352158, e_neg: -0.22276005148887634, e_diff:
0.22020696103572845, e_neg_std: 0.016306934878230095, temp: 1, loss_e: -0.22276005148887634, eps: 0.0, label_ent:
2.272536277770996, l
oss_ml: 0.22020693123340607, loss_total: 0.2792498469352722, x_grad: 0.0009156676824204624, x_grad_first:
0.0009156676824204624, x_off: 0.31731340289115906, iter: 0, gamma: [0.], context_0/c1_pre/cweight:0: 0.0731438547372818,
context_0/res_optim_res_c1/
cweight:0: 4.732660444095593e-11, context_0/res_optim_res_c1/gb:0: 3.4007335836250263e-10,
context_0/res_optim_res_c2/cweight:0: 0.9494612216949463, context_0/res_optim_res_c2/g:0: 1.8536269741353806e-10,
context_0/res_optim_res_c2/gb:0: 6.27235652306268
3e-10, context_0/res_optim_res_c2/cb:0: 1.1606662297936055e-09, context_0/res_1_res_c1/cweight:0: 6.714453298917178e-11,
context_0/res_1_res_c1/gb:0: 3.6198691266697836e-10, context_0/res_1_res_c2/cweight:0: 0.6582950353622437,
context_0/res_1_res_c2/g:0
: 1.669797633496728e-10, context_0/res_1_res_c2/gb:0: 5.911696687732615e-10, context_0/res_1_res_c2/cb:0:
1.1932842491901852e-09, context_0/res_2_res_c1/cweight:0: 8.567072745657711e-11, context_0/res_2_res_c1/gb:0:
6.868505764145993e-10, context_0/res_2
_res_c2/cweight:0: 0.46929678320884705, context_0/res_2_res_c2/g:0: 1.655784120924153e-10, context_0/res_2_res_c2/gb:0:
8.058526068666083e-10, context_0/res_2_res_c2/cb:0: 1.0161046448686761e-09, context_0/res_2_res_adaptive/cweight:0:
0.0194275379180908
2, context_0/res_3_res_c1/cweight:0: 4.011655244107182e-11, context_0/res_3_res_c1/gb:0: 5.064903496609929e-10,
context_0/res_3_res_c2/cweight:0: 0.32239994406700134, context_0/res_3_res_c2/g:0: 9.758494012857e-11,
context_0/res_3_res_c2/gb:0: 7.75612463
1441708e-10, context_0/res_3_res_c2/cb:0: 6.362700366580043e-10, context_0/res_4_res_c1/cweight:0:
4.090133440270982e-11, context_0/res_4_res_c1/gb:0: 6.013010089844784e-10, context_0/res_4_res_c2/cweight:0:
0.34806951880455017, context_0/res_4_res_c2/g:
0: 8.414659247168998e-11, context_0/res_4_res_c2/gb:0: 6.443054978433338e-10, context_0/res_4_res_c2/cb:0:
5.496815780325903e-10, context_0/res_5_res_c1/cweight:0: 3.990113794927197e-11, context_0/res_5_res_c1/gb:0:
3.807749116013781e-10, context_0/res_5
_res_c2/cweight:0: 0.22841960191726685, context_0/res_5_res_c2/g:0: 4.942361797599659e-11, context_0/res_5_res_c2/gb:0:
7.697342763179904e-10, context_0/res_5_res_c2/cb:0: 3.1796060229183354e-10, context_0/fc5/wweight:0: 3.081033706665039,
context_0/fc5/
b:0: 0.4506262540817261,

................................................................................................................................
Inception score of 1.2397289276123047 with std of 0.0
```

<br>

##### cifar-10 conditional

<br>

```
python train.py --exp=cifar10_cond --dataset=cifar10 --num_steps=60 --batch_size=128 --step_lr=10.0 --proj_norm=0.01
--zero_kl --replay_batch --cclass
```

<br>

##### imagenet 32x32 conditional

<br>

```
python train.py --exp=imagenet_cond --num_steps=60 --wider_model --batch_size=32 step_lr=10.0 --proj_norm=0.01
--replay_batch --cclass --zero_kl --dataset=imagenet --imagenet_path=<imagenet32x32 path>
```

<br>

##### imagenet 128x128 conditional

<br>

```
python train.py --exp=imagenet_cond --num_steps=50 --batch_size=16 step_lr=100.0 --replay_batch --swish_act --cclass
--zero_kl --dataset=imagenetfull --imagenet_datadir=<full imagenet path>
```

<br>

##### imagenet demo

<br>

* the imagenet_demo.py file contains code for experiments with ebms on conditional imagenet 128x128
* to generate a gif on sampling, you can run the command:

<br>

```
python imagenet_demo.py --exp=imagenet128_cond --resume_iter=2238000 --swish_act
```

* the ebm_sandbox.py file contains several different tasks that can be used to evaluate ebms, which are defined by
different settings of task flag in the file
* for example, to visualize cross class mappings in cifar-10, you can run:

<br>

```
python ebm_sandbox.py --task=crossclass --num_steps=40 --exp=cifar10_cond --resume_iter=74700
```

<br>

##### generalization

<br>

* to test generalization to out of distribution classification for SVHN (with similar commands for other datasets):

<br>

```
python ebm_sandbox.py --task=mixenergy --num_steps=40 --exp=cifar10_large_model_uncond --resume_iter=121200
--large_model --svhnmix --cclass=False
```

<br>

* to test classification on cifar-10 using a conditional model under either L2 or Li perturbations

<br>

```
python ebm_sandbox.py --task=label --exp=cifar10_wider_model_cond --resume_iter=21600 --lnorm=-1 --pgd=<number of pgd
steps> --num_steps=10 --lival=<li bound value> --wider_model
```

<br>

##### concept combination

<br>

* to train ebms on conditional dsprites dataset, you can train each model separately on each conditioned latent in
`cond_pos`, `cond_rot`, `cond_shape`, `cond_scale`, with an example command given below:

<br>

```
python train.py --dataset=dsprites --exp=dsprites_cond_pos --zero_kl --num_steps=20 --step_lr=500.0 --swish_act
--cond_pos --replay_batch -cclass
```

<br>

* once models are trained, they can be sampled from jointly by running:

```
python ebm_combine.py --task=conceptcombine --exp_size=<exp_size> --exp_shape=<exp_shape> --exp_pos=<exp_pos>
--exp_rot=<exp_rot> --resume_size=<resume_size> --resume_shape=<resume_shape> --resume_rot=<resume_rot>
--resume_pos=<resume_pos>
```
